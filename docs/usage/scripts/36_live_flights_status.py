# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import live_flights_status
from fr24.proto.v1_pb2 import (
    LiveFlightsStatusRequest,
    LiveFlightsStatusResponse,
)
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def live_flights_status_data() -> LiveFlightsStatusResponse:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        message = LiveFlightsStatusRequest(
            flight_ids_list=[0x35FBC363, 0x35FBF180]
        )
        response = await live_flights_status(client, message, headers)
        return parse_data(response.content, LiveFlightsStatusResponse).unwrap()


data = await live_flights_status_data()
data
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:output0]
flights_map {
  flight_id: 905703808
  data {
    lat: 21.7237415
    lon: 114.917908
    status: LIVE
  }
}
flights_map {
  flight_id: 905692003
  data {
    lat: 21.9285736
    lon: 113.912445
    status: LIVE
  }
}
# --8<-- [end:output0]
"""
