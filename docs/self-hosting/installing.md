# Self Hosting

{% hint style="warning" %}
I do not provide support for running your own instance of this bot other than these docs, and I would prefer if you invite the official instance instead. However you can run it if you want to, and you can reach out if you think you have found a bug. I would prefer that if you self host this bot you do not run it at scale (ie only using it in your servers).
{% endhint %}

## Installation

1. Clone [the repo](https://github.com/AnotherCat/message-manager)
2. Make sure you have python3.8 and postgresql
3. Installing requirements
4. Setting up the database and roles
5. Creating a discord application and a bot user at the [discord dev website](https://discord.com/developers/applications), setup guide [here](https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account)
6. [Setting up config](#config)
7. Running `main.py`
8. Inviting the bot to your server, there will be an invite link in the python shell after you run it.

### Setup Example (linux)

```bash
~$ git clone https://github.com/AnotherCat/message-manager.git # Clone this github repo
~$ cd message-manager # Navigate to the main directory for the project.
~/message-manager$ pipenv install # Install the required python packages with pipenv
# Now you need to setup the config variables, see Config below
(bot-env) ~/message-manager$ pipenv run python3.8 main.py # Run the bot
```

Note: This assumes that you have the following packages installed:

- [Python 3.8](https://www.python.org/downloads/release/python-386/)
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

| Field            | Type      | Value             | Description                                                                                                  | Required | Default         |
| :--------------- | :-------- | :---------------- | :----------------------------------------------------------------------------------------------------------- | :------- | --------------- |
| token            | string    | Discord Bot Token | This is the discord bot token.                                                                               | Yes      | `""`            |
| default_prefix   | string    | String            | This is the default prefix before commands. If a server prefix this will be overridden.                      | Yes      | `"!"`           |
| owner            | string    | User ID           | This will appear in the info box from the `!info` command. Leave as `None` if you don't want this to appear. | No       | `None`          |
| owners           | Array[ID] | List[User Ids]    | These are users who get "admin" access to the bot, they can run bot dev only commands.                       | Yes      | `{0}`
| uri              | string    | postgres uri      | This gives the bot access to the database. You'll need to setup a postgres user and database.                | Yes      | see config file |
| guild_cache_max  | integer   | Int               | This is the maxium amount of guild-settings that will be cached before infrequently used ones are dropped    | Yes      | `500`           |
| guild_cache_drop | integer   | Int               | This is the amount of guilds that will be removed from the cache when it exceeds it's max size               | Yes      | `50`            |

## Website

I **really** would prefer if you don't run an instance of the website.
However as per the open source license terms (that i choose) i am required to provide you with installation instructions.

I use Sanic an asyncio python webframework power my site.
To run it you will need to:

- Clone AnotherCat/message-manager-site
- Install requirements `pipenv install`
- See sanic's documentation for detailed instructions on how to run a sanic site.

You are also required to provide the source code to all viewers under the terms of the license, doing this and changing other references such as invite links, support server links, etc is up to you to go into the code and change.

