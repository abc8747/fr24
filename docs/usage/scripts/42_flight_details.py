# ruff: noqa
# fmt: off
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import (
    FlightDetailsParams,
    flight_details,
)
from fr24.proto.v1_pb2 import FlightDetailsResponse
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def flight_details_data() -> FlightDetailsResponse:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        params = FlightDetailsParams(flight_id=0x3c500fdb)
        response = await flight_details(client, params, headers)
        return parse_data(response.content, FlightDetailsResponse).unwrap()

data = await flight_details_data()
data
# --8<-- [end:script0]
#%%
"""
# --8<-- [start:output0]
aircraft_info {
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
  traversed_distance: 13728
  remaining_distance: 9652855
  elapsed_time: 156
  remaining_time: 51708
  eta: 1758518765
  great_circle_distance: 9647791
  mean_flight_time: 48161
  flight_stage: ASCENDING
  delay_status: RED
}
flight_info {
  flightid: 1011879899
  lat: 22.3374939
  lon: 114.046074
  track: 99
  alt: 4975
  speed: 205
  timestamp_ms: 1758467055960
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
  server_time_ms: 1758467057331
}
flight_plan {
}
flight_trail_list {
  snapshot_id: 1758465991
  lat: 22.3132782
  lon: 113.934616
  heading: 70
}
...
flight_trail_list {
  snapshot_id: 1758467049
  lat: 22.3383179
  lon: 114.039337
  altitude: 4800
  spd: 206
  heading: 91
}
position_buffer {
  recent_positions_list {
    delta_lat: -45
    delta_lon: 274
    delta_ms: 2710
  }
  recent_positions_list {
    delta_lat: -50
    delta_lon: 324
    delta_ms: 3180
  }
  recent_positions_list {
    delta_lat: -78
    delta_lon: 585
    delta_ms: 5720
  }
  recent_positions_list {
    delta_lat: -86
    delta_lon: 778
    delta_ms: 7570
  }
  recent_positions_list {
    delta_lat: -92
    delta_lon: 976
    delta_ms: 9540
  }
  recent_positions_list {
    delta_lat: -91
    delta_lon: 1073
    delta_ms: 10500
  }
}
# --8<-- [end:output0]
"""
