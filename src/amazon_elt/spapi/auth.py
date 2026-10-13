import time

import httpx
from pydantic import BaseModel

from amazon_elt.config import SpApiConfig

LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"
REFRESH_MARGIN_SECONDS = 60

# BaseModel is like jsonlite::fromJSON() at R, and most important it does model_validate() 
# at start and throws ValidationError if something is missing.
class LwaTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class LwaAuth:
    def __init__(self, config: SpApiConfig, http: httpx.Client) -> None:
        self._config = config
        self._http = http
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def get_access_token(self) -> str:
        if self._access_token is not None and time.monotonic() < self._expires_at:  
            # !is.null(x) equivalent to 'is not None', never use == at Python
            return self._access_token
        return self._refresh()

    def _refresh(self) -> str:
        response = self._http.post(
            LWA_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._config.refresh_token,
                "client_id": self._config.client_id,
                "client_secret": self._config.client_secret,
            },
        )
        response.raise_for_status() #Just an early error if goes anything that isnt a 200.
        token = LwaTokenResponse.model_validate(response.json()) #Checks with the defined class

        self._access_token = token.access_token
        self._expires_at = time.monotonic() + token.expires_in - REFRESH_MARGIN_SECONDS
        return token.access_token