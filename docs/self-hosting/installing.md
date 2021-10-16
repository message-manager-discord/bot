# Self Hosting

{% hint style="warning" %}
I do not provide support for running your own instance of this bot other than these docs, and I would prefer if you invite the official instance instead. However you can run it if you want to, and you can reach out if you think you have found a bug. I would prefer that if you self host this bot you do not run it at scale (ie only using it in your servers).
{% endhint %}

## Installation

1. Clone [the repo](https://github.com/message-manager-discord/bot)
2. Make sure you have docker
3. Creating a discord application and a bot user at the [discord dev website](https://discord.com/developers/applications), setup guide [here](https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account)
4. [Setting up config](#config)
5. Building and running the bot
6. Performing the initial migration
7. Inviting the bot to your server, there will be an invite link in the docker container log

### Setup Example (linux)

```bash
~$ git clone https://github.com/message-manager-discord/bot.git # Clone this github repo
~$ cd bot # Navigate to the main directory for the project.
# Now you need to setup the config variables, see Config below
~/bot$ docker-compose up --d --build # Run the bot in the background
~/bot$ docker-compose exec bot aerich upgrade # Migrate the database
```

Note: This assumes that you have the following packages installed:

- Docker

Some commands may require sudo privileges depending on your system.

## Config

This bot uses a `.env` file to store config.

### Setting up config

1. Rename `.env.example` to `.env`
2. Set the values as per the comments in `.env` and `load_config.py`

## Website

I **really** would prefer if you don't run an instance of the website.
However as per the open source license terms (that I choose) I am required to provide you with installation instructions.

I use Netlify to deploy the site, which is a Next.js site

See netlify's docs for more information

You are also required to provide the source code to all viewers under the terms of the license, doing this and changing other references such as invite links, support server links, etc is up to you to go into the code and change.
