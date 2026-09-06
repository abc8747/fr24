import time
from collections.abc import Generator

import pytest

from fr24 import FR24
from fr24.service import NearestFlightsResult


@pytest.fixture(autouse=True)
def slow_down() -> Generator[None, None, None]:
    """Ratelimit API tests to avoid overloading the server."""

    yield
    time.sleep(2.5)


@pytest.fixture
async def nearest_flights_result(
    fr24: FR24,
) -> NearestFlightsResult:
    LON = 113.92708
    LAT = 22.31257
    RADIUS = 10000
    LIMIT = 1500

    result = await fr24.nearest_flights.fetch(
        lon=LON, lat=LAT, radius=RADIUS, limit=LIMIT
    )
    return result
