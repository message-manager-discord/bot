---
description: >-
  If set the bot will automaticlly update the name of a voice channel to match
  the current bot / member accounts in the server.
---

# Stats

To setup the stats see the [config page](../startup/setup/config.md#bot-stats-voice-channel)

Stats will be updated every 30 minutes or so, this is on a loop and not on a join event to avoid discord's harsh rate limits.

## Force updating

If for some reason you want to update the stats you can force update them. This command has a 10 minute guild wide cooldown.  

{% hint style="warning" %}
This requires the management role.
{% endhint %}

`~stats update`
