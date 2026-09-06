from typing import cast

from ..clients import AsyncClientLike
from ..types.static import AircraftFamily, Airlines, Airports, Countries
from ..utils import DEFAULT_HEADERS

DEFAULT_HEADERS_STATIC = {
    **DEFAULT_HEADERS,
    "Accept": "*/*",
}


async def fetch_aircraft_family(client: AsyncClientLike) -> AircraftFamily:
    request = client.build_request(
        "GET",
        "https://www.flightradar24.com/mobile/aircraft-family",
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return cast(AircraftFamily, data.json())


async def fetch_airlines(client: AsyncClientLike) -> Airlines:
    request = client.build_request(
        "GET",
        "https://www.flightradar24.com/mobile/airlines",
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return cast(Airlines, data.json())


async def fetch_airports(
    client: AsyncClientLike,
    major_version: int = 4,
    minor_version: int = 0,
) -> Airports:
    request = client.build_request(
        "GET",
        f"https://www.flightradar24.com/mobile/airports/format/{major_version}",
        params={"version": minor_version},
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return cast(Airports, data.json())


async def fetch_countries(client: AsyncClientLike) -> Countries:
    request = client.build_request(
        "GET",
        "https://www.flightradar24.com/mobile/countries",
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return cast(Countries, data.json())


# NOTE: previously, the code downloaded the static json data directly into
# `Path(__file__).parent`. This gives a convenient way to access the data,
# but is often outdated. To avoid committing large diffs, we should instead
# save them into the user cache instead.
