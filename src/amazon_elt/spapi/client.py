import logging
import time
from typing import Any

import httpx

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.auth import LwaAuth
from amazon_elt.spapi.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 5
BASE_BACKOFF_SECONDS = 5.0


class SpApiClient:
    def __init__(self, config: SpApiConfig) -> None:
        self._config = config
        self._http = httpx.Client(timeout=30.0)
        self._auth = LwaAuth(config, self._http)
        self._limiter = RateLimiter()

    def request(
        self,
        method: str,
        path: str,
        operation: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        url = self._config.endpoint + path

        for attempt in range(1, MAX_ATTEMPTS + 1):
            self._limiter.acquire(operation)
            headers = {"x-amz-access-token": self._auth.get_access_token()}
            
            response = self._http.request(
                method, url, headers=headers, params=params, json=json
            )

            if response.status_code not in RETRY_STATUS_CODES:
                response.raise_for_status()
                return response

            if attempt < MAX_ATTEMPTS:
                wait = BASE_BACKOFF_SECONDS * 2 ** (attempt - 1)
                logger.warning(
                    "%s returned %d (attempt %d/%d), retrying in %.0fs",
                    operation, response.status_code, attempt, MAX_ATTEMPTS, wait,
                )
                time.sleep(wait)

        # All attempts got 429/5xx: raise the last error
        response.raise_for_status()
        return response

    def close(self) -> None:
        self._http.close()