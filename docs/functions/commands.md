---
description: A list of all the commands
---

# Commands

{% hint style="info" %}

1. The default prefix is used below for simplicity. Replace this with your prefix for the server.
2. `<>` means a required paramater and `{}` means a optional paramater.

{% endhint %}

{% hint style="warning" %}
Do **not** include the `<>` or `{}` while doing commands. This is just a indicator to show you need to fill it in.
{% endhint %}

## General commands

| Command | Description | Permission Level |
| :--- | :--- | :--- |
| `~help` | Displays help | `@everyone` |
| `~info` | Displays information about the bot | `@everyone` |
| `~ping` | Returns the bot's current command latency | `@everyone` |

## Message commands

| Command | Description | Permission Level |
| :--- | :--- | :--- |
| `~send <channel> <content>` | Send's a message to a specified channel | Management Role |
| `~edit <channel> <message id> <new content>` | Edits a message that was previously send by the bot | Management Role |
| `~fetch <channel> <message id>` | Returns the raw content of that message | Management Role |
| `~delete <channel> <message id>` | Deletes a message that the bot sent | Management Role |

## Stats commands

| Command | Description | Permission Level |
| :--- | :--- | :--- |
| `~stats update` | Force updates the stats. Has a 10 minute cooldown | Management Role |

## Setup commands

{% hint style="info" %}
All commands below will return the current setting if the optional pararmenter is not included.
{% endhint %}

| Command | Description | Permission Level |
| :--- | :--- | :--- |
| `~setup` | Gives information about the setup commands | `ADMINISTRATOR` |
| `~setup prefix {new prefix}` | Changes the guild's prefix to the new prefix. | `ADMINISTRATOR` |
| `~setup admin {admin role}` | Sets the administrative role, or as is more commonly reffered to, the management role | `ADMINISTRATOR` |
| `~setup botstats {voice channel id}` | Sets the the channel to update the bot numbers to | `ADMINISTRATOR` |
| `~setup userstats {voice channel id}` | Sets the the channel to update the user numbers to | `ADMINISTRATOR` |
| `~prefix` | Returns the current prefix for the guild. This is useful if you forget the prefix because it can be invoked with the bot mention prefix | `@everyone` |
