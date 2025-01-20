# ruff: noqa
# fmt: off
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
from fr24 import FR24

async def my_feed() -> None:
    async with FR24() as fr24:
        result = await fr24.live_feed.fetch()
        data = result.to_dict()
        df = result.to_polars()
        result.save()

await my_feed()
# --8<-- [end:script]
# %%
# --8<-- [start:script2]
from fr24 import FR24

async def my_feed() -> None:
    async with FR24() as fr24:
        datac = fr24.live_feed.load(1733036597)

await my_feed()
# --8<-- [end:script2]
# %%
"""
# --8<-- [start:result]
LiveFeedResult(
    request=LiveFeedParams(
        bounding_box=BoundingBox(south=42, north=52, west=-8, east=10),
        stats=False,
        limit=1500,
        maxage=14400,
        fields={'reg', 'flight', 'type', 'route'}
    ),
    response=<Response [200 OK]>,
    base_dir=PosixPath('/home/user/.cache/fr24'),
    timestamp=1737360998
)
# --8<-- [end:result]
# --8<-- [start:data]
{
    'flightsList': [
        {
            'flightid': 952888097,
            'lat': 42.467102,
            'lon': -6.0266876,
            'track': 210,
            'alt': 39000,
            'speed': 437,
            'timestamp': 1737360996,
            'callsign': 'TVF96CL',
            'extraInfo': {
                'flight': 'TO3080',
                'reg': 'F-HTVR',
                'route': {'from': 'ORY', 'to': 'VIL'},
                'type': 'B738'
            },
            'positionBuffer': {
                'recentPositionsList': [
                    {'deltaLat': -306, 'deltaLon': -241, 'deltaMs': 2100},
                    {'deltaLat': -566, 'deltaLon': -445, 'deltaMs': 3110},
                    {'deltaLat': -732, 'deltaLon': -574, 'deltaMs': 4260},
                    {'deltaLat': -897, 'deltaLon': -707, 'deltaMs': 5280},
                    {'deltaLat': -1055, 'deltaLon': -828, 'deltaMs': 6470},
                    {'deltaLat': -1297, 'deltaLon': -1020, 'deltaMs': 7470},
                    {'deltaLat': -1493, 'deltaLon': -1173, 'deltaMs': 8570},
                    {'deltaLat': -1657, 'deltaLon': -1304, 'deltaMs': 9801}
                ]
            }
        },
        {
            'flightid': 952890068,
            'lat': 42.7418,
            'lon': -5.856479,
            'track': 276,
            'alt': 41750,
            'speed': 449,
            'icon': 'LJ60',
            'timestamp': 1737360995,
            'callsign': 'QQE210',
            'extraInfo': {
                'flight': 'QE210',
                'reg': 'A7-CGC',
                'route': {'from': 'BCN', 'to': 'IAD'},
                'type': 'GLF6'
            },
            'positionBuffer': {
                'recentPositionsList': [
                    {'deltaLat': 22, 'deltaLon': -276, 'deltaMs': 1106},
                    {'deltaLat': 46, 'deltaLon': -562, 'deltaMs': 2187},
                    {'deltaLat': 67, 'deltaLon': -838, 'deltaMs': 3189},
                    {'deltaLat': 95, 'deltaLon': -1175, 'deltaMs': 4369},
                    {'deltaLat': 130, 'deltaLon': -1564, 'deltaMs': 5481},
                    {'deltaLat': 158, 'deltaLon': -1903, 'deltaMs': 6522},
                    {'deltaLat': 177, 'deltaLon': -2126, 'deltaMs': 7540},
                    {'deltaLat': 200, 'deltaLon': -2404, 'deltaMs': 8565}
                ]
            }
        },
    ]
    'serverTimeMs': '1737360998825'
}
# --8<-- [end:data]
# --8<-- [start:df]
shape: (899, 18)
┌────────────┬───────────┬───────────┬───────────┬───┬─────┬───────────────┬────────┬──────────────┐
│ timestamp  ┆ flightid  ┆ latitude  ┆ longitude ┆ … ┆ eta ┆ vertical_spee ┆ squawk ┆ position_buf │
│ ---        ┆ ---       ┆ ---       ┆ ---       ┆   ┆ --- ┆ d             ┆ ---    ┆ fer          │
│ u32        ┆ u32       ┆ f32       ┆ f32       ┆   ┆ u32 ┆ ---           ┆ u16    ┆ ---          │
│            ┆           ┆           ┆           ┆   ┆     ┆ i16           ┆        ┆ list[struct[ │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 3]]          │
╞════════════╪═══════════╪═══════════╪═══════════╪═══╪═════╪═══════════════╪════════╪══════════════╡
│ 1737360996 ┆ 952888097 ┆ 42.467102 ┆ -6.026688 ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{-306,-241, │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 2100},       │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ {-566,-445,… │
│ 1737360995 ┆ 952890068 ┆ 42.741798 ┆ -5.856479 ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{22,-276,11 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 06}, {46,-56 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 2,2187…      │
│ 1737360995 ┆ 952889599 ┆ 43.295025 ┆ -5.364467 ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{-279,-228, │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 1120},       │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ {-374,-307,… │
│ 1737360996 ┆ 952886169 ┆ 42.944916 ┆ -5.611012 ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{-256,-210, │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 1004},       │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ {-445,-366,… │
│ 1737360996 ┆ 952881151 ┆ 43.920135 ┆ -7.713935 ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{210,178,13 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 66}, {379,32 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 5,2442…      │
│ …          ┆ …         ┆ …         ┆ …         ┆ … ┆ …   ┆ …             ┆ …      ┆ …            │
│ 1737360996 ┆ 952890387 ┆ 51.8517   ┆ 8.181763  ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{-170,-208, │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 2208},       │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ {-312,-386,… │
│ 1737360995 ┆ 952894571 ┆ 51.961933 ┆ 8.233468  ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{58,257,101 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 5}, {127,577 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ ,2055}…      │
│ 1737360995 ┆ 952889383 ┆ 51.81115  ┆ 9.978867  ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{-14,283,11 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 35}, {-32,57 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 2,2170…      │
│ 1737360996 ┆ 952883520 ┆ 51.52737  ┆ 9.759674  ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{400,68,204 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 0}, {597,99, │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 3163},…      │
│ 1737360995 ┆ 952894664 ┆ 51.909981 ┆ 9.415519  ┆ … ┆ 0   ┆ 0             ┆ 0      ┆ [{-167,-31,1 │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ 009}, {-409, │
│            ┆           ┆           ┆           ┆   ┆     ┆               ┆        ┆ -78,20…      │
└────────────┴───────────┴───────────┴───────────┴───┴─────┴───────────────┴────────┴──────────────┘
# --8<-- [end:df]
"""
