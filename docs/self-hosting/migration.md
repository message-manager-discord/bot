# Migrating guides

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
