# Logging

When ever someone used the bot to do an action, eg sends a message, edits a message, the bot will send a logging message detailing the action to a set channel.

The bot uses webhooks to do this, as this lessens the load on the bot.
It needs the Manage Webhooks permission to do this, go to https://messagemanager.xyz/invite to reinvite with full perms.

## Setting the logging channel

To set the logging channel use the command `~setup logging <channel>`
