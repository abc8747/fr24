# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
from fr24 import FR24, FR24Cache


async def my_nearest_flights() -> None:
    async with FR24() as fr24:
        result = await fr24.nearest_flights.fetch(
            lat=22.31257, lon=113.92708, radius=10000, limit=1500
        )
        print(result)
        print(result.to_dict())
        print(result.to_polars())
        result.write_table(FR24Cache.default())


await my_nearest_flights()
# --8<-- [end:script]

# %%
"""
# --8<-- [start:result]
NearestFlightsResult(
    request=NearestFlightsParams(
        lat=22.31257,
        lon=113.92708,
        radius=10000,
        limit=1500
    ),
    response=<Response [200 OK]>,
    timestamp=1748177063
)
# --8<-- [end:result]
# --8<-- [start:dict]
{
    'flights_list': [
        {
            'flight': {
                'flightid': 981376678,
                'lat': 22.315142,
                'lon': 113.92878,
                'track': 67,
                'timestamp': 1748178906,
                'on_ground': True,
                'extra_info': {'reg': 'B-18663', 'route': {'from': 'HKG'}, 'type': 'B738', 'logo_id': 86},
                'timestamp_ms': '1748178906661'
            },
            'distance': 334
        },
        ...
        {
            'flight': {
                'flightid': 981339515,
                'lat': 22.305908,
                'lon': 113.83389,
                'track': 71,
                'alt': 875,
                'speed': 130,
                'icon': 'A330',
                'timestamp': 1748178957,
                'callsign': 'CPA381',
                'extra_info': {
                    'flight': 'CX381',
                    'reg': 'B-LBJ',
                    'route': {'from': 'PVG', 'to': 'HKG'},
                    'type': 'A333',
                    'logo_id': 57
                },
                'timestamp_ms': '1748178957019'
            },
            'distance': 9629
        }
    ]
}
# --8<-- [end:dict]
# --8<-- [start:polars]
shape: (20, 19)
┌────────────┬───────────┬───────────┬────────────┬───┬────────────┬────────┬───────────┬──────────┐
│ timestamp  ┆ flightid  ┆ latitude  ┆ longitude  ┆ … ┆ vertical_s ┆ squawk ┆ position_ ┆ distance │
│ ---        ┆ ---       ┆ ---       ┆ ---        ┆   ┆ peed       ┆ ---    ┆ buffer    ┆ ---      │
│ u32        ┆ u32       ┆ f32       ┆ f32        ┆   ┆ ---        ┆ u16    ┆ ---       ┆ u32      │
│            ┆           ┆           ┆            ┆   ┆ i16        ┆        ┆ list[stru ┆          │
│            ┆           ┆           ┆            ┆   ┆            ┆        ┆ ct[3]]    ┆          │
╞════════════╪═══════════╪═══════════╪════════════╪═══╪════════════╪════════╪═══════════╪══════════╡
│ 1748178906 ┆ 981376678 ┆ 22.315142 ┆ 113.92878  ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 334      │
│ 1748178954 ┆ 981376632 ┆ 22.313118 ┆ 113.923676 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 355      │
│ 1748178953 ┆ 981376221 ┆ 22.31551  ┆ 113.929932 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 438      │
│ 1748178957 ┆ 981355789 ┆ 22.315166 ┆ 113.923164 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 495      │
│ 1748178958 ┆ 981375544 ┆ 22.313187 ┆ 113.921371 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 591      │
│ …          ┆ …         ┆ …         ┆ …          ┆ … ┆ …          ┆ …      ┆ …         ┆ …        │
│ 1748178954 ┆ 981325451 ┆ 22.310371 ┆ 113.901993 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 2596     │
│ 1748178953 ┆ 981374338 ┆ 22.299173 ┆ 113.89856  ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 3291     │
│ 1748178957 ┆ 981372281 ┆ 22.297474 ┆ 113.898857 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 3354     │
│ 1748178957 ┆ 981376434 ┆ 22.293045 ┆ 113.970421 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 4961     │
│ 1748178957 ┆ 981339515 ┆ 22.305908 ┆ 113.833893 ┆ … ┆ 0          ┆ 0      ┆ []        ┆ 9629     │
└────────────┴───────────┴───────────┴────────────┴───┴────────────┴────────┴───────────┴──────────┘
# --8<-- [end:polars]
"""
