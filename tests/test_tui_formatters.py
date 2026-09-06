from typing import cast

from fr24.tui.formatters import fmt_aircraft
from fr24.types.json import AircraftInfo


def test_fmt_aircraft_allows_missing_model_code() -> None:
    aircraft = {
        "registration": "OE-INL",
        "model": {"code": None, "text": None},
    }

    assert fmt_aircraft(cast(AircraftInfo, aircraft)).plain == "OE-INL ()"
