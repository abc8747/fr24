import asyncio
from copy import deepcopy
from pathlib import Path
from typing import Callable

import httpx
import orjson
import polars as pl
import pytest
from pydantic import TypeAdapter

from fr24 import FR24, FR24Cache
from fr24.json import (
    FlightListParams,
    PlaybackParams,
    flight_list,
    flight_list_df,
    flight_list_parse,
    get_json_headers,
    playback,
)
from fr24.types.json import FlightList

REG = "F-HEPK"
FLIGHT = "AF7463"
HEADERS = httpx.Headers(get_json_headers())


@pytest.mark.anyio
async def test_ll_flight_list(client: httpx.AsyncClient) -> None:
    list_ = flight_list_parse(
        await flight_list(client, FlightListParams(reg=REG), HEADERS, auth=None)
    ).unwrap()
    df = flight_list_df(list_)
    assert df.shape[0] > 0
    landed = df.filter(pl.col("status").str.starts_with("Landed"))
    if landed.shape[0] == 0:
        return
    result = await asyncio.gather(
        *[
            playback(
                client,
                PlaybackParams(
                    flight_id=flight_id,
                    timestamp=entry["time"]["scheduled"]["arrival"],
                ),
                HEADERS,
                auth=None,
            )
            # the entry below is not None because of `if df is None:`
            for entry in list_["result"]["response"]["data"]  # type: ignore
            if (status := entry["status"]["text"]) is not None
            and status.startswith("Landed")
            and (flight_id := entry["identification"]["id"]) is not None
        ]
    )
    assert len(result) == landed.shape[0]

    ta = TypeAdapter(FlightList)
    ta.rebuild()
    ta.validate_python(list_, extra="forbid", strict=True)


# core


@pytest.mark.anyio
async def test_flight_list_reg(fr24: FR24) -> None:
    with pytest.raises(ValueError):  # missing reg/flight
        _ = await fr24.flight_list.fetch()
    result = await fr24.flight_list.fetch(reg=REG)
    data = result.to_dict()
    assert data["result"]["response"]["data"] is not None

    df = result.to_polars()
    assert df.height > 5


@pytest.mark.anyio
async def test_flight_list_flight(fr24: FR24) -> None:
    result = await fr24.flight_list.fetch(flight=FLIGHT)
    data = result.to_dict()
    assert data["result"]["response"]["data"] is not None

    df = result.to_polars()
    assert df.height > 5


@pytest.mark.anyio
async def test_flight_list_reg_paginate(fr24: FR24) -> None:
    """
    call 2 rows in 3 pages, combining them should yield 6 rows
    """
    results = fr24.flight_list.new_result_collection()

    i = 0
    async for result in fr24.flight_list.fetch_all(reg=REG, limit=2, delay=5):
        data = result.to_dict()
        assert data["result"]["response"]["data"] is not None

        df_new = result.to_polars()
        assert df_new.height > 0

        curr_rows = results.to_polars().height
        assert curr_rows == i * 2
        results.append(result)
        updated_rows = results.to_polars().height
        assert updated_rows == curr_rows + 2
        if updated_rows >= 6:
            break
        if i > 5:
            assert False, "infinite loop"
        i += 1


@pytest.mark.anyio
async def test_flight_list_reg_concat(fr24: FR24) -> None:
    """
    if we have existing flightids (10, 9, 8, 7) + new flightids (8, 7, 6, 5),
    the union of them should result in (10, 9, 8, 7, 6, 5)
    """
    result = await fr24.flight_list.fetch(reg=REG, limit=6)
    data = result.to_dict()
    flights = deepcopy(data["result"]["response"]["data"])
    assert flights is not None
    assert len(flights) == 6

    results = fr24.flight_list.new_result_collection()

    data["result"]["response"]["data"] = flights[:4]
    result.response._content = orjson.dumps(data)
    results.append(deepcopy(result))
    assert results.to_polars().height == 4

    data["result"]["response"]["data"] = flights[2:]
    result.response._content = orjson.dumps(data)
    results.append(deepcopy(result))
    assert results.to_polars().height == 6


@pytest.mark.anyio
async def test_flight_list_reg_file_ops(fr24: FR24, cache: FR24Cache) -> None:
    """
    check that saving and reopening in a new instance yields the same rows
    test that auto-detect directory and specified directory saving works
    """
    result = await fr24.flight_list.fetch(reg=REG)

    df = result.to_polars()
    curr_rows = df.height

    def test_ok(fp: Path, save: Callable[[], None]) -> None:
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.unlink(missing_ok=True)
        save()
        assert fp.exists(), (
            f"{fp} not in {list(f.name for f in fp.parent.glob('*'))}"
        )

        df = pl.read_parquet(fp)
        assert df.height == curr_rows
        fp.unlink()

    specific_fp = Path(__file__).parent / "tmp" / "flight_list.parquet"
    test_ok(specific_fp, lambda: result.write_table(specific_fp))
    specific_fp.parent.rmdir()

    test_ok(
        cache.path / "flight_list" / "reg" / f"{REG.upper()}.parquet",
        lambda: result.write_table(cache),
    )
