# ruff: noqa
# fmt: off
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
from fr24 import FR24, FR24Cache

async def get_farthest_flight_id(fr24: FR24) -> int:
    nearest_result = await fr24.nearest_flights.fetch(
        lat=22.31257, lon=113.92708, radius=10000, limit=1500
    )
    return nearest_result.to_proto().flights_list[-1].flight.flightid

async def my_flight_details() -> None:
    async with FR24() as fr24:
        flight_id = await get_farthest_flight_id(fr24)
        result = await fr24.flight_details.fetch(flight_id=flight_id)
        print(result)
        print(result.to_dict())
        print(result.to_polars())
        result.write_table(FR24Cache.default())

await my_flight_details()
# --8<-- [end:script]

# %%
"""
# --8<-- [start:result]
FlightDetailsResult(
    request=FlightDetailsParams(flight_id=1011852915, restriction_mode=0, verbose=True),
    response=<Response [200 OK]>,
    timestamp=1758466410
)
# --8<-- [end:result]
# --8<-- [start:dict]
{
    "aircraft_info": {
        "icao_address": 7864687,
        "reg": "B-HNG",
        "type": "B773",
        "icon": "B777",
        "full_description": "Boeing 777-367",
        "images_list": [
            {
                "url": "https://www.jetphotos.com/photo/11821124",
                "copyright": "kuzuma",
                "thumbnail": "https://cdn.jetphotos.com/200/5/505864_1756100441_tb.jpg",
                "medium": "https://cdn.jetphotos.com/400/5/505864_1756100441.jpg",
                "large": "https://cdn.jetphotos.com/640/5/505864_1756100441.jpg",
            },
            {
                "url": "https://www.jetphotos.com/photo/11808578",
                "copyright": "tobiashsu1217_spotter",
                "thumbnail": "https://cdn.jetphotos.com/200/6/1544325_1755012630_tb.jpg",
                "medium": "https://cdn.jetphotos.com/400/6/1544325_1755012630.jpg",
                "large": "https://cdn.jetphotos.com/640/6/1544325_1755012630.jpg",
            },
            {
                "url": "https://www.jetphotos.com/photo/11804947",
                "copyright": "Stanley Joe Hidayat",
                "thumbnail": "https://cdn.jetphotos.com/200/5/389644_1754704150_tb.jpg",
                "medium": "https://cdn.jetphotos.com/400/5/389644_1754704150.jpg",
                "large": "https://cdn.jetphotos.com/640/5/389644_1754704150.jpg",
            },
        ],
        "msn_available": True,
        "age_available": True,
        "registered_owners": "Cathay Pacific",
        "is_country_of_reg_available": True,
    },
    "schedule_info": {
        "flight_number": "CX902",
        "operated_by_id": 57,
        "painted_as_id": 57,
        "origin_id": 2266,
        "destination_id": 1366,
        "scheduled_departure": 1758457200,
        "scheduled_arrival": 1758466500,
        "actual_departure": 1758460310,
        "arr_terminal": "1",
        "baggage_belt": "10",
    },
    "flight_progress": {
        "traversed_distance": 1146491,
        "remaining_distance": 3113,
        "elapsed_time": 6100,
        "remaining_time": 29,
        "eta": 1758466439,
        "great_circle_distance": 1143502,
        "mean_flight_time": 5846,
        "flight_stage": "AIRBORNE",
        "delay_status": "GREEN",
        "progress_pct": 99,
    },
    "flight_info": {
        "flightid": 1011852915,
        "lat": 22.324324,
        "lon": 113.89048,
        "track": 70,
        "speed": 120,
        "timestamp_ms": "1758466407324",
        "callsign": "CPA902",
        "ems_availability": {
            "qnh_availability": True,
            "amcp_availability": True,
            "oat_availability": True,
            "ias_availability": True,
            "tas_availability": True,
            "mach_availability": True,
            "agps_availability": True,
            "agpsdiff_availability": True,
            "wind_dir_availability": True,
            "wind_speed_availability": True,
        },
        "squawk_availability": True,
        "airspace_availability": True,
        "server_time_ms": "1758466410387",
    },
    "flight_plan": {},
    "flight_trail_list": [
        {
            "snapshot_id": "1758458895",
            "lat": 14.517563,
            "lon": 121.01436,
            "spd": 1,
            "heading": 101,
        },
        ...
        {
            "snapshot_id": "1758466399",
            "lat": 22.322754,
            "lon": 113.88553,
            "altitude": 100,
            "spd": 141,
            "heading": 70,
        },
    ],
    "position_buffer": {
        "recent_positions_list": [
            {"delta_lat": 43, "delta_lon": 131, "delta_ms": 2079},
            {"delta_lat": 94, "delta_lon": 294, "delta_ms": 4660},
            {"delta_lat": 112, "delta_lon": 350, "delta_ms": 5589},
            {"delta_lat": 156, "delta_lon": 495, "delta_ms": 7660},
            {"delta_lat": 196, "delta_lon": 614, "delta_ms": 9579},
            {"delta_lat": 234, "delta_lon": 721, "delta_ms": 11019},
        ]
    },
}
# --8<-- [end:dict]
# --8<-- [start:polars]
shape: (1, 32)
┌─────────────┬───────┬──────────┬─────────────┬───┬────────┬────────────┬────────────┬────────────┐
│ icao_addres ┆ reg   ┆ typecode ┆ flight_numb ┆ … ┆ squawk ┆ ems        ┆ flight_tra ┆ position_b │
│ s           ┆ ---   ┆ ---      ┆ er          ┆   ┆ ---    ┆ ---        ┆ il_list    ┆ uffer      │
│ ---         ┆ str   ┆ str      ┆ ---         ┆   ┆ u16    ┆ struct[13] ┆ ---        ┆ ---        │
│ u32         ┆       ┆          ┆ str         ┆   ┆        ┆            ┆ list[struc ┆ list[struc │
│             ┆       ┆          ┆             ┆   ┆        ┆            ┆ t[8]]      ┆ t[3]]      │
╞═════════════╪═══════╪══════════╪═════════════╪═══╪════════╪════════════╪════════════╪════════════╡
│ 7864687     ┆ B-HNG ┆ B773     ┆ CX902       ┆ … ┆ 0      ┆ {0,0,0,0,0 ┆ [{17584588 ┆ [{43,131,2 │
│             ┆       ┆          ┆             ┆   ┆        ┆ ,0,0,0,0,0 ┆ 95,14.5175 ┆ 079}, {94, │
│             ┆       ┆          ┆             ┆   ┆        ┆ ,0,0,0}    ┆ 63,121.014 ┆ 294,4660}, │
│             ┆       ┆          ┆             ┆   ┆        ┆            ┆ …          ┆ …          │
└─────────────┴───────┴──────────┴─────────────┴───┴────────┴────────────┴────────────┴────────────┘
# --8<-- [end:polars]
"""
