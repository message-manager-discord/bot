-- upgrade --
CREATE TABLE IF NOT EXISTS "channels" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "webhook_id" BIGINT,
    "webhook_token" VARCHAR(255)
);
ALTER TABLE IF EXISTS "servers" RENAME TO "guilds";
CREATE TABLE IF NOT EXISTS "guilds" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "management_role_id" BIGINT,
    "prefix" VARCHAR(3) NOT NULL DEFAULT '~'
);

CREATE TABLE IF NOT EXISTS "logging_channels" (
    "logger_type" VARCHAR(20) NOT NULL,
    "channel_id" BIGINT NOT NULL REFERENCES "channels" ("id") ON DELETE CASCADE,
    "guild_id" BIGINT NOT NULL REFERENCES "guilds" ("id") ON DELETE CASCADE
);

ALTER TABLE "logging_channels" ADD COLUMN "id" SERIAL NOT NULL PRIMARY KEY;

ALTER TABLE "logging_channels" DROP CONSTRAINT IF EXISTS "unique_type";

ALTER TABLE "logging_channels" ADD CONSTRAINT "uid_logging_cha_guild_i_b7be0e" UNIQUE ("guild_id", "channel_id");

CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
