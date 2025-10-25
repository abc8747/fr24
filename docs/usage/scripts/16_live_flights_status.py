# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
from fr24 import FR24, FR24Cache


async def get_nearest_flight_ids(fr24: FR24) -> list[int]:
    nearest_result = await fr24.nearest_flights.fetch(
        lat=22.31257, lon=113.92708, radius=10000, limit=1500
    )
    return [
        flight.flight.flightid
        for flight in nearest_result.to_proto().flights_list
    ]


async def my_live_flights_status() -> None:
    async with FR24() as fr24:
        nearest_flight_ids = await get_nearest_flight_ids(fr24)
        result = await fr24.live_flights_status.fetch(
            flight_ids=nearest_flight_ids[:5]
        )
        print(result)
        print(result.to_dict())
        print(result.to_polars())
        result.write_table(FR24Cache.default())


await my_live_flights_status()
# --8<-- [end:script]

# %%
"""
# --8<-- [start:result]
LiveFlightsStatusResult(
    request=LiveFlightsStatusParams(
        flight_ids=[981395112, 981399624, 981364304, 981357406, 981398399]
    ),
    response=<Response [200 OK]>,
    timestamp=1748186042
)
# --8<-- [end:result]
# --8<-- [start:dict]
{
    'flights_map': [
        {'flight_id': 981395112, 'data': {'lat': 22.311754, 'lon': 113.92508, 'status': 'LIVE'}},
        {'flight_id': 981398399, 'data': {'lat': 22.313644, 'lon': 113.915115, 'status': 'LIVE'}},
        {'flight_id': 981364304, 'data': {'lat': 22.318283, 'lon': 113.928314, 'status': 'LIVE'}},
        {'flight_id': 981357406, 'data': {'lat': 22.313244, 'lon': 113.934654, 'status': 'LIVE'}},
        {'flight_id': 981399624, 'data': {'lat': 22.310404, 'lon': 113.93139, 'status': 'LIVE'}}
    ]
}
# --8<-- [end:dict]
# --8<-- [start:polars]
shape: (5, 5)
┌───────────┬───────────┬────────────┬────────┬────────┐
│ flight_id ┆ latitude  ┆ longitude  ┆ status ┆ squawk │
│ ---       ┆ ---       ┆ ---        ┆ ---    ┆ ---    │
│ u32       ┆ f32       ┆ f32        ┆ u8     ┆ u16    │
╞═══════════╪═══════════╪════════════╪════════╪════════╡
│ 981395112 ┆ 22.311754 ┆ 113.925079 ┆ 4      ┆ 0      │
│ 981398399 ┆ 22.313644 ┆ 113.915115 ┆ 4      ┆ 0      │
│ 981364304 ┆ 22.318283 ┆ 113.928314 ┆ 4      ┆ 0      │
│ 981357406 ┆ 22.313244 ┆ 113.934654 ┆ 4      ┆ 0      │
│ 981399624 ┆ 22.310404 ┆ 113.931389 ┆ 4      ┆ 0      │
└───────────┴───────────┴────────────┴────────┴────────┘
# --8<-- [end:polars]
"""
