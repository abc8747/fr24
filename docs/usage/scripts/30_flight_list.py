# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from datetime import datetime

from fr24.authentication import login
from fr24.json import flight_list, flight_list_df, FlightListParams
from fr24.types.json import FlightList
from fr24.proto.headers import get_grpc_headers


async def my_list() -> FlightList:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        auth = await login(client)
        if auth is not None:
            print(auth.get("message"))
        response = await flight_list(
            client,
            FlightListParams(
                flight="AF291",
                timestamp=datetime.strptime("2025-01-16", "%Y-%m-%d"),  # (1)!
            ),
            headers=headers,
            auth=auth,
        )
        response.raise_for_status()
        list_ = response.json()
        return list_  # type: ignore


list_ = await my_list()
df = flight_list_df(list_)
df
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:df0]
shape: (6, 15)
┌───────────┬────────┬──────────┬─────────┬───┬─────────────┬────────────┬────────────┬────────────┐
│ flight_id ┆ number ┆ callsign ┆ icao24  ┆ … ┆ ATOD        ┆ STOA       ┆ ETOA       ┆ ATOA       │
│ ---       ┆ ---    ┆ ---      ┆ ---     ┆   ┆ ---         ┆ ---        ┆ ---        ┆ ---        │
│ u64       ┆ str    ┆ str      ┆ u32     ┆   ┆ datetime[ms ┆ datetime[m ┆ datetime[m ┆ datetime[m │
│           ┆        ┆          ┆         ┆   ┆ , UTC]      ┆ s, UTC]    ┆ s, UTC]    ┆ s, UTC]    │
╞═══════════╪════════╪══════════╪═════════╪═══╪═════════════╪════════════╪════════════╪════════════╡
│ null      ┆ AF291  ┆ null     ┆ null    ┆ … ┆ null        ┆ 2025-01-24 ┆ null       ┆ null       │
│           ┆        ┆          ┆         ┆   ┆             ┆ 18:00:00   ┆            ┆            │
│           ┆        ┆          ┆         ┆   ┆             ┆ UTC        ┆            ┆            │
│ null      ┆ AF291  ┆ null     ┆ null    ┆ … ┆ null        ┆ 2025-01-22 ┆ null       ┆ null       │
│           ┆        ┆          ┆         ┆   ┆             ┆ 18:00:00   ┆            ┆            │
│           ┆        ┆          ┆         ┆   ┆             ┆ UTC        ┆            ┆            │
│ null      ┆ AF291  ┆ null     ┆ null    ┆ … ┆ null        ┆ 2025-01-19 ┆ null       ┆ null       │
│           ┆        ┆          ┆         ┆   ┆             ┆ 18:00:00   ┆            ┆            │
│           ┆        ┆          ┆         ┆   ┆             ┆ UTC        ┆            ┆            │
│ 952249857 ┆ AF291  ┆ AFR291   ┆ 3789477 ┆ … ┆ 2025-01-17  ┆ 2025-01-17 ┆ null       ┆ 2025-01-17 │
│           ┆        ┆          ┆         ┆   ┆ 05:13:55    ┆ 18:00:00   ┆            ┆ 19:30:15   │
│           ┆        ┆          ┆         ┆   ┆ UTC         ┆ UTC        ┆            ┆ UTC        │
│ 951756645 ┆ AF291  ┆ AFR291   ┆ 3789486 ┆ … ┆ 2025-01-15  ┆ 2025-01-15 ┆ null       ┆ 2025-01-15 │
│           ┆        ┆          ┆         ┆   ┆ 03:45:20    ┆ 18:00:00   ┆            ┆ 17:58:06   │
│           ┆        ┆          ┆         ┆   ┆ UTC         ┆ UTC        ┆            ┆ UTC        │
│ 951093039 ┆ AF291  ┆ AFR291   ┆ 3789475 ┆ … ┆ 2025-01-12  ┆ 2025-01-12 ┆ null       ┆ 2025-01-12 │
│           ┆        ┆          ┆         ┆   ┆ 05:15:13    ┆ 18:00:00   ┆            ┆ 19:03:13   │
│           ┆        ┆          ┆         ┆   ┆ UTC         ┆ UTC        ┆            ┆ UTC        │
└───────────┴────────┴──────────┴─────────┴───┴─────────────┴────────────┴────────────┴────────────┘
# --8<-- [end:df0]
"""
