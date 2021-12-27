

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1



# Install pip requirements
COPY Pipfile .
COPY Pipfile.lock .
RUN python -m pip install pipenv
RUN pipenv install --system --deploy


WORKDIR /app
COPY . /app


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

## Copy variables
ARG DEFAULT_PREFIX
ARG DISCORD_TOKEN
ARG SENTRY_DSN
ARG GUILD_CACHE_MAX
ARG GUILD_CACHE_DROP
ARG BOT_OWNERS
ARG BOT_SELFHOST
ARG LISTING_DBL_TOKEN
ARG LISTING_DBOATS_TOKEN   
ARG LISTING_DEL_TOKEN
ARG LISTING_DBGG_TOKEN
ARG LISTING_TOPGG_TOKEN

## Database variables
ARG PGHOST
ARG PGPASSWORD
ARG PGDATABASE
ARG PGUSER
ARG PGPORT


RUN aerich upgrade

CMD ["python", "main.py"]
