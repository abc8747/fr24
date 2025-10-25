# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx

from fr24.authentication import login
from fr24.json import playback, playback_df, PlaybackParams
from fr24.types.json import Playback
from fr24.proto.headers import get_grpc_headers


async def my_playback() -> Playback:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        auth = await login(client)
        if auth is not None:
            print(auth.get("message"))
        response = await playback(
            client,
            PlaybackParams(flight_id="38c59db3"),
            headers=headers,
            auth=auth,
        )
        response.raise_for_status()
        list_ = response.json()
        return list_  # type: ignore


list_ = await my_playback()
df = playback_df(list_)
df
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:df0]
shape: (203, 9)
┌────────────┬───────────┬────────────┬──────────┬───┬───────────────┬───────┬────────┬────────────┐
│ timestamp  ┆ latitude  ┆ longitude  ┆ altitude ┆ … ┆ vertical_spee ┆ track ┆ squawk ┆ ems        │
│ ---        ┆ ---       ┆ ---        ┆ ---      ┆   ┆ d             ┆ ---   ┆ ---    ┆ ---        │
│ u32        ┆ f32       ┆ f32        ┆ i32      ┆   ┆ ---           ┆ i16   ┆ u16    ┆ struct[18] │
│            ┆           ┆            ┆          ┆   ┆ i16           ┆       ┆        ┆            │
╞════════════╪═══════════╪════════════╪══════════╪═══╪═══════════════╪═══════╪════════╪════════════╡
│ 1737166526 ┆ 22.313072 ┆ 113.931381 ┆ 0        ┆ … ┆ 0             ┆ 317   ┆ 0      ┆ null       │
│ 1737166557 ┆ 22.312778 ┆ 113.931618 ┆ 0        ┆ … ┆ 0             ┆ 270   ┆ 0      ┆ null       │
│ 1737166584 ┆ 22.312763 ┆ 113.931953 ┆ 0        ┆ … ┆ 0             ┆ 250   ┆ 0      ┆ null       │
│ 1737166816 ┆ 22.312626 ┆ 113.931557 ┆ 0        ┆ … ┆ 0             ┆ 250   ┆ 3041   ┆ null       │
│ 1737166864 ┆ 22.312477 ┆ 113.931068 ┆ 0        ┆ … ┆ 0             ┆ 250   ┆ 3041   ┆ null       │
│ …          ┆ …         ┆ …          ┆ …        ┆ … ┆ …             ┆ …     ┆ …      ┆ …          │
│ 1737167965 ┆ 22.200348 ┆ 114.345802 ┆ 13500    ┆ … ┆ 3328          ┆ 142   ┆ 3041   ┆ null       │
│ 1737167997 ┆ 22.154388 ┆ 114.382454 ┆ 14850    ┆ … ┆ 1536          ┆ 143   ┆ 3041   ┆ null       │
│ 1737168028 ┆ 22.107239 ┆ 114.419304 ┆ 16050    ┆ … ┆ 2368          ┆ 143   ┆ 3041   ┆ null       │
│ 1737168060 ┆ 22.059942 ┆ 114.456535 ┆ 17200    ┆ … ┆ 2048          ┆ 143   ┆ 3041   ┆ null       │
│ 1737168092 ┆ 22.008501 ┆ 114.497017 ┆ 18350    ┆ … ┆ 2048          ┆ 143   ┆ 3041   ┆ null       │
└────────────┴───────────┴────────────┴──────────┴───┴───────────────┴───────┴────────┴────────────┘
# --8<-- [end:df0]
"""
