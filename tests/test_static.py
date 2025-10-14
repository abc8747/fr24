import asyncio
from typing import Awaitable, Callable, Type

import httpx
import pytest
from pydantic import TypeAdapter

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
    "fetch_data,static_data_type",
    [
        (fetch_aircraft_family, AircraftFamily),
        (fetch_airlines, Airlines),
        (fetch_airports, Airports),
        (fetch_countries, Countries),
    ],
)
def test_fetch_static_types(
    fetch_data: Callable[[httpx.AsyncClient], Awaitable[StaticData]],
    static_data_type: Type[StaticData],
) -> None:
    async def fetch_data_() -> StaticData:
        async with httpx.AsyncClient() as client:
            return await fetch_data(client)

    data = asyncio.run(fetch_data_())

    ta = TypeAdapter(static_data_type)
    ta.rebuild()
    ta.validate_python(data, extra="forbid", strict=True)
