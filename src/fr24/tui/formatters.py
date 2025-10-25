from __future__ import annotations

from datetime import datetime, timezone

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

    def __format__(self, __format_spec: str) -> str:
        if self.airport is None:
            return ""
        output = __format_spec
        if code := self.airport.get("code"):
            output = output.replace("%a", code["iata"])
            output = output.replace("%o", code["icao"])
        else:
            return ""
        if name := self.airport.get("name"):
            output.replace("%n", name)
        else:
            output = output.replace("%n", "")
        if position := self.airport.get("position"):
            output = output.replace("%y", position["region"]["city"])
        else:
            output = output.replace("%y", "")
        return output


@dataclass_frozen
class Aircraft:
    aircraft: AircraftInfo

    def __format__(self, __format_spec: str) -> str:
        if self.aircraft is None:
            return ""
        registration = self.aircraft["registration"]
        hexcode = self.aircraft["hex"]
        model_text = self.aircraft["model"]["text"]
        return (
            __format_spec.replace("%c", self.aircraft["model"]["code"])
            .replace("%r", registration if registration else "")
            .replace("%x", hexcode if hexcode else "")
            .replace("%p", model_text if model_text else "")
        )
