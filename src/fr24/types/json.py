from __future__ import annotations

from typing import Literal, Union

from typing_extensions import (
    Annotated,
    NotRequired,
    Required,
    TypedDict,
    TypeGuard,
)

from . import IntTimestampS, StrFlightIdHex

#
# authentication
#


class User(TypedDict, total=False):
    id: Required[int]
    identity: str
    locale: str


class Features(TypedDict): ...  # useless anyway


class UserData(TypedDict, total=False):
    accessToken: None | str
    accountType: str
    countryCode: None | str
    dateExpires: IntTimestampS
    dateLastLogin: str
    features: Features
    hasConsented: bool
    hasPassword: bool
    idUser: int
    identity: str
    isActive: bool
    isAnonymousAccount: bool
    isLoggedIn: bool
    localeCode: str
    name: None
    oAuth: None
    oAuthType: None
    publicKey: None
    subscriptionKey: None | str
    tokenLogin: str
    typeSource: str


class Authentication(TypedDict, total=False):
    message: str
    msg: str
    response_code: int
    responseCode: int
    status: str
    success: bool
    token: str
    user: User
    features: Features
    userData: Required[UserData]


class UsernamePassword(TypedDict):
    username: str
    password: str


class TokenSubscriptionKey(TypedDict):
    subscriptionKey: str
    token: str


#
# common
#


class APIResult(TypedDict):
    copyright: str
    legalNotice: str


class FlightNumber(TypedDict):
    default: str | None
    alternative: NotRequired[str | None]


class AircraftModel(TypedDict):
    code: str
    text: None | str


class AircraftAge(TypedDict):
    availability: bool
    date: NotRequired[str]  # if unauthenticated


class AircraftAvailability(TypedDict):
    serialNo: bool
    age: bool


class _GenericStatus(TypedDict):
    text: str | None
    type: str
    color: str | None
    diverted: str | None


class _GenericEventTime(TypedDict):
    utc: int | None
    local: int | None


class _StatusGeneric(TypedDict):
    status: _GenericStatus
    eventTime: _GenericEventTime


class StatusData(TypedDict):
    live: bool | None
    text: str | None
    icon: str | None
    estimated: None
    ambiguous: bool
    generic: _StatusGeneric


class _Iata_Icao(TypedDict):
    iata: str | None
    icao: str


class OwnerData(TypedDict):
    name: str
    code: _Iata_Icao


class AirlineData(TypedDict):
    name: str
    code: _Iata_Icao
    short: str


class _AirportCode(TypedDict):
    iata: str
    icao: str


class _Country(TypedDict):
    name: str
    code: str
    id: int


class _Region(TypedDict):
    city: str


class _AirportPosition(TypedDict):
    latitude: float
    longitude: float
    country: _Country
    region: _Region


class _Timezone(TypedDict):
    name: str
    offset: int
    abbr: str
    abbrName: str | None
    isDst: bool


# prior to v0.2.0 this was `common.Airport`
class CommonAirport(TypedDict):
    name: str
    code: _AirportCode
    position: _AirportPosition
    timezone: _Timezone
    visible: NotRequired[bool]


# O/D can be null when route status is "unknown"
class AirportPairData(TypedDict):
    origin: None | CommonAirport
    destination: None | CommonAirport
    real: None | CommonAirport
    """Destination airport for diverted"""


class _Image(TypedDict):
    src: str
    link: str
    copyright: str
    source: str


class ImageCollection(TypedDict):
    large: list[_Image]
    medium: list[_Image]
    thumbnails: list[_Image]


#
# flight list
#


class FlightListRequest(TypedDict, total=False):
    callback: None
    device: None | str
    fetchBy: Required[str]
    filterBy: str | None
    format: Literal["json"]
    limit: Required[int]
    olderThenFlightId: None
    page: int
    pk: None
    query: Required[str]
    timestamp: IntTimestampS
    token: None | str


class Item(TypedDict):
    current: int
    total: None | int
    limit: int


class Page(TypedDict):
    current: int
    more: bool
    total: None | int


class Identification(TypedDict):
    id: str | None
    """icao hex"""
    row: int
    """internal row id"""
    number: FlightNumber
    callsign: str | None
    codeshare: None


class FlightListCountry(TypedDict):
    id: int | None
    name: str | None
    alpha2: str | None
    alpha3: str | None


class AircraftInfo(TypedDict):
    model: AircraftModel
    registration: None | str
    owner: NotRequired[OwnerData]
    airline: NotRequired[AirlineData]
    country: None | FlightListCountry
    hex: None | str
    restricted: bool
    serialNo: None | str
    age: AircraftAge
    availability: AircraftAvailability


class Interval(TypedDict):
    departure: None | IntTimestampS
    arrival: None | IntTimestampS


