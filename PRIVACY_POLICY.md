# Privacy Policy

Message Manager provides a service through the Website (the "Site"), and the Discord Bot (the "Bot"), collectivity (the 'Service'). These services are provided to you by the Message Manager Dev Team ('we' or 'us') for users ('you').

## Data We Collect

### Data you provide

The Service has settings that administrators of servers can set up on a per server basis. Setting these settings will store the following data when provided.

- Guild ids
- Role ids
- Channel ids
- Webhook authorization details

### Data automatically collected

When you connect to the site traffic is provided through a proxy from cloudflare for security and performance reasons. Cloudflare collects anonymous data which may include but is not limited IP addresses, country, device and browser type, http request type and time. Cloudflare's privacy policy can be found [here](https://www.cloudflare.com/privacy)

We also use Cloudflare's privacy aware analytics service, which records: Referrer, Host, Country, Path, Browser, Operating System and Device Type. All data recorded is anonymous.

We use a LFU (least frequently used) caching method for caching guild settings. Part of this means that the count of times that the data per guild has been access is stored in ram. Because the prefix is checked each time a message event is received to check if the message is a command (most bots work this way) this means that the count will roughly represent the amount of messages in that guild since the bot was loaded. This data will not be used for any other purpose than to maintain the cache.

Command usage is logged for analytics purposes, the timestamp, server id, command name(s), and result (if it succeeded / errors thrown, etc). This data is only available to the bot team.  

#### Cookies

Cookies are only currently used by Cloudflare to detect bad actors and block them, and to provide their other services to us. These cookies do not allow cross site tracking and in most cases log data retrieved using these cookies is only stored for 24 hours by Cloudflare on their servers.

## Where do we store your data

Data is currently stored in the US and both services are hosted in the US.

## Why do we need that data

### To provide functionality

Data that is set by admins (guild-ids, role-ids, channel-ids) are required for certain features to work.  
Role ids are needed to confirm that a user has a set management role and thus permissions.
Guild ids are needed to link server specific settings to their relative servers.
Channel ids are needed to enable the vc-channel stats function to find the right channel.
Webhook ids and tokens are needed for logging to function

### To protect the Service

Data collected by Cloudflare is collected to protect the service from DDoS attacks among others attacks.

Command usage data is also collected to help detect / identify users who are abusing the service.  

### To help us improve the Service

Anonymous data is collected by Cloudflare that contains approximate location, device type, http request info, browser type and other device data. None of this data is personally identifiable. We use this data to give us insight on how the Service is used, and this helps us improve the Service.

Data may also be used in development and testing.

Command usage data is collected to gain insight on command usage to help focus development and identify improvements, to improve the service.

### To optimise the service

Cache access frequency is required to ensure that the data in cache is the most likely to be needed, improving the speed of the bot.

## Who is your data shared with

Other than Discord, users of the Service and developers of the Service your data is not currently shared with anyone else. However Cloudflare does collect data on our behalf regarding usage statics and preventing attacks on the service. We do not send any data that we don't collect through Cloudflare to Cloudflare.

## How to contact us

If you have a concern you can contact us a few ways.  
You can:

- Join the discord [server](https://discord.gg/xFZu29t) and contact me at `Another Cat#4247`
- Emailing [anothercat1259@gmail.com](mailto:anothercat1259@gmail.com)

## How to get your data removed

If you would like us to remove your data please reach out to us and ask.

## Changes to the policy

Note: This Privacy Policy was last updated on 28/09/2021 and came into effect on 1/10/2021. The privacy policy can be updated at anytime without any notice, however we will make an effort to inform you about the change. The support server is the best place to be to stay up to date.
