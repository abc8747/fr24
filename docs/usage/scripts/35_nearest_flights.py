# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import nearest_flights
from fr24.proto.v1_pb2 import (
    NearestFlightsResponse,
    NearestFlightsRequest,
    Geolocation,
)
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def nearest_flights_data() -> NearestFlightsResponse:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        message = NearestFlightsRequest(
            location=Geolocation(lat=22.31257, lon=113.92708),
            radius=1000,
            limit=1500,
        )
        response = await nearest_flights(client, message, headers)
        return parse_data(response.content, NearestFlightsResponse).unwrap()


data = await nearest_flights_data()
data
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:output0]
flights_list {
  flight {
    flightid: 905701578
    lat: 22.3095245
    lon: 113.930717
    track: 78
    speed: 9
    timestamp: 1720071634
    on_ground: true
    callsign: "CES502"
    extra_info {
      flight: "MU502"
      reg: "B-1908"
      route {
        from: "HKG"
        to: "PVG"
      }
      type: "B738"
      logo_id: 131
    }
  }
  distance: 504
}
flights_list {
  flight {
...
      logo_id: 335
    }
  }
  distance: 783
}
# --8<-- [end:output0]
"""
