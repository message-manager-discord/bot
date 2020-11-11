# web/app.py
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

from quart import Quart

from .config import secret_key
from .error_handlers import blueprint as error_handlers
from .index import blueprint as index_blueprint


def create_app():
    app = Quart(__name__)
    app.secret_key = secret_key
    app.register_blueprint(index_blueprint)
    app.register_blueprint(error_handlers)
    return app


if __name__ == "__main__":
    create_app().run()
