# Self Hosting

{% hint style="warning" %}
I do not provide support for running your own instance of this bot other than these docs, and I would prefer if you invite the official instance instead. However you can run it if you want to, and you can reach out if you think you have found a bug.
{% endhint %}

## Installation

1. Clone [the repo](https://github.com/AnotherCat/message-bot)
2. Make sure you have python3.8 and postgresql
3. Setting up the database and roles
4. Creating a discord application and a bot user at the [discord dev website](https://discord.com/developers/applications), setup guide [here](https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account)
5. You **MUST** enable member intents on the bot page for the bot to load.
6. [Setting up config](#config)
7. Running `main.py`
8. Inviting the bot to your server, there will be an invite link in the python shell after you run it.

### Setup Example (linux)

```bash
~$ python3.8 #check if python is installed.
~$ git clone https://github.com/AnotherCat/message-bot.git # Clone this github repo
~$ cd message-bot # Navigate to the main directory for the project.
~/message-bot$ pipenv install # Install the required python packages with pipenv
# Now you need to setup the config variables, see Config below
(bot-env) ~/message-bot$ pipenv run python3.8 main.py # Run the bot
```

Note: This assumes that you have the following packages installed:

- [Python 3.8](https://www.python.org/downloads/release/python-386/) (discord.py does nto currently support the latest version of python, 3.9)
- The latest version of [git](https://git-scm.com/downloads)
- The latest version of [postgresql](https://www.postgresql.org/download/)
- [Pipenv](https://pipenv.pypa.io/en/latest/install/)

Some commands may require sudo privileges depending on your system.

For windows do the same, but replace `python3` with `python`

## Config

This bot uses a `config.py` file to store config.

### Setting up PostgreSQL

1. Install PostgreSQL
2. Create a role for the bot to use
3. Create the database

```bash
$sudo -u postgres psql
postgres=# CREATE ROLE bot LOGIN PASSWORD 'password' SUPERUSER; # Create the role for the bot to use. You can do it without superuser, look up the docs to see what's needed.
postgres=# CREATE DATABASE bot OWNER bot; # Create a database with the same name as the role, so that you can login easier
postgres=# CREATE DATABASE message_bot OWNER bot; # Create the database the bot will use
postgres=# \q
```

Then enter the values into the postgres_uri config.

### Setting up config

1. Rename `config_example.py` to `config.py`
2. Set the values as per the table below

#### Config Values

| Field         | Type     | Value                                             | Description                                                  | Required | Default |
| :-------------- | :------------------ | :----------------------------------------------------------- | --------------- | :-------------- | --------------- |
| token | string         | Discord Bot Token  | This is the discord bot token.                               | Yes | `""` |
| default_prefix    | string         | String    | This is the default prefix before commands. If a server prefix this will be overridden. | Yes | `"!"` |
| owner   | string | User ID | This will appear in the info box from the `!info` command. Leave as `None` if you don't want this to appear. | No | `None` |
| bypassed_users | int[] | User ids in an array | By adding a user to this this will bypass all user checks. This is useful for if you have set allowed_server, but want some users to still be able to use it. **Dangerous** permission to grant. | No | `[]` |
| uri | string | postgres uri | This gives the bot access to the database. You'll need to setup a postgres user and database. | Yes | see config file |

## Website

I **really** would prefer if you don't run an instance of the website.
However as per the open source license terms (that i choose) i am required to provide you with installation instructions.

I use Quart an asyncio version of Flask to power my site.
To run it you will need to:

- Clone AnotherCat/message-manager-site
- Set a `secret_key` in `config.py`
- Setup a production server, see Quart's docs for more instructions

You are also required to provide the source code to all viewers under the terms of the license, doing this and changing other references such as invite links, support server links, etc is up to you to go into the code and change.

### Updates

I will be using the standard version naming.

If the first number in the tuple is the same, it will not break if you leave config the same. In this case all you have to do it pull the repo as `config.py` is the only file that is user specific and there is no file named that in the repo.
It is still suggested that you read the update notes and update your config as said, but if you don't nothing will break.

If the first number in the tuple changes, this means that it is no longer backwards compatible.
This means that you **must** update your configuration after pulling the version.

After any update, do `pipenv install` again
