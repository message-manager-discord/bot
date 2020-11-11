# web/index.py
"""
Message Manager - A bot for discord
Copyright (C) 2020  AnotherCat

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
"""

from quart import Blueprint, redirect, render_template

blueprint = Blueprint("index", __name__)


@blueprint.route("/")
async def index():
    return await render_template("index.html", title="Home - ")


@blueprint.route("/invite")
async def invite():
    return redirect(
        "https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=388176&scope=bot"
    )


@blueprint.route("/docs")
async def docs():
    return redirect("https://docs.messagemanager.xyz")
