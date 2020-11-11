import discord

from quart import Blueprint, current_app, redirect, render_template, url_for

blueprint = Blueprint("error_handlers", __name__)


@blueprint.app_errorhandler(404)
async def handle404(e):
    return await render_template(
        "error.html", title="404 - ", error_code=404, error="That page does not exist!"
    )