class TimeOther(TypedDict):
    eta: None | IntTimestampS
    updated: None | IntTimestampS
    duration: None | int


class FlightListTime(TypedDict):
    scheduled: Interval
    real: Interval
    estimated: Interval
    other: TimeOther


class FlightListItem(TypedDict):
    identification: Identification
    status: StatusData
    aircraft: AircraftInfo
    owner: OwnerData
    airline: AirlineData
    airport: AirportPairData
    time: FlightListTime


class AircraftImage(TypedDict):
    registration: str
    images: ImageCollection


class FlightListResponse(TypedDict):
    item: Item
    page: Page
    timestamp: IntTimestampS
    data: list[FlightListItem] | None
    # TODO: depending on whether the flight list was queried by reg or flight
    # this may change - check this again
    aircraftInfo: AircraftInfo
    aircraftImages: list[AircraftImage]


class FlightListResult(TypedDict):
    request: FlightListRequest
    response: FlightListResponse


class FlightList(TypedDict):
    result: FlightListResult
    _api: APIResult


FLIGHT_LIST_EMPTY: FlightList = {
    "result": {
        "request": {
            "fetchBy": "flight",
            "format": "json",
            "limit": 0,
            "page": 0,
            "query": "",
            "timestamp": 0,
        },
        "response": {
            "item": {"current": 0, "total": None, "limit": 0},
            "page": {"current": 0, "more": False, "total": None},
            "timestamp": 0,
            "data": None,
            "aircraftInfo": {
                "model": {"code": "", "text": ""},
                "registration": None,
                "country": None,
                "hex": None,
                "restricted": False,
                "serialNo": None,
                "age": {"availability": False},
                "availability": {"serialNo": False, "age": False},
            },
            "aircraftImages": [],
        },
    },
    "_api": {"copyright": "", "legalNotice": ""},
}
"""An object with no flight list data, for use as a default value."""

#
# playback types
#


class PlaybackRequest(TypedDict, total=False):
    callback: None
    device: None | str
    flightId: Required[StrFlightIdHex]
    format: Literal["json"]
    pk: None
    timestamp: IntTimestampS | None
    token: None | str


class FlightIdentification(TypedDict):
    id: StrFlightIdHex | int
    number: FlightNumber
    callsign: str


class AircraftIdentification(TypedDict):
    modes: str
    registration: str
    serialNo: None | str
    age: NotRequired[AircraftAge]  # if unauthenticated
    availability: NotRequired[AircraftAvailability]  # if unauthenticated


class AircraftData(TypedDict):
    model: AircraftModel
    identification: AircraftIdentification
    availability: AircraftAvailability


class Median(TypedDict):
    time: int | None
    delay: int | None
    timestamp: IntTimestampS | None


class Altitude(TypedDict):
    feet: int
    meters: int


class Speed(TypedDict):
    kmh: float
    kts: int
    mph: float


class VerticalSpeed(TypedDict):
    fpm: int | None
    ms: int | None


class EMS(TypedDict):
    ts: IntTimestampS
    ias: int | None
    tas: int | None
    mach: int | None
    mcp: int | None
    fms: int | None
    autopilot: None
    oat: int | None
    trueTrack: float | None
    rollAngle: float | None
    qnh: None
    windDir: int | None
    windSpd: int | None
    precision: int | None
    altGPS: int | None
    emergencyStatus: int | None
    tcasAcasDtatus: int | None
    heading: int | None


class TrackData(TypedDict):
    latitude: float
    longitude: float
    altitude: Altitude
    speed: Speed
    verticalSpeed: VerticalSpeed
    heading: int
    """
    !!! warning
        The JSON response claims that `heading` is available, but ADS-B only
        transmits the [ground track](https://mode-s.org/decode/content/ads-b/4-surface-position.html#ground-track).
        [Heading](https://mode-s.org/decode/content/mode-s/7-ehs.html#heading-and-speed-report-bds-60)
        is only available in [EMS][fr24.types.json.EMS] data.

        This field is renamed to `track` to avoid confusion in
        [fr24.json.playback_track_dict][].
    """
    squawk: str
    timestamp: IntTimestampS
    ems: None | EMS


class FlightDataAvailability(TypedDict):
    ems: bool


class FlightData(TypedDict):
    identification: FlightIdentification
    status: StatusData
    aircraft: AircraftData | None
    owner: OwnerData | None
    airline: AirlineData | None
    airport: AirportPairData
    median: Median
    track: list[TrackData]
    aircraftImages: ImageCollection
    availability: FlightDataAvailability


class PlaybackData(TypedDict):
    flight: FlightData


class PlaybackResponse(TypedDict):
    timestamp: IntTimestampS
    altitudeFiltered: bool
    data: PlaybackData


class PlaybackResult(TypedDict):
    request: PlaybackRequest
    response: PlaybackResponse


class Playback(TypedDict):
    result: PlaybackResult
    _api: APIResult


