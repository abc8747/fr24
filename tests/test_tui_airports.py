from fr24.tui.widgets import lookup_airport_info


def test_lookup_airport_by_name() -> None:
    airport = lookup_airport_info("London Heathrow")

    assert airport is not None
    assert airport["iata"] == "LHR"
    assert airport["icao"] == "EGLL"


def test_lookup_airport_by_icao() -> None:
    airport = lookup_airport_info("EGLL")

    assert airport is not None
    assert airport["iata"] == "LHR"


def test_lookup_airport_returns_none_for_unknown_airport() -> None:
    assert lookup_airport_info("this airport does not exist") is None
