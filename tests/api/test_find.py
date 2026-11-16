import pytest
from pydantic import TypeAdapter

from fr24 import FR24
from fr24.types.json import (
    Find,
    is_aircraft,
    is_airport,
    is_live,
    is_operator,
    is_schedule,
)
from fr24.utils import get_current_timestamp

FIND_ADAPTER = TypeAdapter(Find)


@pytest.mark.anyio
async def test_find_airport(fr24: FR24) -> None:
    list_ = (await fr24.find.fetch("tou")).to_dict()
    assert list_ is not None
    assert list_["stats"]["count"]["airport"] >= 2

    found_francazal = False
    for result in list_["results"]:
        assert is_airport(result)
        if "LFBF" in result["label"]:
            found_francazal = True
    assert found_francazal

    FIND_ADAPTER.validate_python(list_, extra="forbid", strict=True)


@pytest.mark.anyio
async def test_find_aircraft(fr24: FR24) -> None:
    list_ = (await fr24.find.fetch("b-hp")).to_dict()
    assert list_ is not None

    found_bhpb = False
    for result in list_["results"]:
        if is_aircraft(result) and result["id"] == "B-HPB":
            found_bhpb = True

    assert found_bhpb

    FIND_ADAPTER.validate_python(list_, extra="forbid", strict=True)


@pytest.mark.anyio
async def test_find_operator(fr24: FR24) -> None:
    list_ = (await fr24.find.fetch("cat")).to_dict()
    assert list_ is not None

    found_cathay = False
    for result in list_["results"]:
        if is_operator(result) and "Cathay" in result["label"]:
            found_cathay = True
    assert found_cathay

    FIND_ADAPTER.validate_python(list_, extra="forbid", strict=True)


@pytest.mark.anyio
async def test_find_schedule_and_live(fr24: FR24) -> None:
    # avoid deadzone in the middle of the night
    utc_h = get_current_timestamp() % 86400 // 3600
    route = "cju-gmp" if utc_h < 8 else "fco-mad" if utc_h < 16 else "lax-sfo"
    list_ = (await fr24.find.fetch(route)).to_dict()
    assert list_ is not None

    schedule_count = 0
    live_count = 0
    for result in list_["results"]:
        if is_schedule(result):
            schedule_count += 1
        elif is_live(result):
            live_count += 1
    assert list_["stats"]["count"]["schedule"] == schedule_count
    assert schedule_count > 0
    assert list_["stats"]["count"]["live"] == live_count
    assert live_count > 0

    FIND_ADAPTER.validate_python(list_, extra="forbid", strict=True)
