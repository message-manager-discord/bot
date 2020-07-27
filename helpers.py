# helpers.py
from discord import Embed

# Creating the create embed function. This fuction takes a title, colour and a list of values. 
# It returns a discord Embed type.
def create_embed(title_value, colour_value, values):
    new_embed = Embed(title=title_value, colour = colour_value)
    for a in values:
        new_embed.add_field(name=a[0],value=a[1],inline=a[2])
    return new_embed

# Create the function get message. This function returns the discord message type.
async def get_message(channel_id, message_id):
    channel = bot.get_channel(int(channel_id))
    return await channel.fetch_message(int(message_id))

# Create the function that create an embed for the message commands.
def create_message_info_embed(command_type, author, content, message):
    title = 'Sent'
    list_content = [

        ["Author", author.mention, True],
        ["Channel", message.channel.mention, True],  
        ["Content", content, False]
    ]
    if command_type == 'edit':
        title = "Edited"
        list_content.insert(2, ["Original Content",message.content,False])
        list_content[3][0] = 'New Content'
    elif command_type == 'delete':
        title = 'Deleted'

    embed = create_embed(
        f"{title} the message!",
        discord.Colour(0xc387c1),
        list_content
    )
    return embed
    