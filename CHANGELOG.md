# Changelog - Bot

## v1.1.0

### Stats Function Removed

#### Summary

The stats function, which updated the names of two voice channels every thirty minutes with the amount of bot users and non bot users in a guild has been removed.  
From now on any command relating to the stats function, eg `~stats update`, `~setup botstats`, will display a warning message saying that the function was removed and a link to this changelog. After a month this will be removed.

#### Reasons

Discord has recently added restrictions on what information bots can receive from the api. These are called Privileged Intents and required approval from discord to have them after a bot reaches one hundred guilds.
One of the intents is the member intent which allows the bot to receive member_join and member_leave events among other things. Without this intent the guild count can't be updated without making a request to discord for every guild. Previously, with the member intent the guild count was updated every time the bot received the join and leave events, meaning the count was accurate.
Making a request to discord for every single guild every 30 minutes would have got out of hand after 100 guilds or so. On top of this even if the bot could keep an up to date guild count without the members intent it would not be able to get the amount of bot vs non bot accounts. This bot was unlikely to have received approval from discord for the member intent because this is the only feature that needs it and it's a very small feature. Also this feature is not following the main theme of the bot which focuses on messages in a guild.

#### Code Changes

- Replace all stats related commands with warning messages to be removed in one month.
- Remove the loop that automatically updated the stats channels.
- Remove db functions that fetched / set stats channels.
- Remove command `~stats update` from help command.
- Add warning message to setup help to be removed in one month.
- Replace setup commands relating to stats with warning messages to be removed in one month.
- Remove stats references in docs.
- Update invite link to no longer ask for manage channel permissions.
- Remove manage channel permissions from the permissions page in the docs.

> Note: I have not removed entries from the database for the stats channels, i will do this and update the database that the bot creates in one month.
