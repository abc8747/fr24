import sys

import httpx

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

from .._deprecated import JSON_API_DEPRECATION_NOTICE
from ..types.static import AircraftFamily, Airlines, Airports, Countries
from ..utils import DEFAULT_HEADERS

DEFAULT_HEADERS_STATIC = {
    **DEFAULT_HEADERS,
    "Accept": "*/*",
}


@deprecated(JSON_API_DEPRECATION_NOTICE)
async def fetch_aircraft_family(client: httpx.AsyncClient) -> AircraftFamily:
    request = httpx.Request(
        "GET",
        "https://www.flightradar24.com/mobile/aircraft-family",
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return data.json()  # type: ignore[no-any-return]


@deprecated(JSON_API_DEPRECATION_NOTICE)
async def fetch_airlines(client: httpx.AsyncClient) -> Airlines:
    request = httpx.Request(
        "GET",
        "https://www.flightradar24.com/mobile/airlines",
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return data.json()  # type: ignore[no-any-return]


@deprecated(JSON_API_DEPRECATION_NOTICE)
async def fetch_airports(
    client: httpx.AsyncClient, major_version: int = 4, minor_version: int = 0
) -> Airports:
    request = httpx.Request(
        "GET",
        f"https://www.flightradar24.com/mobile/airports/format/{major_version}",
        params={"version": minor_version},
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return data.json()  # type: ignore[no-any-return]


@deprecated(JSON_API_DEPRECATION_NOTICE)
async def fetch_countries(client: httpx.AsyncClient) -> Countries:
    request = httpx.Request(
        "GET",
        "https://www.flightradar24.com/mobile/countries",
        headers=DEFAULT_HEADERS_STATIC,
    )
    data = await client.send(request)
    data.raise_for_status()
    return data.json()  # type: ignore[no-any-return]


# NOTE: previously, the code downloaded the static json data directly into
# `Path(__file__).parent`. This gives a convenient way to access the data,
# but is often outdated. To avoid committing large diffs, we should instead
# save them into the user cache instead.
