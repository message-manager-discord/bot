---
description: >-
  The main function of this bot is to easily manage key server information
  messages.
---

# Messages

## Features

* Sending messages remotely \(from another channel\)
* Editing messages that were 'sent' by someone else
* Deleting messages from the bot
* Fetching the raw message content
* Commands limited to users with a set role

## Usage

### Interactive modes

All message commands are interactive.  
This means that if parts of the command are not given, you will be prompted for them. An example of the `send` command and this being used is below:

![Interactive example](../.gitbook/assets/send_interactive%20%281%29.png)

### Plain content messages

#### Sending messages

To send a message you must specify the channel and content to send.  
The content may be either just the exact message after the channel or enclosed in a code block with triple backticks \( \`\`\` \). If it is the code block will be removed before sending. If you would like to send a code block just put six backticks instead of three.

{% hint style="info" %}
The `<channel>` can be either the channel id or the channel mention.
{% endhint %}

`~send <channel> <content>`

Example:

![Sending a message](../.gitbook/assets/send_1%20%281%29.png)

![You can also do this](../.gitbook/assets/send_1_code_block%20%281%29.png)

![And the result](../.gitbook/assets/send_2%20%281%29.png)

#### Editing Messages

To edit messages you need to provide the channel, message id and the new content  
The bot cannot edit messages that were not sent from the bot.

`~edit <channel> <message id> <new content>`

![Editing the message](../.gitbook/assets/edit_1%20%281%29.png)

![The edited message](../.gitbook/assets/edit_2%20%281%29.png)

### Rich Embed Messages

If you are struggling with the formatting, please join the support server and ask.

#### Sending rich embeds

When sending rich embeds there are two options.

##### Sending basic embeds

This will send an embed with only the title and description set.
The command is `~send-embed <channel>` the bot will then prompt you for the title and then the description.

##### Sending full embeds

This is sending a fully customizable embed. The command will take the JSON version of an embed and turn it into an embed. The format for the JSON can be found on the [discord dev website](https://discord.com/developers/docs/resources/channel#embed-object). I suggest using a tool like [discohook](https://discohook.org) and then copying the JSON content.
`~send-embed-json <channel> <json-embed>`

#### Editing rich embeds

Two options as above, both take the same content.  
{% hint style="warning" %}
Trying to edit a message without an embed will result in an error.
{% endhint %} 

##### Editing basic embeds

This will update only the title and description of the embed in the message provided. Any other content is ingored.  
`~edit-embed <channel> <message>` The title and description will be prompted

##### Editing full embeds

Provide the JSON form of the new embed, the format can be found in the sending [section](/#full-embeds)  
I suggest fetching the JSON version of the original embed and then editing it to use in this command.  
`~edit-embed-json <channel> <message> <json-embed>`

### Fetching messages

When you 'fetch' a message it will return a `.txt` or `.json` file depending on the type of message.
If the message is an embed the bot will send a `.json` file with the JSON representation of the embed.  
This is useful because it mean that you can view and change the exact content that the bot handles without any of discord's formatting.

`~fetch <channel> <message id>`  
Alias: `~fetch-embed`

{% code title="Content.txt" %}

```text
Content:

This message was edited!
```

{% endcode %}

### Deleting messages

The bot can delete messages that it has sent. This is useful in situations where you don't have the `MANAGE MESSAGES` permission.  
You will be prompted to confirm the deletion

{% hint style="info" %}
A `.txt` file will be returned if the content is too long, or a `.json` file if the message was an embed.
{% endhint %}

`~delete <channel> <message id>`  
Alias: `~delete-embed`

![Deleting a message](../.gitbook/assets/delete%20%281%29.png)
