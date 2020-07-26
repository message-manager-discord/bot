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
~$ source bot-env/bin/activate # Activate the python virtual enviroment (will need to do this every time)
(bot-env) ~$ cd custom_helper_bot # Navigate to the main dir for the project.
(bot-env) ~/custom_helper_bot$ pip install -r requirments.txt # Install the required python packeges.
# Now you need to setup the enviromental variables, see Config below
(bot-env) ~/custom_helper_bot$ python3 main.py # Run the bot
```

Note: This assumes that you have the following packages installed: The latest version of python with pip and venv installed. The latest version of git.
Some commands may require sudo privileges depending on your system.

For windows do the same, but replace `python3` with python and replace `source bot-env/bin/activate` with `/bot-env/scripts/activate.bat`

## Config

1. Create a python environment
2. Install the required packages with `pip install -r requirments.txt`
3. This bot uses [dotenv](https://pypi.org/project/python-dotenv/) for environment variables. 
4. Rename `.example_env` to `.env`
5. At `DISCORD_TOKEN=bot_token` replace bot_token with the bot's token. 

### Config Values
| Field           | Value           | Description                                                  |
| --------------- | ------------------- | ------------------------------------------------------------ |
| DISCORD_TOKEN   | String          | This is the discord bot token.                               |
| OWNER_ID        | User ID (INT)   | This will appear in the info box from the `!info` command. Leave as `None` if you don't want this to appear. |
| SERVER_ID       | Server ID (INT) | If set the bot will only respond to commands in this server. Leave as `None` to make the bot respond regardless of server.|
| MANAGEMENT_ROLE | Role ID (INT)   | Setting this means that only users with this role can use the bot. Leave it as `None` if you don't want this. **Not Advised** |
| PREFIX          | String          | This is the prefix before commands. Default is `!`.          |
