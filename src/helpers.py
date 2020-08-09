# helpers.py
from discord import Embed
import discord
import asyncio

# Creating the create embed function. This fuction takes a title, colour and a list of values. 
# It returns a discord Embed type.
def create_embed(title_value, colour_value, values):
    new_embed = Embed(title=title_value, colour = colour_value)
    for a in values:
        new_embed.add_field(name=a[0],value=a[1],inline=a[2])
    return new_embed

# Create the function get message. This function returns the discord message type.
async def get_message(bot, channel_id, message_id):
    channel = bot.get_channel(int(channel_id))
     
    msg = await channel.fetch_message(int(message_id))
    return msg

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
        list_content[0][0] = "Editor"
    elif command_type == 'delete':
        title = 'Deleted'
        list_content[0][0] = "Deleter"

    embed = create_embed(
        f"{title} the message!",
        discord.Colour(0xc387c1),
        list_content
    )
    return embed



async def check_channel_id(ctx, channel_id, bot):
    def is_correct(m):
        return m.author == ctx.author
    if channel_id == None:
        message = await ctx.send(
            embed = create_embed(
                "What is the id of the channel that the message is in?",
                discord.Color.blue(),
                []
            )
        )
        try: 
            get_channel_id = await bot.wait_for('message', check=is_correct, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send('Timedout, Please re-do the command.')

        channel_id = int(get_channel_id.content)
        await message.delete()
        await get_channel_id.delete()    
        return channel_id
    else:
        return channel_id

async def check_message_id(ctx, message_id, bot):
    def is_correct(m):
        return m.author == ctx.author
    if message_id == None:
        message = await ctx.send(
            embed = create_embed(
                "What is the id of the message?",
                discord.Color.blue(),
                []
            )
        )
        try: 
            get_message_id = await bot.wait_for('message', check=is_correct, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send('Timedout, Please re-do the command.')

        message_id = int(get_message_id.content)
        await message.delete()
        await get_message_id.delete()    
        return message_id
    else:
        return message_id

if __name__ == "__main__":
    print("Im afraid you ran the wrong file, please run main.py instead.")