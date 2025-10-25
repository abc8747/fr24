from __future__ import annotations

from datetime import datetime, timezone

from rich.text import Text

from fr24.types import IntTimestampS
from fr24.types.json import AircraftInfo
from fr24.types.json import CommonAirport as AirportJSON
from fr24.utils import dataclass_frozen


@dataclass_frozen
class Time:
    timestamp: None | IntTimestampS

    def __format__(self, __format_spec: str) -> str:
        if self.timestamp is None:
            return ""
        dt = datetime.fromtimestamp(self.timestamp, tz=timezone.utc)
        return format(dt, __format_spec)


@dataclass_frozen
class Airport:
    airport: AirportJSON | None

    def to_text(self) -> Text:
        if self.airport is None:
            return Text("")

        code = self.airport.get("code")
        icao = code.get("icao", "") if code else ""

        city = ""
        if position := self.airport.get("position"):
            city = position.get("region", {}).get("city", "")

        if not city:
            city = self.airport.get("name", "")

        if city and icao:
            text = Text(city)
            text.append(" (", style="dim")
            text.append(icao, style="dim")
            text.append(")", style="dim")
            return text
        if city:
            return Text(city)
        if icao:
            text = Text("(", style="dim")
            text.append(icao, style="dim")
            text.append(")", style="dim")
            return text
        return Text("")


@dataclass_frozen
class Aircraft:
    aircraft: AircraftInfo | None

    def to_text(self) -> Text:
        if self.aircraft is None:
            return Text("")

        registration = self.aircraft.get("registration")
        typecode = self.aircraft.get("model", {}).get("code", "")

        if registration:
            text = Text(registration)
            text.append(" (", style="dim")
            text.append(typecode, style="dim")
            text.append(")", style="dim")
            return text
        return Text(typecode, style="dim")
