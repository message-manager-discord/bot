# Custom Helper Bot

## General Info

This is a general custom made bot.

Features are:

1. Sending messages in channels and being able to edit them with commands. (pending)
2. Sending announcements. (pending)



## Installation 

1. Clone this repo
2. Make sure you have the latest version of python
3. Creating a discord application and a bot user at the [discord dev website](https://discord.com/developers/applications), setup guide [here](https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account)
4. [Setting up config](#config)
5. Running `main.py` 
6. Inviting the bot to your server, there will be an invite link in the python shell after you run it. 

### Setup Example (linux)

```bash
~$ python3 #check if python is installed.
~$ git clone https://github.com/AnotherCat/custom_helper_bot.git # Clone this github repo
~$ python3 -m venv bot-env # Create the python virtual enviroment bot-env
~$ source bot-env/bin/activate # Activate the python virtual enviroment (will need to do this every time you want to be able to run the bot)
(bot-env) ~$ cd custom_helper_bot # Navigate to the main directory for the project.
(bot-env) ~/custom_helper_bot$ pip install -r requirments.txt # Install the required python packeges.
# Now you need to setup the enviromental variables, see Config below
(bot-env) ~/custom_helper_bot$ python3 main.py # Run the bot
```

Note: This assumes that you have the following packages installed: 

- The latest version of python with pip and venv installed. 
- The latest version of git.

Some commands may require sudo privileges depending on your system.

For windows do the same, but replace `python3` with python and replace `source bot-env/bin/activate` with `/bot-env/scripts/activate.bat`

## Config

This bot uses [dotenv](https://pypi.org/project/python-dotenv/) for environment variables. 

### Setting this up:

4. Rename `.example_env` to `.env`
5. Set the values as per the table below

#### Config Values
| Field           | Value           | Description                                                  | Required |
| :-------------- | :------------------ | :----------------------------------------------------------- | --------------- |
| DISCORD_TOKEN   | String          | This is the discord bot token.                               | Yes |
| OWNER_ID        | User ID (INT)   | This will appear in the info box from the `!info` command. Leave as `None` if you don't want this to appear. | No |
| SERVER_ID       | Server ID (INT) | If set the bot will only respond to commands in this server. Leave as `None` to make the bot respond regardless of server.| No |
| MANAGEMENT_ROLE | Role ID (INT)   | Setting this means that only users with this role can use the bot. Leave it as `None` if you don't want this. **Not Advised** as this will allow `@everyone` to use it. | No |
| PREFIX          | String          | This is the prefix before commands. Default is `!`.          | Yes |

## Commands

| Command                                   | Description                                                  | Who can use it                        |
| ----------------------------------------- | ------------------------------------------------------------ | ------------------------------------- |
| `!help`                                   | Displays the help embed                                      | `@everyone`                           |
| `!info`                                   | Displays info about the bot                                  | `@everyone`                           |
| `!ping`                                   | Returns the bot-side latency                                 | `@everyone`                           |
| `!send channel_id message_content`        | Sends a message to a channel. The channel is the channel which channel_id points to. | Requires the management role (if set) |
| `!edit channel_id message_id new_content` | Edits the message that can be found in the channel which channel_id points to. The message **must** be from the bot. | Requires the management role (if set) |
| `!delete channel_id message_id`           | Deletes the message. The message **must** be from the bot.   | Requires the management role (if set) |

