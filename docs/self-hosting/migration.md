# Migrating guides

## v1 -> v2

In v2 the database is now managed with Tortoise-ORM and aerich.

## Steps

- Backup the database. There are a number of ways you can do this, the easiest is `pg_dump`
- Pull v2.x tag from the repository 
- In the database uri in `config.py` replace `postgresql` with `postgres`
- Update packages with `pipenv install`
- Run `aerich update` in the root of the repo.
- Run the bot as normal.