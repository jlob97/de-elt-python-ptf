import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = [
    "SP_API_CLIENT_ID",
    "SP_API_CLIENT_SECRET",
    "SP_API_REFRESH_TOKEN",
    "SP_API_MARKETPLACE_IDS",
]


@dataclass(frozen=True) #not mutable
class SpApiConfig:
    client_id: str
    client_secret: str = field(repr=False)
    refresh_token: str = field(repr=False)
    marketplace_ids: list[str]
    endpoint: str

    @classmethod
    def from_env(cls) -> "SpApiConfig":
        missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
        if missing:
            raise ValueError(f"Missing variables in .env: {', '.join(missing)}")

        marketplaces = os.environ["SP_API_MARKETPLACE_IDS"].split(",")

        return cls(
            client_id=os.environ["SP_API_CLIENT_ID"],
            client_secret=os.environ["SP_API_CLIENT_SECRET"],
            refresh_token=os.environ["SP_API_REFRESH_TOKEN"],
            marketplace_ids=[m.strip() for m in marketplaces],
            endpoint=os.getenv("SP_API_ENDPOINT", "https://sellingpartnerapi-na.amazon.com"),
        )

SNOWFLAKE_REQUIRED_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PRIVATE_KEY_FILE",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]

@dataclass(frozen=True)
class SnowflakeConfig:
    account: str
    user: str
    private_key_file: str
    role: str
    warehouse: str
    database: str
    schema: str

    @classmethod
    def from_env(cls) -> "SnowflakeConfig":
        missing = [name for name in SNOWFLAKE_REQUIRED_VARS if not os.getenv(name)]
        if missing:
            raise ValueError(f"Missing variables in .env: {', '.join(missing)}")

        return cls(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            private_key_file=os.environ["SNOWFLAKE_PRIVATE_KEY_FILE"],
            role=os.environ["SNOWFLAKE_ROLE"],
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            database=os.environ["SNOWFLAKE_DATABASE"],
            schema=os.environ["SNOWFLAKE_SCHEMA"],
        )