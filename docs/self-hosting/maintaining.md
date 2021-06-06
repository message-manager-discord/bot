# Maintaining your self hosted bot

## Updating

Unless you want to help out and test the most recent version, **only** pull from the latest tag.

If there have been no breaking changes then all you need to do is fetch the most recent tag from github and restart the bot.

Otherwise you will have to refer to the migration page.

## Database

After pulling from the remote run `pipenv install` then `aerich upgrade` 
If you are currently on a v1.x version or earlier **this won't work** and make sure that you read the migration page.