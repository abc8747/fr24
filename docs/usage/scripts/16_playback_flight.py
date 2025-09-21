# ruff: noqa
# fmt: off
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
from fr24 import FR24, FR24Cache
import polars as pl


async def get_last_flight(fr24: FR24, *, reg: str = "B-LRA") -> tuple[int, int]:
    flight_list_result = await fr24.flight_list.fetch(reg=reg)
    df = flight_list_result.to_polars()

    landed = df.filter(pl.col("status").str.starts_with("Landed"))
    assert landed.height > 0, "no landed flights found"

    flight_id = landed[0, "flight_id"]
    stod = int(landed[0, "ATOD"].timestamp())
    return flight_id, stod


async def my_playback_flight() -> None:
    async with FR24() as fr24:
        flight_id, timestamp = await get_last_flight(fr24)
        result = await fr24.playback_flight.fetch(
            flight_id=flight_id, timestamp=timestamp
        )
        print(result)
        print(result.to_dict())
        print(result.to_polars())
        result.write_table(FR24Cache.default())


await my_playback_flight()
# --8<-- [end:script]

# %%
"""
# --8<-- [start:result]
PlaybackFlightResult(
    request=PlaybackFlightParams(flight_id=1011667820, timestamp=1758386815),
    response=<Response [200 OK]>
)
# --8<-- [end:result]
# --8<-- [start:dict]
{
    "aircraft_info": {
        "icao_address": 7867035,
        "reg": "B-LRA",
        "type": "A359",
        "icon": "A330",
        "full_description": "Airbus A350-941",
        "images_list": [
            {
                "url": "https://www.jetphotos.com/photo/11806625",
                "copyright": "EthanLi",
                "thumbnail": "https://cdn.jetphotos.com/200/5/682006_1754851444_tb.jpg",
                "medium": "https://cdn.jetphotos.com/400/5/682006_1754851444.jpg",
                "large": "https://cdn.jetphotos.com/640/5/682006_1754851444.jpg",
            },
            {
                "url": "https://www.jetphotos.com/photo/11728089",
                "copyright": "Hypocrite",
                "thumbnail": "https://cdn.jetphotos.com/200/6/1954570_1747460006_tb.jpg",
                "medium": "https://cdn.jetphotos.com/400/6/1954570_1747460006.jpg",
                "large": "https://cdn.jetphotos.com/640/6/1954570_1747460006.jpg",
            },
            {
                "url": "https://www.jetphotos.com/photo/11721357",
                "copyright": "Steven-lzy",
                "thumbnail": "https://cdn.jetphotos.com/200/5/778073_1746782825_tb.jpg",
                "medium": "https://cdn.jetphotos.com/400/5/778073_1746782825.jpg",
                "large": "https://cdn.jetphotos.com/640/5/778073_1746782825.jpg",
            },
        ],
        "msn_available": True,
        "age_available": True,
        "registered_owners": "Cathay Pacific",
        "is_country_of_reg_available": True,
    },
    "schedule_info": {
        "flight_number": "CX170",
        "operated_by_id": 57,
        "painted_as_id": 57,
        "origin_id": 2730,
        "destination_id": 1366,
        "scheduled_departure": 1758384600,
        "scheduled_arrival": 1758412500,
        "actual_departure": 1758386815,
        "actual_arrival": 1758414073,
        "arr_terminal": "1",
        "baggage_belt": "14",
    },
    "flight_info": {
        "flightid": 1011667820,
        "lat": -31.94989,
        "lon": 115.962234,
        "track": 194,
        "speed": 168,
        "timestamp_ms": "1758386809081",
        "callsign": "CPA170",
        "ems_availability": {
            "qnh_availability": True,
            "amcp_availability": True,
            "mach_availability": True,
            "agps_availability": True,
            "agpsdiff_availability": True,
            "rs_availability": True,
        },
        "squawk_availability": True,
        "vspeed_availability": True,
        "airspace_availability": True,
        "server_time_ms": "1758466605103",
    },
    "flight_trail_list": [
        {
            "snapshot_id": "1758385543",
            "lat": -31.94054,
            "lon": 115.973206,
            "heading": 151,
        },
        ...
        {
            "snapshot_id": "1758415950",
            "lat": 22.31186,
            "lon": 113.92748,
            "spd": 1,
            "heading": 295,
        },
    ],
}
# --8<-- [end:dict]
# --8<-- [start:polars]
shape: (1, 24)
┌─────────────┬───────┬──────────┬─────────────┬───┬──────────┬────────┬─────────────┬─────────────┐
│ icao_addres ┆ reg   ┆ typecode ┆ flight_numb ┆ … ┆ callsign ┆ squawk ┆ ems         ┆ flight_trai │
│ s           ┆ ---   ┆ ---      ┆ er          ┆   ┆ ---      ┆ ---    ┆ ---         ┆ l_list      │
│ ---         ┆ str   ┆ str      ┆ ---         ┆   ┆ str      ┆ u16    ┆ struct[13]  ┆ ---         │
│ u32         ┆       ┆          ┆ str         ┆   ┆          ┆        ┆             ┆ list[struct │
│             ┆       ┆          ┆             ┆   ┆          ┆        ┆             ┆ [7]]        │
╞═════════════╪═══════╪══════════╪═════════════╪═══╪══════════╪════════╪═════════════╪═════════════╡
│ 7867035     ┆ B-LRA ┆ A359     ┆ CX758       ┆ … ┆ CPA758   ┆ 0      ┆ {0,0,0,0,0, ┆ [{174815111 │
│             ┆       ┆          ┆             ┆   ┆          ┆        ┆ 0,0,0,0,0,0 ┆ 3,1.341973, │
│             ┆       ┆          ┆             ┆   ┆          ┆        ┆ ,0,0}       ┆ 103.9865…   │
└─────────────┴───────┴──────────┴─────────────┴───┴──────────┴────────┴─────────────┴─────────────┘
# --8<-- [end:polars]
"""
