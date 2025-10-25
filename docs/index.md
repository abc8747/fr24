# fr24

[![image](https://img.shields.io/pypi/v/fr24.svg)](https://pypi.python.org/pypi/fr24)
[![image](https://img.shields.io/pypi/l/fr24.svg)](https://pypi.python.org/pypi/fr24)
[![image](https://img.shields.io/pypi/pyversions/fr24.svg)](https://pypi.python.org/pypi/fr24)
[![image](https://img.shields.io/pypi/status/fr24)](https://pypi.python.org/pypi/fr24)

`fr24` is a Python library for data retrieval from [Flightradar24](https://flightradar24.com) using [gRPC](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md) and JSON APIs.

For a detailed quickstart, examples and references, please refer to the [documentation](https://abc8747.github.io/fr24/usage/quickstart/).

## Features

`fr24` supports the following endpoints:

| Endpoint                      | Description                                                | Type |
| ----------------------------- | ---------------------------------------------------------- | ---- |
| **Live Feed**                 | Current real-time flight data within a bounding box.       | gRPC |
| **Live Feed Playback**        | Historical snapshot of live feed data for a specific time. | gRPC |
| **Flight List**               | List of flights based on registration or flight number.    | JSON |
| **Playback**                  | Historical state vectors data for a flight.                | JSON |
| **Airport Arrivals**          | Aircraft arrival information for a given airport.          | JSON |
| **Airport Search**            | Search for airports by keyword.                            | JSON |
| **Nearest Flights**           | Real-time flight data for aircraft within a given radius.  | gRPC |
| **Follow Flight** (streaming) | Historical track and real-time updates for a live flight.  | gRPC |
| **Top Flights**               | List of the most viewed flights.                           | gRPC |
| **Live Flight Status**        | Real-time status updates for live flights.                 | gRPC |
| **Flight Details**            | Detailed information for a live flight.                    | gRPC |
| **Playback Flight**           | Detailed information for a historical flight.              | gRPC |
<!--
| **Live Trail**                | Real-time trail data for a flight.                             | gRPC   |
| **Historic Trail**            | Historical trail data for a flight.                            | gRPC   |
-->

`fr24` is built with modularity and performance in mind, utilising asynchronous programming to handle concurrent requests efficiently.

## Installation

For the latest stable version:

```sh
pip install fr24
```

For a development version, clone the repository and run in the directory:

```sh
uv venv
source .venv/bin/activate
uv sync --all-extras --dev
```

This installs all optional dependencies, typing, linting, testing and documentation tools.

## Examples

Fetch live feed data for a specific bounding box:

```py
import asyncio

from fr24 import FR24, BoundingBox

bbox = BoundingBox(south=42, north=52, west=-8, east=10)

async def main() -> None:
    async with FR24() as client:
        result = await client.live_feed.fetch(bbox)
        print(result.response.content)  # access raw, undecoded bytes
        # convert to other formats:
        print(result.to_proto())  # protobuf object
        print(result.to_dict())  # nested dictionary
        print(result.to_polars())  # polars dataframe

        # write to a parquet file:
        result.write_table("feed.parquet")


if __name__ == "__main__":
    asyncio.run(main())
```

To improve efficiency and reduce API calls, `fr24` provides a simple file-based cache:

```py
import asyncio

from fr24 import FR24, FR24Cache, BBOX_FRANCE_UIR

cache = FR24Cache.default()

async def main() -> None:
    async with FR24() as client:
        result = await client.live_feed.fetch(BBOX_FRANCE_UIR)
        # on Linux, this writes to ~/.cache/fr24/feed/{timestamp_s}.parquet
        result.write_table(cache)

def some_time_later() -> None:
    for fp in cache.live_feed.glob("*"):
        print(fp)
        print(cache.live_feed.scan_table(fp).collect())

if __name__ == "__main__":
    asyncio.run(main())
    some_time_later()
```

`fr24` also comes with a CLI for quick data retrieval:

```console
$ fr24 live-feed --bounding-box "42.0,52.0,-8.0,10.0" -o feed.parquet
[00:00:00] INFO     using environment `subscription_key` and      __init__.py:98
                    `token`                                                     
[00:00:00] INFO     HTTP Request: POST                           _client.py:1740
                    https://data-feed.flightradar24.com/fr24.fee                
                    d.api.v1.Feed/LiveFeed "HTTP/2 200 OK"                      
           INFO     wrote 1500 rows to                              utils.py:229
                    `/home/user/feed.parquet
$ duckdb -c "describe select * from 'feed.parquet'";
┌─────────────────┬──────────────────────┬─────────┬───┬─────────┬─────────┐
│   column_name   │     column_type      │  null   │ … │ default │  extra  │
│     varchar     │       varchar        │ varchar │   │ varchar │ varchar │
├─────────────────┼──────────────────────┼─────────┼───┼─────────┼─────────┤
│ timestamp       │ TIMESTAMP WITH TIM…  │ YES     │ … │ NULL    │ NULL    │
│ flightid        │ UINTEGER             │ YES     │ … │ NULL    │ NULL    │
│ latitude        │ FLOAT                │ YES     │ … │ NULL    │ NULL    │
│ longitude       │ FLOAT                │ YES     │ … │ NULL    │ NULL    │
│ track           │ USMALLINT            │ YES     │ … │ NULL    │ NULL    │
│ altitude        │ INTEGER              │ YES     │ … │ NULL    │ NULL    │
│ ground_speed    │ SMALLINT             │ YES     │ … │ NULL    │ NULL    │
│ on_ground       │ BOOLEAN              │ YES     │ … │ NULL    │ NULL    │
│ callsign        │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
│ source          │ UTINYINT             │ YES     │ … │ NULL    │ NULL    │
│ registration    │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
│ origin          │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
│ destination     │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
│ typecode        │ VARCHAR              │ YES     │ … │ NULL    │ NULL    │
│ eta             │ UINTEGER             │ YES     │ … │ NULL    │ NULL    │
│ squawk          │ USMALLINT            │ YES     │ … │ NULL    │ NULL    │
│ vertical_speed  │ SMALLINT             │ YES     │ … │ NULL    │ NULL    │
│ position_buffer │ STRUCT(delta_lat I…  │ YES     │ … │ NULL    │ NULL    │
├─────────────────┴──────────────────────┴─────────┴───┴─────────┴─────────┤
│ 18 rows                                              6 columns (5 shown) │
└──────────────────────────────────────────────────────────────────────────┘
```

For a full list of commands and options, run:

```sh
fr24 --help
```

`fr24` also comes with a TUI - search for flights directly in your terminal:

```sh
fr24 tui
```

## Disclaimer

> [!IMPORTANT]  
> Code has been developed for educational purposes ONLY. Do not abuse it.

```json
{
  "copyright": "Copyright (c) 2014-2025 Flightradar24 AB. All rights reserved.",
  "legalNotice": "The contents of this file and all derived data are the property of Flightradar24 AB for use exclusively by its products and applications. Using, modifying or redistributing the data without the prior written permission of Flightradar24 AB is not allowed and may result in prosecutions."
}
```

Official Resources: [Python SDK](https://github.com/Flightradar24/fr24api-sdk-python), [API](https://fr24api.flightradar24.com/)
