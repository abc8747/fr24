import pytest

from fr24 import FR24, FR24Cache
from fr24.service import LiveFlightsStatusResult, NearestFlightsResult


@pytest.fixture
async def live_flights_status_result(
    fr24: FR24,
    nearest_flights_result: NearestFlightsResult,
) -> LiveFlightsStatusResult:
    flight_ids = [
        f.flight.flightid
        for f in nearest_flights_result.to_proto().flights_list[:5]
    ]

    result = await fr24.live_flights_status.fetch(flight_ids=flight_ids)
    return result


@pytest.mark.anyio
async def test_live_flights_status_simple(
    live_flights_status_result: LiveFlightsStatusResult,
) -> None:
    num_flights_requested = len(live_flights_status_result.request.flight_ids)
    num_flights = len(live_flights_status_result.to_proto().flights_map)
    assert num_flights_requested == num_flights

    df = live_flights_status_result.to_polars()
    assert df.height == num_flights
    assert df.width == 5


@pytest.mark.anyio
async def test_live_flights_status_file_ops(
    live_flights_status_result: LiveFlightsStatusResult, cache: FR24Cache
) -> None:
    timestamp = live_flights_status_result.timestamp
    ident = f"{timestamp}"
    fp = cache.path / "live_flights_status" / f"{ident}.parquet"
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.unlink(missing_ok=True)

    live_flights_status_result.write_table(cache)
    assert fp.exists(), f"{fp} not in {[f.name for f in fp.parent.glob('*')]}"

    df_local = cache.live_flights_status.scan_table(ident).collect()
    assert df_local.equals(live_flights_status_result.to_polars())

    fp.unlink()
