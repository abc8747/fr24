# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import historic_trail
from fr24.proto.v1_pb2 import HistoricTrailRequest, HistoricTrailResponse
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def historic_trail_data() -> HistoricTrailResponse:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        message = HistoricTrailRequest(flight_id=0x395C43CF)
        response = await historic_trail(client, message, headers)
        return parse_data(response.content, HistoricTrailResponse).unwrap()


data = await historic_trail_data()
data
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:output0]
504 GATEWAY TIMEOUT
# --8<-- [end:output0]
"""
