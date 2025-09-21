# ruff: noqa
# fmt: off
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script]
import httpx

from fr24 import FR24
from fr24.proto.v1_pb2 import NearestFlightsResponse

async def get_nearest_flights(fr24: FR24) -> NearestFlightsResponse:
    nearest_result = await fr24.nearest_flights.fetch(
        lat=22.31257, lon=113.92708, radius=10000, limit=1500
    )
    return nearest_result.to_proto()

async def my_follow_flight() -> None:
    timeout = httpx.Timeout(5, read=120)
    async with FR24(client=httpx.AsyncClient(timeout=timeout)) as fr24:
        nearest_flights_result = await get_nearest_flights(fr24)
        flight_id = nearest_flights_result.flights_list[0].flight.flightid
        i = 0
        async for result in fr24.follow_flight.stream(flight_id=flight_id):
            print(f"##### {i} #####")
            print(result.to_proto())
            i += 1
            if i > 2:
                break

await my_follow_flight()
# --8<-- [end:script]
# fmt: off
# %%
"""
# --8<-- [start:proto]
##### 0 #####
aircraft_info {
  icao_address: 7701252
  reg: "RP-C9903"
  type: "A321"
  icon: A320
  full_description: "Airbus A321-231"
  images_list {
    url: "https://www.jetphotos.com/photo/11825012"
    copyright: "yajoo"
    thumbnail: "https://cdn.jetphotos.com/200/5/2378185_1756401937_tb.jpg"
    medium: "https://cdn.jetphotos.com/400/5/2378185_1756401937.jpg"
    large: "https://cdn.jetphotos.com/640/5/2378185_1756401937.jpg"
  }
  images_list {
    url: "https://www.jetphotos.com/photo/11813525"
    copyright: "Landing HKG"
    thumbnail: "https://cdn.jetphotos.com/200/6/522343_1755503883_tb.jpg"
    medium: "https://cdn.jetphotos.com/400/6/522343_1755503883.jpg"
    large: "https://cdn.jetphotos.com/640/6/522343_1755503883.jpg"
  }
  images_list {
    url: "https://www.jetphotos.com/photo/11745327"
    copyright: "saTrL"
    thumbnail: "https://cdn.jetphotos.com/200/5/630999_1749204666_tb.jpg"
    medium: "https://cdn.jetphotos.com/400/5/630999_1749204666.jpg"
    large: "https://cdn.jetphotos.com/640/5/630999_1749204666.jpg"
  }
  msn_available: true
  age_available: true
  registered_owners: "Philippine Airlines"
  is_country_of_reg_available: true
}
schedule_info {
  flight_number: "PR311"
  operated_by_id: 98
  painted_as_id: 98
  origin_id: 1366
  destination_id: 2266
  scheduled_departure: 1758466800
  scheduled_arrival: 1758475200
  arr_terminal: "1"
}
flight_progress {
  traversed_distance: 657
  remaining_distance: 1143081
  great_circle_distance: 1143502
  mean_flight_time: 5886
  flight_stage: ON_GROUND
}
flight_info {
  flightid: 1011880908
  lat: 22.3098583
  lon: 113.922615
  track: 160
  speed: 8
  timestamp_ms: 1758466956660
  on_ground: true
  callsign: "PAL311"
  ems_availability {
    rs_availability: true
  }
  squawk_availability: true
  airspace_availability: true
  server_time_ms: 1758466960115
}
flight_trail_list {
  snapshot_id: 1758466272
  lat: 22.3157578
  lon: 113.932076
  spd: 3
  heading: 177
}
...
}
flight_trail_list {
  snapshot_id: 1758466950
  lat: 22.3100777
  lon: 113.922523
  spd: 9
  heading: 160
}
position_buffer {
  recent_positions_list {
    delta_lat: -5
    delta_lon: 2
    delta_ms: 1670
  }
  recent_positions_list {
    delta_lat: -9
    delta_lon: 3
    delta_ms: 2610
  }
  recent_positions_list {
    delta_lat: -21
    delta_lon: 9
    delta_ms: 6010
  }
  recent_positions_list {
    delta_lat: -47
    delta_lon: 18
    delta_ms: 12350
  }
}

##### 1 #####
schedule_info {
  flight_number: "PR311"
  operated_by_id: 98
  painted_as_id: 98
  origin_id: 1366
  destination_id: 2266
  scheduled_departure: 1758466800
  scheduled_arrival: 1758475200
  arr_terminal: "1"
}
flight_progress {
  traversed_distance: 662
  remaining_distance: 1143066
  great_circle_distance: 1143502
  mean_flight_time: 5886
  flight_stage: ON_GROUND
}
flight_info {
  flightid: 1011880908
  lat: 22.3097286
  lon: 113.922668
  track: 160
  speed: 8
  timestamp_ms: 1758466960150
  on_ground: true
  callsign: "PAL311"
  ems_availability {
    rs_availability: true
  }
  squawk_availability: true
  airspace_availability: true
  server_time_ms: 1758466963120
}

##### 2 #####
schedule_info {
  flight_number: "PR311"
  operated_by_id: 98
  painted_as_id: 98
  origin_id: 1366
  destination_id: 2266
  scheduled_departure: 1758466800
  scheduled_arrival: 1758475200
  arr_terminal: "1"
}
flight_progress {
  traversed_distance: 667
  remaining_distance: 1143051
  great_circle_distance: 1143502
  mean_flight_time: 5886
  flight_stage: ON_GROUND
}
flight_info {
  flightid: 1011880908
  lat: 22.3095818
  lon: 113.922714
  track: 160
  speed: 9
  timestamp_ms: 1758466963941
  on_ground: true
  callsign: "PAL311"
  ems_availability {
    rs_availability: true
  }
  squawk_availability: true
  airspace_availability: true
  server_time_ms: 1758466966122
}

# --8<-- [end:proto]
"""
