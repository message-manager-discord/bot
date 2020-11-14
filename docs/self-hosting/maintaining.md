# Maintaining your self hosted bot

## Updating

Unless you want to help out and test the most recent version, **only** pull from the latest tag.

If there have been no breaking changes then all you need to do is fetch the most recent tag from github and restart the bot.

Otherwise you will have to refer to the release notes in that release.

## Database

Every time the bot is run a check is made to check if the database is up to date with the code version.  
If it is not it executes an SQL query and updates the database.
