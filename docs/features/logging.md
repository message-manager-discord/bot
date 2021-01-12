# Logging

Whenever someone uses the bot to do an action, eg sends a message, edits a message, the bot will send a logging message detailing the action to a set channel.

The bot uses webhooks to do this, as this lessens the load on the bot.
It needs the Manage Webhooks permission to do this, go to https://messagemanager.xyz/invite to reinvite with full perms.

## Setting the logging channel

To set the logging channel use the command `~setup logging <channel>`
This require manage webhooks to work correctly

{% hint style="warning" %}
If the bot can't view the channel, doesn't have `manage_webhooks` or `send_messages` permissions in that channel sending the log will fail **silently**.
{% endhint %}
