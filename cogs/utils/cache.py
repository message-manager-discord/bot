# cogs/utils/cache.py
"""
Message Manager - A bot for discord
Copyright (C) 2020-2021 AnotherCat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This file incorporates work covered by the following copyright and permission notice:
    Repository: https://github.com/luxigner/lfu_cache

    Copyright (c) 2018 Shane Wang

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""


from __future__ import annotations

from typing import Any, Dict, Hashable, Optional, Union

from cogs.utils import errors
from cogs.utils.db.db import DatabasePool, GuildTuple


class CacheNode:
    def __init__(
        self,
        key: Hashable,
        value: Any,
        freq_node: Optional[FreqNode],
        pre: Optional[CacheNode],
        next: Optional[CacheNode],
    ) -> None:
        self.key = key
        self.value = value
        self.freq_node = freq_node
        self.pre = pre  # previous CacheNode
        self.next = next  # next CacheNode

    def free_myself(self) -> None:
        if self.freq_node is None:
            raise errors.CacheError("CacheNode outside of a FreqNode")
        if self.freq_node.cache_head == self.freq_node.cache_tail:
            self.freq_node.cache_head = self.freq_node.cache_tail = None
        elif self.freq_node.cache_head == self:
            assert self.next is not None
            self.next.pre = None
            self.freq_node.cache_head = self.next
        elif self.freq_node.cache_tail == self:
            assert self.pre is not None
            self.pre.next = None
            self.freq_node.cache_tail = self.pre
        else:
            assert self.next is not None and self.pre is not None
            self.pre.next = self.next
            self.next.pre = self.pre

        self.pre = None
        self.next = None
        self.freq_node = None


class FreqNode:
    def __init__(
        self, freq: int, pre: Optional[FreqNode], next: Optional[FreqNode]
    ) -> None:
        self.freq = freq
        self.pre = pre  # previous FreqNode
        self.next = next  # next FreqNode
        self.cache_head: Optional[
            CacheNode
        ] = None  # CacheNode head under this FreqNode
        self.cache_tail: Optional[
            CacheNode
        ] = None  # CacheNode tail under this FreqNNode

    def count_caches(self) -> Union[int, str]:
        if self.cache_head is None and self.cache_tail is None:
            return 0
        elif self.cache_head == self.cache_tail:
            return 1
        else:

            return "2+"

    def is_zero_length(self) -> bool:
        return self.cache_head is None and self.cache_tail is None

    def remove(self) -> None:
        if self.pre is not None:
            self.pre.next = self.next
        if self.next is not None:
            self.next.pre = self.pre

        self.pre = self.next = self.cache_head = self.cache_tail = None

    def pop_head_cache(self) -> Optional[CacheNode]:
        if self.cache_head is None and self.cache_tail is None:
            return None
        elif self.cache_head == self.cache_tail:
            cache_head = self.cache_head
            self.cache_head = self.cache_tail = None
            return cache_head
        else:
            assert self.cache_head is not None
            assert self.cache_head.next is not None
            cache_head = self.cache_head
            self.cache_head.next.pre = None
            self.cache_head = self.cache_head.next
            return cache_head

    def append_cache_to_tail(self, cache_node: CacheNode) -> None:
        cache_node.freq_node = self

        if self.cache_head is None and self.cache_tail is None:
            self.cache_head = self.cache_tail = cache_node
        else:
            assert self.cache_tail is not None
            cache_node.pre = self.cache_tail
            cache_node.next = None
            self.cache_tail.next = cache_node
            self.cache_tail = cache_node

    def insert_after_me(self, freq_node: FreqNode) -> None:
        freq_node.pre = self
        freq_node.next = self.next

        if self.next is not None:
            self.next.pre = freq_node

        self.next = freq_node

    def insert_before_me(self, freq_node: FreqNode) -> None:
        if self.pre is not None:
            self.pre.next = freq_node

        freq_node.pre = self.pre
        freq_node.next = self
        self.pre = freq_node


class BaseLFUCache:
    def __init__(self, capacity: int, db: DatabasePool, drop_amount: int) -> None:
        self.cache: Dict[Hashable, CacheNode] = {}  # {key: cache_node}
        self.capacity = capacity
        self.freq_link_head: Optional[FreqNode] = None
        self.db = db
        self.drop_amount = drop_amount
        if drop_amount > capacity:
            pass
            # raise

    async def get(self, key: Hashable) -> Any:
        if key in self.cache:
            cache_node = self.cache[key]
            freq_node = cache_node.freq_node
            if freq_node is None:
                raise errors.CacheError("CacheNode outside of a FreqNode")
            value = cache_node.value

            self.move_forward(cache_node, freq_node)

            return value
        else:
            new_data = await self.fetch(key)
            self.set(key, new_data)
            return await self.get(key)  # To increment freq once

    async def fetch(self, key: Hashable) -> Any:
        # for use when the key is not in the cache, empty to allow for different data types
        return None

    def set(self, key: Hashable, value: Any) -> None:
        if key not in self.cache:
            if len(self.cache) >= self.capacity:
                self.dump_cache()

            self.create_cache(key, value)
        else:
            cache_node = self.cache[key]
            freq_node = cache_node.freq_node
            if freq_node is None:
                raise errors.CacheError("CacheNode outside of a FreqNode")
            cache_node.value = value

            self.move_forward(cache_node, freq_node)

    def move_forward(self, cache_node: CacheNode, freq_node: FreqNode) -> None:
        if freq_node.next is None or freq_node.next.freq != freq_node.freq + 1:
            target_freq_node = FreqNode(freq_node.freq + 1, None, None)
            target_empty = True
        else:
            target_freq_node = freq_node.next
            target_empty = False
        cache_node.free_myself()
        target_freq_node.append_cache_to_tail(cache_node)

        if target_empty:
            freq_node.insert_after_me(target_freq_node)

        if freq_node.is_zero_length():
            if self.freq_link_head == freq_node:
                self.freq_link_head = target_freq_node

            freq_node.remove()

    def dump_cache(self) -> None:
        head_freq_node = self.freq_link_head

        for cache in range(self.drop_amount):
            if head_freq_node is None:
                return  # Cache empty
            if head_freq_node.cache_head is None:
                self.freq_link_head = head_freq_node.next
                head_freq_node.remove()
                head_freq_node = self.freq_link_head
            else:
                self.cache.pop(head_freq_node.cache_head.key)
                head_freq_node.pop_head_cache()
                if head_freq_node.is_zero_length():
                    self.freq_link_head = head_freq_node.next
                    head_freq_node.remove()
                    head_freq_node = self.freq_link_head

    def create_cache(self, key: Hashable, value: Any) -> None:
        cache_node = CacheNode(key, value, None, None, None)
        self.cache[key] = cache_node

        if self.freq_link_head is None or self.freq_link_head.freq != 0:
            new_freq_node = FreqNode(0, None, None)
            new_freq_node.append_cache_to_tail(cache_node)

            if self.freq_link_head is not None:
                self.freq_link_head.insert_before_me(new_freq_node)

            self.freq_link_head = new_freq_node
        else:
            self.freq_link_head.append_cache_to_tail(cache_node)


class PartialGuildCache(BaseLFUCache):
    async def get(self, key: int) -> GuildTuple:  # type: ignore[override]
        data = await super().get(key)
        assert isinstance(data, GuildTuple)
        # Fetch was also overridden, therefore all values will be of type GuildTuple
        return data

    async def fetch(self, key: int) -> GuildTuple:  # type: ignore[override]
        return await self.db.get_guild(key)

    async def update_prefix(self, guild_id: int, prefix: str) -> GuildTuple:
        before = await self.get(guild_id)
        new = GuildTuple(
            id=before.id, management_role=before.management_role, prefix=prefix
        )
        await self.db.update_prefix(guild_id, prefix)
        self.set(guild_id, new)
        return new

    async def update_management_role(
        self, guild_id: int, management_role: Optional[int]
    ) -> GuildTuple:
        before = await self.get(guild_id)
        new = GuildTuple(
            id=before.id, management_role=management_role, prefix=before.prefix
        )
        await self.db.update_admin_role(guild_id, management_role)
        self.set(guild_id, new)
        return new
