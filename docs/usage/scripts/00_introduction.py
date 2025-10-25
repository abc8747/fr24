# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
import asyncio
from fr24 import FR24, BoundingBox

bbox = BoundingBox(south=42, north=52, west=-8, east=10)


async def main() -> None:  # (1)!
    async with FR24() as fr24:
        result = await fr24.live_feed.fetch(bbox)  # (2)!
        print(result)
        print(result.to_proto())
        print(result.to_dict())
        print(result.to_polars())


if __name__ == "__main__":
    asyncio.run(main())  # (3)!
# --8<-- [end:script]
# %%
"""
# --8<-- [start:result]
LiveFeedResult(
    request=LiveFeedParams(
        bounding_box=BoundingBox(south=42, north=52, west=-8, east=10),
        stats=False,
        limit=1500,
        maxage=14400,
        fields={'type', 'route', 'flight', 'reg'}
    ),
    response=<Response [200 OK]>,
    timestamp=1753072997,
)
# --8<-- [end:result]
# --8<-- [start:result-proto]
flights_list {
  flightid: 995675586
  lat: 42.0227051
  lon: -2.89851785
  track: 30
  alt: 39975
  speed: 502
  icon: A330
  timestamp: 1753072999
  callsign: "AFR754"
  extra_info {
    flight: "AF754"
    reg: "F-HRBI"
    route {
      from: "BZV"
      to: "CDG"
    }
    type: "B789"
  }
  position_buffer {
    recent_positions_list {
      delta_lat: 201
      delta_lon: 162
      delta_ms: 1030
    }
    recent_positions_list {
      delta_lat: 418
      delta_lon: 340
      delta_ms: 2060
    }
    ...
  }
  timestamp_ms: 1753072998785
}
...
server_time_ms: 1753073001486
# --8<-- [end:result-proto]
# --8<-- [start:result-dict]
{
    "flights_list": [
        {
            "flightid": 995675586,
            "lat": 42.022705,
            "lon": -2.8985178,
            "track": 30,
            "alt": 39975,
            "speed": 502,
            "icon": "A330",
            "timestamp": 1753072999,
            "callsign": "AFR754",
            "extra_info": {
                "flight": "AF754",
                "reg": "F-HRBI",
                "route": {"from": "BZV", "to": "CDG"},
                "type": "B789",
            },
            "position_buffer": {
                "recent_positions_list": [
                    {"delta_lat": 201, "delta_lon": 162, "delta_ms": 1030},
                    {"delta_lat": 418, "delta_lon": 340, "delta_ms": 2060},
                    {"delta_lat": 599, "delta_lon": 480, "delta_ms": 3050},
                    {"delta_lat": 837, "delta_lon": 674, "delta_ms": 4200},
                    {"delta_lat": 1136, "delta_lon": 915, "delta_ms": 5730},
                    {"delta_lat": 1335, "delta_lon": 1075, "delta_ms": 6660},
                    {"delta_lat": 1634, "delta_lon": 1317, "delta_ms": 8200},
                    {"delta_lat": 1835, "delta_lon": 1479, "delta_ms": 9190},
                    {"delta_lat": 2032, "delta_lon": 1635, "delta_ms": 10220},
                ]
            },
            "timestamp_ms": "1753072998785",
        },
        ...
    ],
    "server_time_ms": "1753073001486",
}

# --8<-- [end:result-dict]
# --8<-- [start:result-polars]
shape: (1_383, 18)
┌──────────────┬───────────┬───────────┬───────────┬───┬─────┬────────┬──────────────┬─────────────┐
│ timestamp    ┆ flightid  ┆ latitude  ┆ longitude ┆ … ┆ eta ┆ squawk ┆ vertical_spe ┆ position_bu │
│ ---          ┆ ---       ┆ ---       ┆ ---       ┆   ┆ --- ┆ ---    ┆ ed           ┆ ffer        │
│ datetime[ms, ┆ u32       ┆ f32       ┆ f32       ┆   ┆ u32 ┆ u16    ┆ ---          ┆ ---         │
│ UTC]         ┆           ┆           ┆           ┆   ┆     ┆        ┆ i16          ┆ list[struct │
│              ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ [3]]        │
╞══════════════╪═══════════╪═══════════╪═══════════╪═══╪═════╪════════╪══════════════╪═════════════╡
│ 2025-07-21   ┆ 995675586 ┆ 42.022705 ┆ -2.898518 ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{201,162,1 │
│ 04:43:18.785 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 030}, {418, │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 340,2060…   │
│ 2025-07-21   ┆ 995726866 ┆ 42.01926  ┆ -2.377071 ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{200,89,10 │
│ 04:43:18.908 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 20}, {442,1 │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 98,2180}…   │
│ 2025-07-21   ┆ 995727804 ┆ 42.206726 ┆ 0.818107  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{283,87,13 │
│ 04:43:19.345 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 45}, {489,1 │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 49,2340}…   │
│ 2025-07-21   ┆ 995728695 ┆ 42.044865 ┆ 1.248098  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{188,-59,9 │
│ 04:43:18.930 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 66}, {391,- │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 127,2036…   │
│ 2025-07-21   ┆ 995730200 ┆ 42.262867 ┆ 1.626488  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{181,-153, │
│ 04:43:19.262 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 1125}, {340 │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ ,-285,20…   │
│ …            ┆ …         ┆ …         ┆ …         ┆ … ┆ …   ┆ …      ┆ …            ┆ …           │
│ 2025-07-21   ┆ 995719413 ┆ 51.366852 ┆ 8.458804  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{183,-393, │
│ 04:43:19.591 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 2161}, {274 │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ ,-593,32…   │
│ 2025-07-21   ┆ 995728483 ┆ 51.609512 ┆ 9.095863  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{91,-295,9 │
│ 04:43:18.941 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 70}, {184,- │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 608,1970…   │
│ 2025-07-21   ┆ 995730833 ┆ 51.500927 ┆ 9.861908  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{-4,-274,1 │
│ 04:43:18.857 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 090}, {-9,- │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 419,1680…   │
│ 2025-07-21   ┆ 995729878 ┆ 51.558651 ┆ 9.883041  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{-59,-264, │
│ 04:43:19.168 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 960}, {-146 │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ ,-643,23…   │
│ 2025-07-21   ┆ 995730144 ┆ 50.797848 ┆ 9.983597  ┆ … ┆ 0   ┆ 0      ┆ 0            ┆ [{173,459,1 │
│ 04:43:19.392 ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 455}, {297, │
│ UTC          ┆           ┆           ┆           ┆   ┆     ┆        ┆              ┆ 793,2496…   │
└──────────────┴───────────┴───────────┴───────────┴───┴─────┴────────┴──────────────┴─────────────┘
# --8<-- [end:result-polars]
"""
# %%
# --8<-- [start:script-1]
from fr24 import FR24


