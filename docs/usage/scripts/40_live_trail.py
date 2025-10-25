# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import live_trail
from fr24.proto.v1_pb2 import LiveTrailRequest, LiveTrailResponse
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def live_trail_data() -> LiveTrailResponse:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        message = LiveTrailRequest(flight_id=0x395C43CF)
        response = await live_trail(client, message, headers)
        return parse_data(response.content, LiveTrailResponse).unwrap()


data = await live_trail_data()
data
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:output0]
radar_records_list {
  timestamp: 1720064455
  lat: 30.2406578
  lon: 120.420403
  spd: 15
  heading: 61
  callsign: "CPA959"
}
radar_records_list {
  timestamp: 1720064462
  lat: 30.2408924
  lon: 120.420937
  heading: 61
  callsign: "CPA959"
}
radar_records_list {
  timestamp: 1720064480
  lat: 30.2415791
  lon: 120.422478
  spd: 18
  heading: 61
  callsign: "CPA959"
}
radar_records_list {
  timestamp: 1720064488
...
  heading: 269
  vspd: -960
  squawk: 13874
  callsign: "CPA959"
}
...
# --8<-- [end:output0]
"""