#
# airport list
#


# prior to v0.2.0 this was `airport_list.Schedule`
class AirportListScheduleSetting(TypedDict):
    mode: Literal["departures", "arrivals"] | None
    timestamp: IntTimestampS


Plugin = Literal[
    "details",
    "runways",
    "schedule",
    "satelliteImage",
    "scheduledRoutesStatistics",
    "weather",
]


class PluginSetting(TypedDict, total=False):
    schedule: AirportListScheduleSetting


AirportRequest = TypedDict(
    # we need this syntax because of the plugin-setting parameter
    "AirportRequest",
    {
        "callback": None,
        "code": str,
        "device": Union[str, None],
        "fleet": Union[str, None],
        "format": Literal["json"],
        "limit": int,
        "page": int,
        "pk": None,
        "plugin": list[Plugin],
        "plugin[]": list[Plugin],
        "plugin-setting": PluginSetting,
        "plugin-setting[schedule][mode]": str,
        "plugin-setting[schedule][timestamp]": IntTimestampS,
        "token": Union[str, None],
    },
    total=False,
)


class AirportSchedule(TypedDict):
    arrivals: FlightListResponse
    departures: FlightListResponse


class AirportPluginData(TypedDict):
    schedule: AirportSchedule


class AirportListData(TypedDict):
    pluginData: AirportPluginData


class AirportResponse(TypedDict):
    airport: AirportListData


class AirportResult(TypedDict):
    request: AirportRequest
    response: AirportResponse


class AirportList(TypedDict):
    result: AirportResult
    _api: APIResult


#
# find
#


class Live(TypedDict):
    operator_id: NotRequired[int]
    lat: float
    lon: float
    schd_from: str
    schd_to: NotRequired[str]
    ac_type: str
    route: str
    logo: NotRequired[str]
    reg: str
    callsign: NotRequired[str]
    flight: NotRequired[str]
    operator: NotRequired[str]


class FindAirportDetail(TypedDict):
    lat: float
    lon: float
    size: float


class Operator(TypedDict):
    operator_id: int
    iata: NotRequired[str]
    logo: NotRequired[str]


class FindScheduleDetail(TypedDict):
    logo: NotRequired[str]
    callsign: NotRequired[str]
    flight: str
    operator: NotRequired[str]
    operator_id: NotRequired[int]
    schd_from: NotRequired[str]
    schd_to: NotRequired[str]


class Aircraft(TypedDict):
    owner: str  # icao
    equip: str  # aircraft type
    hex: str
    operator_id: int
    logo: str


class EntryBase(TypedDict):
    label: str
    name: NotRequired[str]


Iata = Annotated[str, "IATA"]
Icao = Annotated[str, "ICAO"]


class AirportEntry(EntryBase):
    id: Iata | Icao  # iata if match == "begins"
    detail: FindAirportDetail
    type: Literal["airport"]
    match: Literal["icao", "iata", "begins", "contains"]


class OperatorEntry(EntryBase):
    id: str
    detail: Operator
    type: Literal["operator"]
    match: Literal["begins", "icao"]


class LiveEntry(EntryBase):
    id: str
    detail: Live
    type: Literal["live"]
    match: Literal["route", "begins"]


# prior to v0.2.0 this was `find.Schedule`
class ScheduleEntry(EntryBase):
    id: str
    detail: FindScheduleDetail
    type: Literal["schedule"]
    match: Literal["route", "begins"]


class AircraftEntry(EntryBase):
    id: str
    detail: Aircraft
    type: Literal["aircraft"]
    match: Literal["begins"]


Entry = Union[
    AirportEntry, OperatorEntry, LiveEntry, ScheduleEntry, AircraftEntry
]
# NOTE: in tests, we use Annotated[Entry, pydantic.Discriminator("type")]
# not adding here because pydantic belongs to test dependencies


def is_airport(entry: Entry) -> TypeGuard[AirportEntry]:
    return entry["type"] == "airport"


def is_operator(entry: Entry) -> TypeGuard[OperatorEntry]:
    return entry["type"] == "operator"


def is_live(entry: Entry) -> TypeGuard[LiveEntry]:
    return entry["type"] == "live"


def is_schedule(entry: Entry) -> TypeGuard[ScheduleEntry]:
    return entry["type"] == "schedule"


def is_aircraft(entry: Entry) -> TypeGuard[AircraftEntry]:
    return entry["type"] == "aircraft"


class StatsEntry(TypedDict):
    all: NotRequired[int]
    airport: int
    operator: int
    live: int
    schedule: int
    aircraft: int


class Stats(TypedDict):
    total: StatsEntry
    count: StatsEntry


class Info(TypedDict):
    grpcEnabled: bool


class Find(TypedDict):
    results: list[Entry]
    stats: Stats
    info: Info
