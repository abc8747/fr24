import httpx
import pytest

from fr24.grpc import (
    follow_flight_request_create,
    follow_flight_stream,
    live_flights_status,
    live_flights_status_request_create,
    nearest_flights,
    nearest_flights_request_create,
)
from fr24.proto.v1_pb2 import (
    FollowFlightRequest,
    Geolocation,
    LiveFlightsStatusRequest,
    NearestFlightsRequest,
    NearestFlightsResponse,
    Status,
    TopFlightsRequest,
)


@pytest.fixture
async def nearest_flights_result(
    client: httpx.AsyncClient,
) -> NearestFlightsResponse:
    message = NearestFlightsRequest(
        location=Geolocation(lat=22.31257, lon=113.92708),
        radius=10000,
        limit=1500,
    )
    request = nearest_flights_request_create(message)
    data = await nearest_flights(client, request)
    return data.unwrap()


@pytest.mark.anyio
async def test_nearest_flights(
    nearest_flights_result: NearestFlightsResponse,
) -> None:
    assert len(nearest_flights_result.flights_list) > 2


@pytest.mark.anyio
async def test_live_flights_status(
    nearest_flights_result: NearestFlightsResponse, client: httpx.AsyncClient
) -> None:
    flight_ids = [
        f.flight.flightid for f in nearest_flights_result.flights_list
    ]

    message = LiveFlightsStatusRequest(flight_ids_list=flight_ids[:3])
    request = live_flights_status_request_create(message)
    result = await live_flights_status(client, request)
    data_status = result.unwrap()
    assert len(data_status.flights_map) == 3
    for flight in data_status.flights_map:
        assert flight.data.status == Status.LIVE


@pytest.mark.anyio
async def test_follow_flight(
    nearest_flights_result: NearestFlightsResponse,
) -> None:
    flight_id = nearest_flights_result.flights_list[0].flight.flightid
    timeout = httpx.Timeout(5, read=120)
    async with httpx.AsyncClient(timeout=timeout) as client:
        message = FollowFlightRequest(flight_id=flight_id)
        request = follow_flight_request_create(message)
        i = 0
        async for response in follow_flight_stream(client, request):
            if i == 0:
                assert len(response.unwrap().flight_trail_list)
            assert response.unwrap().flight_info.flightid == flight_id
            i += 1
            if i > 2:
                break


@pytest.mark.anyio
async def test_top_flights(client: httpx.AsyncClient) -> None:
    from fr24.grpc import top_flights, top_flights_request_create

    message = TopFlightsRequest(limit=10)
    request = top_flights_request_create(message)
    results = await top_flights(client, request)
    data = results.unwrap()
    assert len(data.scoreboard_list)


@pytest.mark.skip(
    reason="The API began to return empty `DATA` frames since Sep 2024"
)
@pytest.mark.anyio
async def test_live_trail(
    nearest_flights_result: NearestFlightsResponse, client: httpx.AsyncClient
) -> None:
    from fr24.grpc import live_trail, live_trail_request_create
    from fr24.proto.v1_pb2 import LiveTrailRequest

    flight_id = nearest_flights_result.flights_list[0].flight.flightid
    message = LiveTrailRequest(flight_id=flight_id)
    request = live_trail_request_create(message)
    results = await live_trail(client, request)
    data = results.unwrap()
    assert len(data.radar_records_list)


@pytest.mark.skip(reason="Private API, does not return data.")
@pytest.mark.anyio
async def test_search_index(client: httpx.AsyncClient) -> None:
    from fr24.grpc import search_index, search_index_request_create
    from fr24.proto.v1_pb2 import FetchSearchIndexRequest

    message = FetchSearchIndexRequest()
    request = search_index_request_create(message)
    results = await search_index(client, request)
    assert results.is_ok()  # fails, empty data frame
    data = results.unwrap()
    assert data


@pytest.mark.skip(reason="Private API, does not return data.")
@pytest.mark.anyio
async def test_historic_trail(
    nearest_flights_result: NearestFlightsResponse, client: httpx.AsyncClient
) -> None:
    from fr24.grpc import historic_trail, historic_trail_request_create
    from fr24.proto.v1_pb2 import HistoricTrailRequest

    flight_id = nearest_flights_result.flights_list[0].flight.flightid
    message = HistoricTrailRequest(flight_id=flight_id)
    request = historic_trail_request_create(message)
    results = await historic_trail(client, request)

    assert results.is_ok()  # read timeout
    data = results.unwrap()
    from fr24.proto.v1_pb2 import HistoricTrailResponse

    assert isinstance(data, HistoricTrailResponse)


def test_parse_data_grpc_status_error() -> None:
    """Fix for: https://github.com/cathaypacific8747/fr24/issues/68"""
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
