# Custom Helper Bot

If you find a bug or if you want to make a feature request, either join the [discord server](https://discord.gg/xFZu29t) or open an issue.  
If you want to contrubite to the docs or the code of the bot feel free to open a pull request.

## Invite link

[Click here to invite the bot](https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=388176&scope=bot)

## To Do

- Add support for the shift click message ids `(<channelid>-<messageid>)`

## Docs

Offical docs are [here](https://anothercat1259.gitbook.io/message-bot/). Read them before asking questions please :smile:

## Installation

1. Clone this repo
2. Make sure you have the latest version of python and postgresql
3. Setting up the database and roles
4. Creating a discord application and a bot user at the [discord dev website](https://discord.com/developers/applications), setup guide [here](https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account)
5. You **MUST** enable member intents on the bot page for the bot to load.
6. [Setting up config](#config)
7. Running `main.py`
8. Inviting the bot to your server, there will be an invite link in the python shell after you run it.

### Setup Example (linux)

```bash
~$ python3 #check if python is installed.
~$ git clone https://github.com/AnotherCat/custom_helper_bot.git # Clone this github repo
~$ python3 -m venv bot-env # Create the python virtual enviroment bot-env
~$ source bot-env/bin/activate # Activate the python virtual enviroment (will need to do this every time you want to be able to run the bot)
(bot-env) ~$ cd custom_helper_bot # Navigate to the main directory for the project.
(bot-env) ~/custom_helper_bot$ pip install -r requirments.txt # Install the required python packages.
# Now you need to setup the config variables, see Config below
(bot-env) ~/custom_helper_bot$ python3 main.py # Run the bot
```

Note: This assumes that you have the following packages installed:

- The latest version of python with pip and venv installed.
- The latest version of git.
- The latest version of postgresql

Some commands may require sudo privileges depending on your system.

For windows do the same, but replace `python3` with python and replace `source bot-env/bin/activate` with `/bot-env/scripts/activate.bat`

## Config

This bot uses a `config.py` file to store config.

### Setting up PostgreSQL

1. Install PostgreSQL
2. Create a role for the bot to use
3. Create the bot's database

```bash
$sudo -u postgres psql
postgres=# CREATE ROLE bot LOGIN PASSWORD 'password' SUPERUSER; # Create the role for the bot to use. You can do it without superuser, look up the docs to see what's needed.
postgres=# CREATE DATABASE bot OWNER bot; # Create a database with the same name as the role, so that you can login easier
postgres=# CREATE DATABASE message_bot OWNER bot; # Create the database the bot will use
postgres=# \q
```

Then enter the values into the postgres_uri config.

### Setting this up

1. Rename `config_example.py` to `config.py`
2. Set the values as per the table below

#### Config Values

| Field         | Type     | Value                                             | Description                                                  | Required | Default |
| :-------------- | :------------------ | :----------------------------------------------------------- | --------------- | :-------------- | --------------- |
| token | string         | Discord Bot Token  | This is the discord bot token.                               | Yes | `""` |
| default_prefix    | string         | String    | This is the default prefix before commands. If a server prefix this will be overidden. | Yes | `"!"` |
| owner   | string | User ID | This will appear in the info box from the `!info` command. Leave as `None` if you don't want this to appear. | No | `None` |
| bypassed_users | int[] | User ids in an array | By adding a user to this this will bypass all user checks. This is useful for if you have set allowed_server, but want some users to still be able to use it. **Dangerous** permission to grant. | No | `[]` |
| uri | string | postgres uri | This gives the bot access to the database. You'll need to setup a postgres user and database. | Yes | see config file |

## Important Notes

### Updates

I will be using the standard version naming.

If the first number in the tuple is the same, it will not break if you leave config the same. In this case all you have to do it pull the repo as `config.json` is the only file that is user specific and there is no file named that in the repo.
It is still suggested that you read the update notes and update your config as said, but if you don't nothing will break.

If the first number in the tuple changes, this means that it is no longer backwards compatible.
This means that you **must** update your configuration after pulling the version.
