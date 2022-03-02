# Migrating guides

{% hint style="warning" %}
The current version of the bot will be deprecated towards the end of March /
April 2022.  
 The new version is more microservice based and mainly build in typescript.  
 Development has been stopped on the old (python) version of the bot, and bug
fixes will only remain until the new version is released. If you would like
more information on this, please join the support server.
{% endhint %}

## v2 - v3

You will need to reinstall the bot with docker, config will also need to be ported over. No intervention should be required with the database.

## v1 -> v2

In v2 the database is now managed with Tortoise-ORM and aerich.

### Steps

- Backup the database. There are a number of ways you can do this, the easiest is `pg_dump`
- Pull the latest `v1.x` tag, check that tag and then run the bot. **This step is vital to avoid data loss**.
- Pull v2.x tag from the repository then check it out.
- In the database uri in `config.py` replace `postgresql` with `postgres`
- Update packages with `pipenv install`
- Run `aerich update` in the root of the repo.
- Run the bot as normal.
