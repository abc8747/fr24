# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
from fr24 import FR24
from fr24.types.json import AirportList

import polars as pl


async def my_arrivals() -> AirportList:
    async with FR24() as fr24:
        result = await fr24.airport_list.fetch(
            airport="tls",
            mode="arrivals",
        )
        return result.to_dict()


airports = await my_arrivals()
arrivals = airports["result"]["response"]["airport"]["pluginData"]["schedule"][
    "arrivals"
]["data"]
assert arrivals is not None
df = pl.json_normalize(arrivals)
print(df)
# %%
# --8<-- [start:script0]
import httpx

from fr24.types.json import AirportList
from fr24.json import airport_list, AirportListParams
from fr24.proto.headers import get_grpc_headers

import polars as pl


async def my_arrivals() -> AirportList:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        response = await airport_list(
            client,
            AirportListParams(airport="tls", mode="arrivals"),
            headers=headers,
            auth=None,
        )
        response.raise_for_status()
        list_ = response.json()
        return list_  # type: ignore


airports = await my_arrivals()
arrivals = airports["result"]["response"]["airport"]["pluginData"]["schedule"][
    "arrivals"
]["data"]
assert arrivals is not None
df = pl.json_normalize(arrivals)
print(df)
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:df0]
shape: (10, 76)
┌───────────┬───────────┬───────────┬───────────┬───┬───────────┬───────────┬───────────┬──────────┐
│ flight.id ┆ flight.id ┆ flight.id ┆ flight.id ┆ … ┆ flight.ti ┆ flight.ai ┆ flight.ow ┆ flight.a │
│ entificat ┆ entificat ┆ entificat ┆ entificat ┆   ┆ me.other. ┆ rcraft.im ┆ ner       ┆ irline   │
│ ion.id    ┆ ion.row   ┆ ion.numbe ┆ ion.numbe ┆   ┆ duration  ┆ ages      ┆ ---       ┆ ---      │
│ ---       ┆ ---       ┆ r.d…      ┆ r.a…      ┆   ┆ ---       ┆ ---       ┆ null      ┆ null     │
│ str       ┆ i64       ┆ ---       ┆ ---       ┆   ┆ null      ┆ null      ┆           ┆          │
│           ┆           ┆ str       ┆ str       ┆   ┆           ┆           ┆           ┆          │
╞═══════════╪═══════════╪═══════════╪═══════════╪═══╪═══════════╪═══════════╪═══════════╪══════════╡
│ 3963916d  ┆ 563063588 ┆ AF6132    ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 1         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ null      ┆ 563365562 ┆ null      ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 4         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ 39638d76  ┆ 563085809 ┆ T71527    ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 2         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ 3963a803  ┆ 563063662 ┆ AF7408    ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 2         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ 396399a4  ┆ 563087474 ┆ U24849    ┆ EC4849    ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 7         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ null      ┆ 563088423 ┆ V72371    ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 4         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ 3963978d  ┆ 563085809 ┆ T73718    ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 1         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ 3963ab98  ┆ 563089434 ┆ XK720     ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 8         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ 396398ab  ┆ 563071223 ┆ FR3903    ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 6         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
│ 3963b61f  ┆ 563072081 ┆ GP155     ┆ null      ┆ … ┆ null      ┆ null      ┆ null      ┆ null     │
│           ┆ 9         ┆           ┆           ┆   ┆           ┆           ┆           ┆          │
└───────────┴───────────┴───────────┴───────────┴───┴───────────┴───────────┴───────────┴──────────┘
# --8<-- [end:df0]
"""
