# helpers.py
from discord import Embed
def create_embed(title_value, colour_value, values):
    new_embed = Embed(title=title_value, colour = colour_value)
    for a in values:
        new_embed.add_field(name=a[0],value=a[1],inline=a[2])
    return new_embed