async def my_feed() -> None:
    async with FR24() as fr24:
        ...


# --8<-- [end:script-1]
# %%
# --8<-- [start:login]
from fr24 import FR24


async def main() -> None:
    async with FR24() as fr24:
        # anonymous now
        await fr24.login()  # reads from environment or configuration file, or,
        await fr24.login(creds={"username": "...", "password": "..."})  # or,
        await fr24.login(creds={"subscriptionKey": "...", "token": "..."})


# --8<-- [end:login]
# %%
# --8<-- [start:client-sharing]
import httpx

from fr24 import FR24

client = httpx.AsyncClient(
    http1=False, http2=True, transport=httpx.AsyncHTTPTransport(retries=5)
)


async def main() -> None:
    async with FR24(client) as fr24:
        ...


# --8<-- [end:client-sharing]
# %%
# --8<-- [start:script-2]
from fr24 import FR24, BBOX_FRANCE_UIR


async def my_feed() -> None:
    async with FR24() as fr24:
        result = await fr24.live_feed.fetch(BBOX_FRANCE_UIR)
        print(result.response.content)


# --8<-- [end:script-2]

# %%
"""
# --8<-- [start:result-response-content]
b'...truncated
\x84\x02(\xa2\x160m8\x03@\x00H\xfc\xc1\xac\xbe\x06P\x00Z\x05DEGLC`\x00j\x1c\n\x00\x12\x06D-EGLC\x1a\n\n\x03KSF\x12
\x03EIB"\x04C172r6\n\x19\x08\xd3\xff\xff\xff\xff\xff\xff\xff\xff\x01\x10\xa5\xfc\xff\xff\xff\xff\xff\xff\xff\x01\x18
\x8f%\n\x19\x08\xc4\xff\xff\xff\xff\xff\xff\xff\xff\x01\x10\xbd\xfb\xff\xff\xff\xff\xff\xff\xff\x01\x18\xb42x\xf5
\xb0\xe3\x8b\xd72\n\x96\x01\x08\xd4\xa6\x8d\xcb\x03\x15\xb0$OB\x1dp\x0e\x1fA 
\x12(\xbar0\xf3\x028\x05@\x00H\xfe\xc1\xac\xbe\x06P\x00Z\x06ECA4RT`\x00j\x1c\n\x00\x12\x06D-CFRT\x1a\n\n\x03FMM\x12
\x03HAJ"\x04C25CrA\n\x08\x08\xa2\x01\x10S\x18\x86\x08\n\t\x08\x8b\x03\x10\xcd\x01\x18\xa0\x10\n\t\x08\xd1\x05\x10
\xf5\x02\x18\x8c!\n\t\x08\xf9\x06\x10\xd1\x03\x18\xac*\n\t\x08\xb7\n\x10\xbc\x05\x18\x8c=\n\t\x08\xed\x0b\x10\xa1\x06
\x18\x9fEx\xf0\xc4\xe3\x8b\xd72\nN\x08\x80\xd3\x8c\xcb\x03\x15\x88\xa5OB\x1dO\xd6\x19A 
\xf2\x01(\x96\x1a0\n8\x03@\x00H\xfe\xc1\xac\xbe\x06P\x00Z\x05DEGZZ`\x01j\x16\n\x00\x12\x06D-EGZZ\x1a\x04\n\x00\x12
\x00"\x04DA40r\x00x\xc4\xc1\xe3\x8b\xd72\n\x9c\x01\x08\x8f\x94\x8d\xcb\x03\x15\xfb\xb2OB\x1d\xeeL\x1fA 
\n(\xa1Y0\xd6\x028\x07@\x00H\xff\xc1\xac\xbe\x06P\x00Z\x07AFR87MJ`\x00j"\n\x06AF1838\x12\x06F-HBXE\x1a\n\n\x03CDG
\x12\x03HAJ"\x04E170r@\n\x08\x08\xdc\x01\x10<\x18\xa2\x08\n\x08\x08\xf9\x02\x10f\x18\xb7\x12\n\t\x08\xed\x05\x10\xd3
\x01\x18\x82&\n\t\x08\x9e\x07\x10\x8a\x02\x18\xbd.\n\t\x08\xb9\x08\x10\xb8\x02\x18\xa76\n\t\x08\xb5\x0b\x10\xa3\x03
\x18\xa1Gx\xb4\xcb\xe3\x8b\xd72 \x92\xe1\xe3\x8b\xd72\x80\x00\x00\x00\x0fgrpc-status:0\r\n'
# --8<-- [end:result-response-content]
"""
# %%
# --8<-- [start:script-3]
import asyncio
from fr24 import FR24, BBOX_FRANCE_UIR


