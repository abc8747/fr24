# ruff: noqa
# mypy: disable-error-code="top-level-await, no-redef"
# %%
# --8<-- [start:script0]
import httpx
from fr24.grpc import search_index
from fr24.proto.v1_pb2 import FetchSearchIndexRequest, FetchSearchIndexResponse
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers


async def search_index_data() -> FetchSearchIndexResponse:
    headers = httpx.Headers(get_grpc_headers(auth=None))
    async with httpx.AsyncClient() as client:
        message = FetchSearchIndexRequest()
        response = await search_index(client, message, headers)
        return parse_data(response.content, FetchSearchIndexResponse).unwrap()


data = await search_index_data()
data
# --8<-- [end:script0]
# %%
"""
# --8<-- [start:output0]
GrpcError('empty DATA frame')
# --8<-- [end:output0]
"""
