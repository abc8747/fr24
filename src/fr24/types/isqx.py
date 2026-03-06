from __future__ import annotations

from typing import TypeVar

import isqx
import isqx.aerospace
import isqx.usc
from typing_extensions import Annotated, TypeAlias

_T = TypeVar("_T")


TimestampS: TypeAlias = Annotated[_T, isqx.TIME[isqx.S]]
TimestampMs: TypeAlias = Annotated[_T, isqx.TIME[isqx.MILLI * isqx.S]]
DurationS: TypeAlias = Annotated[_T, isqx.DURATION(isqx.S)]
UtcOffsetS: TypeAlias = Annotated[_T, isqx.DURATION["utc_offset"](isqx.S)]
DistanceM: TypeAlias = Annotated[_T, isqx.DISTANCE(isqx.M)]

LatitudeDeg: TypeAlias = Annotated[_T, isqx.LATITUDE(isqx.DEG)]
LongitudeDeg: TypeAlias = Annotated[_T, isqx.LONGITUDE(isqx.DEG)]
BearingDeg: TypeAlias = Annotated[_T, isqx.aerospace.HEADING(isqx.DEG)]
GroundTrackDeg: TypeAlias = Annotated[_T, isqx.aerospace.GROUND_TRACK(isqx.DEG)]
BankAngleDeg: TypeAlias = Annotated[_T, isqx.aerospace.BANK_ANGLE(isqx.DEG)]

AltitudeM: TypeAlias = Annotated[_T, isqx.aerospace.PRESSURE_ALTITUDE(isqx.M)]
AltitudeFt: TypeAlias = Annotated[
    _T, isqx.aerospace.PRESSURE_ALTITUDE(isqx.usc.FT)
]
GeometricAltitudeM: TypeAlias = Annotated[
    _T, isqx.aerospace.GEOMETRIC_ALTITUDE(isqx.M)
]
PressureAltimeterHpa: TypeAlias = Annotated[
    _T, isqx.aerospace.PRESSURE_ALTIMETER(isqx.HECTO * isqx.PA)
]
StaticTemperatureC: TypeAlias = Annotated[
    _T, isqx.aerospace.STATIC_TEMPERATURE(isqx.CELSIUS)
]

GroundSpeedKmh: TypeAlias = Annotated[
    _T,
    isqx.aerospace.GROUND_SPEED(isqx.KILO * isqx.M * isqx.HOUR**-1),
]
GroundSpeedKt: TypeAlias = Annotated[
    _T, isqx.aerospace.GROUND_SPEED(isqx.usc.KNOT)
]
GroundSpeedMph: TypeAlias = Annotated[
    _T, isqx.aerospace.GROUND_SPEED(isqx.usc.MPH)
]
IndicatedAirSpeedKt: TypeAlias = Annotated[
    _T, isqx.aerospace.INDICATED_AIRSPEED(isqx.usc.KNOT)
]
TrueAirSpeedKt: TypeAlias = Annotated[
    _T, isqx.aerospace.TRUE_AIRSPEED(isqx.usc.KNOT)
]
WindSpeedKt: TypeAlias = Annotated[_T, isqx.aerospace.WIND_SPEED(isqx.usc.KNOT)]
# TODO: does fr24 return inertial/GNSS or barometric?
VerticalSpeedFpm: TypeAlias = Annotated[
    _T, isqx.aerospace.VERTICAL_RATE(isqx.usc.FT * isqx.MIN**-1)
]
VerticalSpeedMps: TypeAlias = Annotated[
    _T, isqx.aerospace.VERTICAL_RATE(isqx.M * isqx.S**-1)
]

MachTimes1K: TypeAlias = Annotated[_T, isqx.MACH_NUMBER * 1000]
