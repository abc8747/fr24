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


def fmt_airport(airport: AirportJSON | None) -> Text:
    if airport is None:
        return Text("")

    code = airport.get("code")
    icao = code.get("icao", "") if code else ""

    city = ""
    if position := airport.get("position"):
        city = position.get("region", {}).get("city", "")

    if not city:
        city = airport.get("name", "")

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


def fmt_aircraft(aircraft: AircraftInfo | None) -> Text:
    if aircraft is None:
        return Text("")

    registration = aircraft.get("registration")
    typecode = aircraft.get("model", {}).get("code", "")

    if registration:
        text = Text(registration)
        text.append(" (", style="dim")
        text.append(typecode, style="dim")
        text.append(")", style="dim")
        return text
    return Text(typecode, style="dim")


BLUE = "#5d9ad4"
GREEN = "#67a76d"
ORANGE = "#bd8a44"
RED = "#cf7a78"
GREY = "#959595"


def fmt_status(
    status_text: str,
    *,
    colours: dict[str, str] = {
        "Scheduled": BLUE,
        "Departed": GREEN,
        "Estimated": GREEN,
        "Landed": GREEN,
        "Delayed": ORANGE,
        "Canceled": RED,
        "Diverted": RED,
        "Unknown": GREY,
    },
) -> Text:
    for status, status_color in colours.items():
        if status_text.startswith(status):
            return Text(status_text, style=status_color)
    return Text(status_text, style=GREY)
