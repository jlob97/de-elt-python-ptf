import pytest

from amazon_elt.spapi.rate_limit import RateLimiter


@pytest.mark.parametrize("factor", [0, -0.5, 1.5])
def test_limiter_rejects_invalid_safety_factor(factor: float) -> None:
    with pytest.raises(ValueError):
        RateLimiter(safety_factor=factor)


def test_limiter_rejects_unknown_operation() -> None:
    limiter = RateLimiter()

    with pytest.raises(KeyError):
        limiter.acquire("createReprot")