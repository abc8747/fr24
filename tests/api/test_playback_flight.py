import pytest

from fr24 import FR24, FR24Cache
from fr24.service import FlightListResult, PlaybackFlightResult
from fr24.utils import to_flight_id


@pytest.fixture
async def flight_list_result(
    fr24: FR24,
) -> FlightListResult:
    REG = "B-LXA"
    result = await fr24.flight_list.fetch(reg=REG)
    return result


@pytest.fixture
async def playback_flight_result(
    fr24: FR24,
    flight_list_result: FlightListResult,
) -> PlaybackFlightResult:
    import polars as pl

    df = flight_list_result.to_polars()
    landed = df.filter(pl.col("status").str.starts_with("Landed"))

    assert landed.height > 0, "no landed flights found"

    flight_id = landed[0, "flight_id"]
    stod = int(landed[0, "ATOD"].timestamp())

    result = await fr24.playback_flight.fetch(
        flight_id=flight_id, timestamp=stod
    )
    return result


@pytest.mark.anyio
async def test_playback_flight_simple(
    playback_flight_result: PlaybackFlightResult,
) -> None:
    proto = playback_flight_result.to_proto()
    assert len(proto.flight_trail_list) > 10

    df = playback_flight_result.to_polars()
    assert df.height == 1
    assert df.width == 24


@pytest.mark.anyio
async def test_playback_flight_file_ops(
    playback_flight_result: PlaybackFlightResult, cache: FR24Cache
) -> None:
    flight_id = f"{to_flight_id(playback_flight_result.request.flight_id):0x}"
    timestamp = playback_flight_result.request.timestamp
    fp = (
        cache.path
        / "playback_flight"
        / f"{flight_id.upper()}_{timestamp}.parquet"
    )
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.unlink(missing_ok=True)

    playback_flight_result.write_table(cache)
    assert fp.exists(), (
        f"{fp} not in {list(f.name for f in fp.parent.glob('*'))}"
    )

    df_local = cache.playback_flight.scan_table(flight_id, timestamp).collect()
    assert df_local.equals(playback_flight_result.to_polars())

    fp.unlink()
