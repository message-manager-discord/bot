# Maintaining your self hosted bot

## Updating

Unless you want to help out and test the most recent version, **only** pull from the latest tag.

If there have been no breaking changes then all you need to do is fetch the most recent tag from github and restart the bot.

Otherwise you will have to refer to the migration page.

## Database

To migrate the database run this after pulling and restarting:

```bash
~/bot$ docker-compose exec bot aerich upgrade
```

### Backups

Making a backup:

```bash
~/bot$ docker exec -i postgres /usr/bin/pg_dump -U <postgresql_user> <postgresql_database> > postgres-backup.sql
```

Restoring from a plain text backup

```bash
~/bot$ docker cp <archive> <container name>:/backup-bot.sql
~/bot$ docker-compose exec postgres psql -U <db-user> -d <db-name> -f /backup-bot.sql
~/bot$ docker-compose exec postgres rm /backup-bot.sql
```

NOTE: This is just an example, you'll probably need to figure out docker commands and what works for you
