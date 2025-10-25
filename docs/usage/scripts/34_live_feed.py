# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import LiveFeedParams, BoundingBox, live_feed
from fr24.proto.v1_pb2 import LiveFeedResponse
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def france_data() -> LiveFeedResponse:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        params = LiveFeedParams(
            bounding_box=BoundingBox(north=50, west=-7, south=40, east=10)
        )
        response = await live_feed(client, params, headers)
        result = parse_data(response.content, LiveFeedResponse)
        return result.unwrap()  # (1)!


data = await france_data()
data
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:output0]
flights_list {
  flightid: 941292228
  lat: 40.0058289
  lon: -5.02393532
  track: 225
  alt: 26800
  speed: 427
  icon: A320
  timestamp: 1732481230
  callsign: "IBS15MA"
  extra_info {
    flight: "IB1589"
    reg: "EC-OAS"
    route {
      from: "MAD"
      to: "TFN"
    }
    type: "A21N"
  }
  position_buffer {
    recent_positions_list {
      delta_lat: -418
      delta_lon: -562
      delta_ms: 3000
    }
...
      delta_lon: -1958
      delta_ms: 10000
    }
  }
}
# --8<-- [end:output0]
"""
# %% [markdown]
# # explore in JSON format

# %%
# --8<-- [start:script1]
from google.protobuf.json_format import MessageToDict

MessageToDict(data)["flightsList"]
# --8<-- [end:script1]
# %%
"""
# --8<-- [start:output1]
[{'flightid': 941292228,
  'lat': 40.00583,
  'lon': -5.0239353,
  'track': 225,
  'alt': 26800,
  'speed': 427,
  'icon': 'A320',
  'timestamp': 1732481230,
  'callsign': 'IBS15MA',
  'extraInfo': {'flight': 'IB1589',
   'reg': 'EC-OAS',
   'route': {'from': 'MAD', 'to': 'TFN'},
   'type': 'A21N'},
  'positionBuffer': {'recentPositionsList': [{'deltaLat': -418,
     'deltaLon': -562,
     'deltaMs': 3000}]}},
 {'flightid': 941277503,
  'lat': 40.050613,
  'lon': -6.7190137,
  'track': 24,
  'alt': 38000,
  'speed': 481,
  'icon': 'A320',
  'timestamp': 1732481230,
  'callsign': 'VOE2RY',
...
  'positionBuffer': {'recentPositionsList': [{'deltaLat': 315,
     'deltaLon': -660,
     'deltaMs': 3000},
    {'deltaLat': 553, 'deltaLon': -1170, 'deltaMs': 6000},
    {'deltaLat': 929, 'deltaLon': -1958, 'deltaMs': 10000}]}}]
# --8<-- [end:output1]
"""
# %%
