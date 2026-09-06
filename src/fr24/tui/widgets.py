from __future__ import annotations

from functools import cache
from typing import TypedDict, cast

import airportsdata
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Label, Static

from fr24 import FR24
from fr24.types.json import is_aircraft, is_schedule


class AirportInfo(TypedDict):
    name: str
    iata: str
    icao: str
    city: str


@cache
def get_airports() -> dict[str, AirportInfo]:
    """Load the bundled IATA airport database once per TUI session."""
    return cast(dict[str, AirportInfo], airportsdata.load("IATA"))


def lookup_airport_info(query: str) -> AirportInfo | None:
    """Find the best IATA airport match without FR24's blocked API."""
    query = query.strip().casefold()
    if not query:
        return None

    airports = get_airports()
    if airport := airports.get(query.upper()):
        return airport

    def rank(airport: AirportInfo) -> tuple[int, str]:
        iata = airport["iata"].casefold()
        icao = airport["icao"].casefold()
        name = airport["name"].casefold()
        city = airport["city"].casefold()
        if query in (iata, icao):
            return (0, name)
        if iata.startswith(query) or icao.startswith(query):
            return (1, name)
        if name.startswith(query) or city.startswith(query):
            return (2, name)
        return (3, name)

    candidates = (
        airport
        for airport in airports.values()
        if query in " ".join(
            (
                airport["iata"].casefold(),
                airport["icao"].casefold(),
                airport["name"].casefold(),
                airport["city"].casefold(),
            )
        )
    )
    return min(candidates, key=rank, default=None)


def get_fr24(app: App[None]) -> FR24:
    return app.fr24  # type: ignore


class AirportWidget(Static):
    def compose(self) -> ComposeResult:
        assert self.name is not None
        self.iata = Static("", id="iata")
        self.icao = Static("", id="icao")
        self.fullname = Static("", id="name")
        self.airport_id = ""
        self.input = Input(id=self.name)

        yield Label(self.name)
        yield self.input
        with Horizontal():
            yield self.iata
            yield self.icao
        yield self.fullname

    @on(Input.Changed)
    def lookup_airport(self) -> None:
        self.app.query_one(AircraftWidget).input.value = ""
        self.app.query_one(FlightWidget).input.value = ""
        input_ = self.query_one(Input)
        if len(value := input_.value) >= 3:
            self.run_worker(
                self.update_airport(value),
                name="airport_lookup",
                exclusive=True,
            )
        else:
            self.update_info()
            self.airport_id = ""

    def update_info(self, info: AirportInfo | None = None) -> None:
        # NOTE(abr): for some odd reason when i backspace too quickly it doesn't
        # clear properly
        if info is None:
            self.icao.update()
            self.iata.update()
            self.fullname.update()
            self.airport_id = ""
        else:
            self.icao.update(info["icao"])
            self.iata.update(info["iata"])
            self.fullname.update(info["name"])
            self.airport_id = info["iata"]

    async def update_airport(self, value: str) -> None:
        # The legacy FR24 find endpoint is Cloudflare-protected. Airport
        # metadata is static, so resolve it locally instead of making a request
        # that fails while the user is typing.
        if self.input.value != value:
            return  # stale worker, discard result.
        info = lookup_airport_info(value)
        self.update_info(info)


class AircraftWidget(Static):
    def compose(self) -> ComposeResult:
        assert self.name is not None
        self.hex = Static("", id="hex")
        self.reg = Static("", id="reg")
        self.type = Static("", id="type")
        self.aircraft_id = ""
        self.input = Input(id=self.name)

        yield Label(self.name)
        yield self.input
        yield self.reg
        with Horizontal():
            yield self.hex
            yield self.type

    @on(Input.Changed)
    def lookup_aircraft(self) -> None:
        self.app.query_one(FlightWidget).input.value = ""
        for widget in self.app.query(AirportWidget):
            widget.input.value = ""
        input_ = self.query_one(Input)
        if len(value := input_.value) >= 3:
            self.run_worker(
                self.update_aircraft(value),
                name="aircraft_lookup",
                exclusive=True,
            )
        else:
            self.update_info()

    def update_info(
        self,
        reg: None | str = None,
        hex: None | str = None,
        typecode: None | str = None,
    ) -> None:
        if reg is None or hex is None or typecode is None:
            self.type.update()
            self.hex.update()
            self.reg.update()
            self.aircraft_id = ""
        else:
            self.type.update(typecode)
            self.hex.update(hex.lower())
            self.reg.update(reg)
            self.aircraft_id = reg

    async def update_aircraft(self, value: str) -> None:
        result = await get_fr24(self.app).find.fetch(query=value)
        if self.input.value != value:
            return
        res = result.to_dict()
        if res is None:
            return self.update_info()
        candidates = (elt for elt in res["results"] if is_aircraft(elt))
        aircraft = next(candidates, None)
        if aircraft is None:
            return self.update_info()

        return self.update_info(
            aircraft["id"],
            aircraft["detail"]["hex"],
            aircraft["detail"]["equip"],
        )


class FlightWidget(Static):
    def compose(self) -> ComposeResult:
        assert self.name is not None
        self.flight = Static("", id="flight")
        self.callsign = Static("", id="callsign")
        self.number = ""
        self.input = Input(id=self.name)

        yield Label(self.name)
        yield self.input
        with Horizontal():
            yield self.flight
            yield self.callsign

        self.input.focus()

    @on(Input.Changed)
    def lookup_number(self) -> None:
        self.app.query_one(AircraftWidget).input.value = ""
        for widget in self.app.query(AirportWidget):
            widget.input.value = ""
        input_ = self.query_one(Input)
        if len(value := input_.value) >= 3:
            self.run_worker(
                self.update_number(value), name="flight_lookup", exclusive=True
            )
        else:
            self.update_info()

    def update_info(
        self,
        number: str | None = None,
        callsign: str | None = None,
    ) -> None:
        if number is None or callsign is None:
            self.flight.update()
            self.callsign.update()
            self.number = ""
        else:
            self.flight.update(number)
            self.callsign.update(callsign)
            self.number = number

    async def update_number(self, value: str) -> None:
        result = await get_fr24(self.app).find.fetch(query=value)
        if self.input.value != value:
            return
        find_results = result.to_dict()
        if find_results is None:
            return self.update_info()
        candidate = next(
            (elt for elt in find_results["results"] if is_schedule(elt)),
            None,
        )
        if candidate is None:
            return self.update_info()
        return self.update_info(
            candidate["detail"]["flight"], candidate["detail"].get("callsign")
        )
