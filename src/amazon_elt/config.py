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