-- upgrade --
CREATE TABLE IF NOT EXISTS "command_usage_analytics" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "guild_id" BIGINT,
    "timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "command_name" TYPE JSONB NOT NULL,
    "slash" BOOL NOT NULL,
    "success" SMALLINT NOT NULL  DEFAULT 0
);;
-- downgrade --
DROP TABLE IF EXISTS "command_usage_analytics";
