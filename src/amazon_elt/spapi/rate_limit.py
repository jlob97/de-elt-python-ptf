import time

# Amazon API published limits: (requests per second, burst)
OPERATION_LIMITS: dict[str, tuple[float, int]] = {
    "createReport": (0.0167, 15),
    "getReport": (2.0, 15),
    "getReportDocument": (0.0167, 15),
    "getMarketplaceParticipations": (0.016, 15),
}

# Safety factor so we can use the API if needed. Easy to change.
SAFETY_FACTOR = 0.8


class TokenBucket:
    def __init__(self, rate: float, burst: int) -> None:
        self.rate = rate
        self.burst = burst
        self._tokens = float(burst)
        self._updated_at = time.monotonic()

    def acquire(self) -> None:
        self._refill()
        if self._tokens < 1:
            time.sleep((1 - self._tokens) / self.rate)
            self._refill()
        self._tokens -= 1

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._updated_at
        self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
        self._updated_at = now


class RateLimiter:
    def __init__(
        self,
        limits: dict[str, tuple[float, int]] = OPERATION_LIMITS,
        safety_factor: float = SAFETY_FACTOR,
    ) -> None:
        if not 0 < safety_factor <= 1:
            raise ValueError(f"safety_factor must be between 0 and 1, got {safety_factor}")

        self._buckets = {
            operation: TokenBucket(rate * safety_factor, max(1, int(burst * safety_factor)))
            for operation, (rate, burst) in limits.items()
        }

    def acquire(self, operation: str) -> None:
        self._buckets[operation].acquire()