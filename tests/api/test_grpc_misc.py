import httpx
import pytest

from fr24.grpc import (
    nearest_flights,
)
from fr24.proto import parse_data
from fr24.proto.headers import get_grpc_headers
from fr24.proto.v1_pb2 import (
    Geolocation,
    NearestFlightsRequest,
    NearestFlightsResponse,
)

HEADERS = get_grpc_headers(auth=None)


# NOTE: this fixture already exists in `tests/api/conftest.py`
# TODO: remove once services are implemented
@pytest.fixture
async def nearest_flights_response(
    httpx_aclient: httpx.AsyncClient,
) -> NearestFlightsResponse:
    message = NearestFlightsRequest(
        location=Geolocation(lat=22.31257, lon=113.92708),
        radius=10000,
        limit=1500,
    )
    response = await nearest_flights(httpx_aclient, message, HEADERS)
    return parse_data(response.content, NearestFlightsResponse).unwrap()


@pytest.mark.skip(
    reason="Server began to return empty `DATA` frames since Sep 2024"
)
@pytest.mark.anyio
async def test_live_trail(
    nearest_flights_response: NearestFlightsResponse,
    httpx_aclient: httpx.AsyncClient,
) -> None:
    from fr24.grpc import live_trail
    from fr24.proto.v1_pb2 import LiveTrailRequest, LiveTrailResponse

    flight_id = nearest_flights_response.flights_list[0].flight.flightid
    message = LiveTrailRequest(flight_id=flight_id)
    response = await live_trail(httpx_aclient, message, HEADERS)
    result = parse_data(response.content, LiveTrailResponse)
    data = result.unwrap()
    assert len(data.radar_records_list)


@pytest.mark.skip(reason="Private API, does not return data.")
@pytest.mark.anyio
async def test_search_index(httpx_aclient: httpx.AsyncClient) -> None:
    from fr24.grpc import search_index
    from fr24.proto.v1_pb2 import (
        FetchSearchIndexRequest,
        FetchSearchIndexResponse,
    )

    message = FetchSearchIndexRequest()
    response = await search_index(httpx_aclient, message, HEADERS)
    result = parse_data(response.content, FetchSearchIndexResponse)
    assert result.is_ok()  # fails, empty data frame
    data = result.unwrap()
    assert data


@pytest.mark.skip(reason="Private API, does not return data.")
@pytest.mark.anyio
async def test_historic_trail(
    nearest_flights_response: NearestFlightsResponse,
    httpx_aclient: httpx.AsyncClient,
) -> None:
    from fr24.grpc import historic_trail
    from fr24.proto.v1_pb2 import HistoricTrailRequest, HistoricTrailResponse

    flight_id = nearest_flights_response.flights_list[0].flight.flightid
    message = HistoricTrailRequest(flight_id=flight_id)
    response = await historic_trail(httpx_aclient, message, HEADERS)
    result = parse_data(response.content, HistoricTrailResponse)

    assert result.is_ok()  # read timeout
    data = result.unwrap()
    from fr24.proto.v1_pb2 import HistoricTrailResponse

    assert isinstance(data, HistoricTrailResponse)


def test_parse_data_grpc_status_error() -> None:
    """Fix for: https://github.com/abc8747/fr24/issues/68"""
    from fr24.proto import GrpcError, parse_data
    from fr24.proto.v1_pb2 import FollowFlightResponse

    error_data = (
        b"\x80\x00\x00\x00/grpc-status:5\r\ngrpc-message:Flight not found!\r\n"
    )

    result = parse_data(error_data, FollowFlightResponse)

    assert result.is_err()
    err = result.err()
    assert isinstance(err, GrpcError)
    assert err.status == 5
    assert err.status_message == b"Flight not found!"
