from collections.abc import Awaitable
from typing import Callable

import pytest
from pydantic import TypeAdapter

from fr24.clients.curl import CurlAsyncClient
from fr24.static import (
    fetch_aircraft_family,
    fetch_airlines,
    fetch_airports,
    fetch_countries,
)
from fr24.types.static import (
    AircraftFamily,
    Airlines,
    Airports,
    Countries,
    StaticData,
)


@pytest.mark.parametrize(
    ("fetch_data", "static_data_type"),
    [
        (fetch_aircraft_family, AircraftFamily),
        (fetch_airlines, Airlines),
        (fetch_airports, Airports),
        (fetch_countries, Countries),
    ],
)
@pytest.mark.anyio
async def test_fetch_static_types(
    fetch_data: Callable[[CurlAsyncClient], Awaitable[StaticData]],
    static_data_type: type[StaticData],
    curl_client: CurlAsyncClient,
) -> None:
    data = await fetch_data(curl_client)

    ta = TypeAdapter(static_data_type)
    ta.rebuild()
    ta.validate_python(data, extra="forbid", strict=True)