async def main() -> None:
    async with FR24() as fr24:
        result = await fr24.live_feed.fetch(BBOX_FRANCE_UIR)
        print(result.to_proto())
        print(result.to_dict())
        print(result.to_polars())


# --8<-- [end:script-3]
# %%
# --8<-- [start:script-4]
import asyncio
import json
from fr24 import FR24, BBOX_FRANCE_UIR


async def main() -> None:
    async with FR24() as fr24:
        result = await fr24.live_feed.fetch(BBOX_FRANCE_UIR)
        with open("path/to/some/file.json", "w") as f:
            json.dump(result.to_dict(), f, indent=4)


# --8<-- [end:script-4]
# %%
# --8<-- [start:script-5]
import asyncio
from io import BytesIO
from fr24 import FR24, BBOX_FRANCE_UIR


async def main() -> None:
    async with FR24() as fr24:
        result = await fr24.live_feed.fetch(BBOX_FRANCE_UIR)
        result.write_table("path/to/some/file.parquet")  # (1)!
        result.write_table("path/to/some/file.csv", format="csv")  # (2)!

        buffer = BytesIO()
        result.write_table(buffer, format="parquet")
        buffer.seek(0)


# --8<-- [end:script-5]
# %%
# --8<-- [start:script-6]
import asyncio
from fr24 import FR24, FR24Cache, BBOX_FRANCE_UIR

cache = FR24Cache("path/to/some/directory/")
# alternatively, use the default cache directory:
cache = FR24Cache.default()  # (1)!


async def main() -> None:
    async with FR24() as fr24:
        result = await fr24.live_feed.fetch(BBOX_FRANCE_UIR)
        result.write_table(cache)


# --8<-- [end:script-6]
# %%
# --8<-- [start:script-7]
from fr24 import FR24Cache

cache = FR24Cache.default()

for fp in cache.live_feed.glob("*"):
    print(fp)
    lf = fp.scan_table()
    print(lf.collect())

# alternatively, scan one file:
lf = cache.live_feed.scan_table(timestamp=1733036597)
# --8<-- [end:script-7]
# %%
"""
# --8<-- [start:output-7]
/home/user/.cache/fr24/feed/1733036597.parquet
# --8<-- [end:output-7]
"""
# %%
