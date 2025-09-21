# ruff: noqa
# fmt: off
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import follow_flight_stream
from fr24.proto.v1_pb2 import FollowFlightRequest, FollowFlightResponse
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def follow_flight_data() -> None:
    timeout = httpx.Timeout(5, read=120)
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient(timeout=timeout) as client:
        message = FollowFlightRequest(flight_id=0x3c500fdb)
        i = 0
        async for response in follow_flight_stream(client, message, headers):
            print(f"##### {i} #####")
            print(parse_data(response, FollowFlightResponse))
            i += 1
            if i > 3:
                break


await follow_flight_data()
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:output0]
##### 0 #####
Ok(_value=aircraft_info {
  icao_address: 7866977
  reg: "B-KQM"
  type: "B77W"
  icon: B777
  full_description: "Boeing 777-367(ER)"
  images_list {
    url: "https://www.jetphotos.com/photo/11825817"
    copyright: "ZSHC_Linzx"
    thumbnail: "https://cdn.jetphotos.com/200/5/1291679_1756473618_tb.jpg"
    medium: "https://cdn.jetphotos.com/400/5/1291679_1756473618.jpg"
    large: "https://cdn.jetphotos.com/640/5/1291679_1756473618.jpg"
  }
  images_list {
    url: "https://www.jetphotos.com/photo/11813969"
    copyright: "CAN-Eric"
    thumbnail: "https://cdn.jetphotos.com/200/5/967682_1755532162_tb.jpg"
    medium: "https://cdn.jetphotos.com/400/5/967682_1755532162.jpg"
    large: "https://cdn.jetphotos.com/640/5/967682_1755532162.jpg"
  }
  images_list {
    url: "https://www.jetphotos.com/photo/11803561"
    copyright: "cc12214"
    thumbnail: "https://cdn.jetphotos.com/200/6/585221_1754572527_tb.jpg"
    medium: "https://cdn.jetphotos.com/400/6/585221_1754572527.jpg"
    large: "https://cdn.jetphotos.com/640/6/585221_1754572527.jpg"
  }
  msn_available: true
  age_available: true
  registered_owners: "Cathay Pacific (Oneworld Livery)"
  is_country_of_reg_available: true
}
schedule_info {
  flight_number: "CX251"
  operated_by_id: 57
  painted_as_id: 57
  origin_id: 1366
  destination_id: 1942
  scheduled_departure: 1758465600
  scheduled_arrival: 1758516000
  actual_departure: 1758466901
  arr_terminal: "3"
}
flight_progress {
  traversed_distance: 21783
  remaining_distance: 9668300
  elapsed_time: 295
  remaining_time: 51569
  eta: 1758518765
  great_circle_distance: 9647791
  mean_flight_time: 48161
  flight_stage: ASCENDING
  delay_status: RED
}
flight_info {
  flightid: 1011879899
  lat: 22.1949
  lon: 114.087921
  track: 169
  alt: 7525
  speed: 303
  timestamp_ms: 1758467194561
  callsign: "CPA251"
  ems_availability {
    qnh_availability: true
    amcp_availability: true
    oat_availability: true
    ias_availability: true
    tas_availability: true
    mach_availability: true
    agps_availability: true
    agpsdiff_availability: true
    wind_dir_availability: true
    wind_speed_availability: true
    rs_availability: true
  }
  squawk_availability: true
  vspeed_availability: true
  airspace_availability: true
  server_time_ms: 1758467196527
}
flight_trail_list {
  snapshot_id: 1758465991
  lat: 22.3132782
  lon: 113.934616
  heading: 70
}
flight_trail_list {
  snapshot_id: 1758466089
  lat: 22.3131981
  lon: 113.934303
  spd: 2
  heading: 70
}
...
flight_trail_list {
  snapshot_id: 1758467188
  lat: 22.2043304
  lon: 114.086678
  altitude: 7450
  spd: 300
  heading: 179
}
position_buffer {
  recent_positions_list {
    delta_lat: -155
    delta_lon: 34
    delta_ms: 1090
  }
  recent_positions_list {
    delta_lat: -517
    delta_lon: 94
    delta_ms: 3710
  }
  recent_positions_list {
    delta_lat: -746
    delta_lon: 119
    delta_ms: 5270
  }
  recent_positions_list {
    delta_lat: -942
    delta_lon: 124
    delta_ms: 6700
  }
  recent_positions_list {
    delta_lat: -1107
    delta_lon: 129
    delta_ms: 7870
  }
  recent_positions_list {
    delta_lat: -1364
    delta_lon: 129
    delta_ms: 9710
  }
  recent_positions_list {
    delta_lat: -1597
    delta_lon: 129
    delta_ms: 11380
  }
}
)
##### 1 #####
Ok(_value=schedule_info {
  flight_number: "CX251"
  operated_by_id: 57
  painted_as_id: 57
  origin_id: 1366
  destination_id: 1942
  scheduled_departure: 1758465600
  scheduled_arrival: 1758516000
  actual_departure: 1758466901
  arr_terminal: "3"
}
flight_progress {
  traversed_distance: 21940
  remaining_distance: 9668494
  elapsed_time: 298
  remaining_time: 51566
  eta: 1758518765
  great_circle_distance: 9647791
  mean_flight_time: 48161
  flight_stage: ASCENDING
  delay_status: RED
}
flight_info {
  flightid: 1011879899
  lat: 22.1930809
  lon: 114.088387
  track: 167
  alt: 7550
  speed: 303
  timestamp_ms: 1758467195921
  callsign: "CPA251"
  ems_availability {
    qnh_availability: true
    amcp_availability: true
    oat_availability: true
    ias_availability: true
    tas_availability: true
    mach_availability: true
    agps_availability: true
    agpsdiff_availability: true
    wind_dir_availability: true
    wind_speed_availability: true
    rs_availability: true
  }
  squawk_availability: true
  vspeed_availability: true
  airspace_availability: true
  server_time_ms: 1758467199530
}
)
##### 2 #####
Ok(_value=schedule_info {
  flight_number: "CX251"
  operated_by_id: 57
  painted_as_id: 57
  origin_id: 1366
  destination_id: 1942
  scheduled_departure: 1758465600
  scheduled_arrival: 1758516000
  actual_departure: 1758466901
  arr_terminal: "3"
}
flight_progress {
  traversed_distance: 22437
  remaining_distance: 9669070
  elapsed_time: 301
  remaining_time: 51563
  eta: 1758518765
  great_circle_distance: 9647791
  mean_flight_time: 48161
  flight_stage: ASCENDING
  delay_status: RED
}
flight_info {
  flightid: 1011879899
  lat: 22.1880341
  lon: 114.09037
  track: 158
  alt: 7600
  speed: 305
  timestamp_ms: 1758467199681
  callsign: "CPA251"
  ems_availability {
    qnh_availability: true
    amcp_availability: true
    oat_availability: true
    ias_availability: true
    tas_availability: true
    mach_availability: true
    agps_availability: true
    agpsdiff_availability: true
    wind_dir_availability: true
    wind_speed_availability: true
    rs_availability: true
  }
  squawk_availability: true
  vspeed_availability: true
  airspace_availability: true
  server_time_ms: 1758467202532
}
)
##### 3 #####
Ok(_value=schedule_info {
  flight_number: "CX251"
  operated_by_id: 57
  painted_as_id: 57
  origin_id: 1366
  destination_id: 1942
  scheduled_departure: 1758465600
  scheduled_arrival: 1758516000
  actual_departure: 1758466901
  arr_terminal: "3"
}
flight_progress {
  traversed_distance: 22657
  remaining_distance: 9669316
  elapsed_time: 304
  remaining_time: 51560
  eta: 1758518765
  great_circle_distance: 9647791
  mean_flight_time: 48161
  flight_stage: ASCENDING
  delay_status: RED
}
flight_info {
  flightid: 1011879899
  lat: 22.1859741
  lon: 114.09137
  track: 154
  alt: 7625
  speed: 305
  timestamp_ms: 1758467201271
  callsign: "CPA251"
  ems_availability {
    qnh_availability: true
    amcp_availability: true
    oat_availability: true
    ias_availability: true
    tas_availability: true
    mach_availability: true
    agps_availability: true
    agpsdiff_availability: true
    wind_dir_availability: true
    wind_speed_availability: true
    rs_availability: true
  }
  squawk_availability: true
  vspeed_availability: true
  airspace_availability: true
  server_time_ms: 1758467205534
}
)
# --8<-- [end:output0]
"""
