import pytest

from fr24 import FR24, FR24Cache
from fr24.service import FlightDetailsResult, NearestFlightsResult
from fr24.utils import to_flight_id


@pytest.fixture
async def flight_details_result(
    fr24: FR24,
    nearest_flights_result: NearestFlightsResult,
) -> FlightDetailsResult:
    flight_id = (
        nearest_flights_result.to_proto().flights_list[-1].flight.flightid
    )

    result = await fr24.flight_details.fetch(flight_id=flight_id)
    return result


@pytest.mark.anyio
async def test_flight_details_simple(
    flight_details_result: FlightDetailsResult,
) -> None:
    proto = flight_details_result.to_proto()
    assert len(proto.flight_trail_list) > 10

    df = flight_details_result.to_polars()
    assert df.height == 1
    assert df.width == 32


@pytest.mark.anyio
async def test_flight_details_file_ops(
    flight_details_result: FlightDetailsResult, cache: FR24Cache
) -> None:
    flight_id = f"{to_flight_id(flight_details_result.request.flight_id):0x}"
    timestamp = flight_details_result.timestamp
    fp = (
        cache.path
        / "flight_details"
        / f"{flight_id.upper()}_{timestamp}.parquet"
    )
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.unlink(missing_ok=True)

    flight_details_result.write_table(cache)
    assert fp.exists(), (
        f"{fp} not in {list(f.name for f in fp.parent.glob('*'))}"
    )

    df_local = cache.flight_details.scan_table(flight_id, timestamp).collect()
    assert df_local.equals(flight_details_result.to_polars())

    fp.unlink()
