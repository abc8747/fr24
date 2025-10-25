from __future__ import annotations

import asyncio
import re

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Label, Static

from fr24 import FR24
from fr24.types.json import is_aircraft, is_airport, is_schedule


def get_fr24(app: App) -> FR24:
    return app.fr24  # type: ignore


class AirportWidget(Static):
    UPDATE_TASK: None | asyncio.Task[None] = None

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
    async def lookup_airport(self) -> None:
        self.app.query_one(AircraftWidget).input.value = ""
        self.app.query_one(FlightWidget).input.value = ""
        input_ = self.query_one(Input)
        if len(value := input_.value) >= 3:
            if AirportWidget.UPDATE_TASK is not None:
                AirportWidget.UPDATE_TASK.cancel()
            AirportWidget.UPDATE_TASK = asyncio.create_task(
                self.update_airport(value)
            )
        else:
            self.iata.update()
            self.icao.update()
            self.fullname.update()
            self.airport_id = ""

    def update_info(self, info: None | dict[str, str] = None) -> None:
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
        result = await get_fr24(self.app).find.fetch(query=value)
        find_results = result.to_dict()
        if find_results is None:
            return self.update_info()
        candidate = next(
            (elt for elt in find_results["results"] if is_airport(elt)),
            None,
        )
        if candidate is None:
            return self.update_info()
        group = re.match(
            r"(?P<name>.+) \((?P<iata>\w+) / (?P<icao>\w+)\)",
            candidate["label"],
        )
        if group is None:
            return self.update_info()
        info: dict[str, str] = group.groupdict()
        return self.update_info(info)


class AircraftWidget(Static):
    UPDATE_TASK: None | asyncio.Task[None] = None

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
    async def lookup_aircraft(self) -> None:
        self.app.query_one(FlightWidget).input.value = ""
        for widget in self.app.query(AirportWidget):
            widget.input.value = ""
        input_ = self.query_one(Input)
        if len(value := input_.value) >= 3:
            if AircraftWidget.UPDATE_TASK is not None:
                AircraftWidget.UPDATE_TASK.cancel()
            AircraftWidget.UPDATE_TASK = asyncio.create_task(
                self.update_aircraft(value)
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
    UPDATE_TASK: None | asyncio.Task[None] = None

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
    async def lookup_number(self) -> None:
        self.app.query_one(AircraftWidget).input.value = ""
        for widget in self.app.query(AirportWidget):
            widget.input.value = ""
        input_ = self.query_one(Input)
        if len(value := input_.value) >= 3:
            if FlightWidget.UPDATE_TASK is not None:
                FlightWidget.UPDATE_TASK.cancel()
            FlightWidget.UPDATE_TASK = asyncio.create_task(
                self.update_number(value)
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
