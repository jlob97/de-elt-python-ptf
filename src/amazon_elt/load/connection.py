import snowflake.connector
from snowflake.connector import SnowflakeConnection

from amazon_elt.config import SnowflakeConfig


def connect(config: SnowflakeConfig) -> SnowflakeConnection:
    return snowflake.connector.connect(
        account=config.account,
        user=config.user,
        private_key_file=config.private_key_file,
        role=config.role,
        warehouse=config.warehouse,
        database=config.database,
        schema=config.schema,
    )