import asyncio
import time

import httpx
import pytest
from google.protobuf.json_format import MessageToDict

from fr24 import BBOX_FRANCE_UIR, BBOXES_WORLD_STATIC, FR24, FR24Cache
from fr24.grpc import (
    BoundingBox,
    LiveFeedParams,
    LiveFeedPlaybackParams,
    live_feed,
    live_feed_playback,
)
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers
from fr24.proto.v1_pb2 import Flight, LiveFeedResponse, PlaybackResponse

HEADERS = httpx.Headers(get_grpc_headers(auth=None))


@pytest.mark.anyio
async def test_ll_live_feed_france(client: httpx.AsyncClient) -> None:
    params = LiveFeedParams(bounding_box=BBOX_FRANCE_UIR)
    response = await live_feed(client, params, HEADERS)
    result = parse_data(response.content, LiveFeedResponse)

    json_output = MessageToDict(
        result.unwrap(), preserving_proto_field_name=True
    )
    assert len(json_output["flights_list"]) > 10


@pytest.mark.anyio
async def test_ll_live_feed_world(client: httpx.AsyncClient) -> None:
    async def get_data(bbox: BoundingBox) -> list[Flight]:
        params = LiveFeedParams(bounding_box=bbox)
        response = await live_feed(client, params, HEADERS)
        result = parse_data(response.content, LiveFeedResponse)
        return list(result.unwrap().flights_list)

    tasks = [get_data(bbox) for bbox in BBOXES_WORLD_STATIC]
    flightss = await asyncio.gather(*tasks)
    assert all(len(f) > 0 for f in flightss)
    assert len([f for flights in flightss for f in flights]) > 100


@pytest.mark.anyio
async def test_ll_live_feed_playback_world(client: httpx.AsyncClient) -> None:
    timestamp = int(time.time() - 86400)

    async def get_data(bbox: BoundingBox) -> list[Flight]:
        params = LiveFeedPlaybackParams(bounding_box=bbox, timestamp=timestamp)
        response = await live_feed_playback(client, params, HEADERS)
        result = parse_data(response.content, PlaybackResponse)
        return list(result.unwrap().live_feed_response.flights_list)

    tasks = [get_data(bbox) for bbox in BBOXES_WORLD_STATIC]
    flightss = await asyncio.gather(*tasks)
    assert all(len(f) > 0 for f in flightss)
    assert len([f for flights in flightss for f in flights]) > 100


# core tests


@pytest.mark.anyio
async def test_live_feed_live_france(fr24: FR24) -> None:
    result = await fr24.live_feed.fetch(BBOX_FRANCE_UIR)
    len_proto = len(result.to_proto().flights_list)
    assert len_proto > 10

    df = result.to_polars()
    assert df.height == len_proto


@pytest.mark.anyio
async def test_live_feed_playback_france(fr24: FR24) -> None:
    yesterday = int(time.time() - 86400)
    result = await fr24.live_feed_playback.fetch(
        BBOX_FRANCE_UIR, timestamp=yesterday
    )
    assert result.to_polars().height > 10


@pytest.mark.anyio
async def test_live_feed_file_ops(fr24: FR24, cache: FR24Cache) -> None:
    """ensure context persists after serialisation to parquet"""
    result = await fr24.live_feed.fetch(BBOX_FRANCE_UIR)
    result.write_table(cache)

    df_local = cache.live_feed.scan_table(result.timestamp).collect()
    assert df_local.equals(result.to_polars())
    # NOTE: metadata serialisation is not implemented
