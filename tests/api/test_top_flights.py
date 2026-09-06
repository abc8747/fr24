import pytest

from fr24 import FR24, FR24Cache
from fr24.service import TopFlightsResult


@pytest.fixture
async def top_flights_result(
    fr24: FR24,
) -> TopFlightsResult:
    LIMIT = 10

    result = await fr24.top_flights.fetch(limit=LIMIT)
    return result


@pytest.mark.anyio
async def test_top_flights_fetch(top_flights_result: TopFlightsResult) -> None:
    num_flights_requested = top_flights_result.request.limit
    num_flights = len(top_flights_result.to_proto().scoreboard_list)
    assert num_flights_requested == num_flights

    df = top_flights_result.to_polars()
    assert df.height == num_flights
    assert df.width == 12


@pytest.mark.anyio
async def test_top_flights_file_ops(
    top_flights_result: TopFlightsResult, cache: FR24Cache
) -> None:
    timestamp = top_flights_result.timestamp
    ident = f"{timestamp}"
    fp = cache.path / "top_flights" / f"{ident}.parquet"
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.unlink(missing_ok=True)

    top_flights_result.write_table(cache)
    assert fp.exists(), f"{fp} not in {[f.name for f in fp.parent.glob('*')]}"

    df_local = cache.top_flights.scan_table(ident).collect()
    assert df_local.equals(top_flights_result.to_polars())

    fp.unlink()
