# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import rich
from fr24 import FR24, FR24Cache


async def my_playback() -> None:
    async with FR24() as fr24:
        result = await fr24.playback.fetch(0x2FB3041)  # (1)!
        df = result.to_polars()
        print(df)
        rich.print(result.metadata())
        result.write_table(FR24Cache.default())


await my_playback()
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:df0]
shape: (363, 9)
┌────────────┬───────────┬────────────┬──────────┬───┬───────────────┬───────┬────────┬────────────┐
│ timestamp  ┆ latitude  ┆ longitude  ┆ altitude ┆ … ┆ vertical_spee ┆ track ┆ squawk ┆ ems        │
│ ---        ┆ ---       ┆ ---        ┆ ---      ┆   ┆ d             ┆ ---   ┆ ---    ┆ ---        │
│ u32        ┆ f32       ┆ f32        ┆ i32      ┆   ┆ ---           ┆ i16   ┆ u16    ┆ struct[18] │
│            ┆           ┆            ┆          ┆   ┆ i16           ┆       ┆        ┆            │
╞════════════╪═══════════╪════════════╪══════════╪═══╪═══════════════╪═══════╪════════╪════════════╡
│ 1232049993 ┆ 40.770302 ┆ -73.862801 ┆ 0        ┆ … ┆ null          ┆ 59    ┆ 0      ┆ null       │
│ 1232049997 ┆ 40.770302 ┆ -73.862503 ┆ 0        ┆ … ┆ null          ┆ 65    ┆ 0      ┆ null       │
│ 1232050001 ┆ 40.770302 ┆ -73.862198 ┆ 0        ┆ … ┆ null          ┆ 71    ┆ 0      ┆ null       │
│ 1232050005 ┆ 40.770302 ┆ -73.862198 ┆ 0        ┆ … ┆ null          ┆ 76    ┆ 0      ┆ null       │
│ 1232050009 ┆ 40.770302 ┆ -73.862198 ┆ 0        ┆ … ┆ null          ┆ 82    ┆ 0      ┆ null       │
│ …          ┆ …         ┆ …          ┆ …        ┆ … ┆ …             ┆ …     ┆ …      ┆ …          │
│ 1232051425 ┆ 40.781399 ┆ -73.998199 ┆ 326      ┆ … ┆ null          ┆ 223   ┆ 0      ┆ null       │
│ 1232051429 ┆ 40.779202 ┆ -73.999603 ┆ 274      ┆ … ┆ null          ┆ 226   ┆ 0      ┆ null       │
│ 1232051433 ┆ 40.777199 ┆ -74.001297 ┆ 187      ┆ … ┆ null          ┆ 222   ┆ 0      ┆ null       │
│ 1232051437 ┆ 40.775002 ┆ -74.002899 ┆ 106      ┆ … ┆ null          ┆ 223   ┆ 0      ┆ null       │
│ 1232051441 ┆ 40.773102 ┆ -74.004303 ┆ 42       ┆ … ┆ null          ┆ 223   ┆ 0      ┆ null       │
└────────────┴───────────┴────────────┴──────────┴───┴───────────────┴───────┴────────┴────────────┘
# --8<-- [end:df0]
"""
# %%
# --8<-- [start:metadata0]
{
    "flight_id": 50016321,
    "callsign": "AWE1549",
    "flight_number": "UA1549",
    "status_type": "departure",
    "status_text": None,
    "status_diverted": None,
    "status_time": None,
    "model_code": "A320",
    "icao24": 10493137,
    "registration": "N106US",
    "owner": None,
    "airline": None,
    "origin": "KLGA",
    "destination": "KCLT",
    "median_delay": None,
    "median_time": None,
}
# --8<-- [end:metadata0]

# %%
# --8<-- [start:script1]
import rich
from fr24 import FR24, FR24Cache

cache = FR24Cache.default()


async def my_playback() -> None:
    async with FR24() as fr24:
        result = await fr24.playback.fetch(0x2FB3041)
        result.write_table(cache)  # (1)!
    # some time later...
    df_local = cache.playback.scan_table(0x2FB3041).collect()  # (2)!
    print(df_local)


await my_playback()
# --8<-- [end:script1]

# %%
