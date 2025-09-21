from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    AsyncIterator,
    Generic,
    Literal,
    Protocol,
    Sequence,
    TypeVar,
    Union,
)

from google.protobuf.json_format import MessageToDict
from typing_extensions import runtime_checkable

from .cache import FR24Cache
from .grpc import (
    BoundingBox,
    FlightDetailsParams,
    FollowFlightParams,
    LiveFeedParams,
    LiveFeedPlaybackParams,
    LiveFlightsStatusParams,
    NearestFlightsParams,
    PlaybackFlightParams,
    TopFlightsParams,
    flight_details,
    flight_details_df,
    follow_flight_stream,
    live_feed,
    live_feed_df,
    live_feed_playback,
    live_feed_playback_df,
    live_flights_status,
    live_flights_status_df,
    nearest_flights,
    nearest_flights_df,
    playback_flight,
    playback_flight_df,
    top_flights,
    top_flights_df,
)
from .json import (
    AirportListParams,
    FindParams,
    FlightListParams,
    PlaybackParams,
    airport_list,
    airport_list_parse,
    find,
    find_parse,
    flight_list,
    flight_list_df,
    flight_list_parse,
    playback,
    playback_df,
    playback_metadata_dict,
    playback_parse,
)
from .proto import SupportsToProto, parse_data
from .proto.v1_pb2 import (
    FlightDetailsResponse,
    FollowFlightResponse,
    LiveFeedResponse,
    LiveFlightsStatusResponse,
    NearestFlightsResponse,
    PlaybackFlightResponse,
    PlaybackResponse,
    RestrictionVisibility,
    TopFlightsResponse,
)
from .types import IntoFlightId, IntoTimestamp, IntTimestampS
from .types.cache import TabularFileFmt
from .types.grpc import LiveFeedField
from .types.json import (
    FLIGHT_LIST_EMPTY,
    AirportList,
    Find,
    FlightList,
    Playback,
)
from .utils import (
    FileExistsBehaviour,
    FileLike,
    SupportsToDict,
    SupportsToPolars,
    dataclass_frozen,
    dataclass_opts,
    get_current_timestamp,
    parse_server_timestamp,
    static_check_signature,
    write_table,
)

if TYPE_CHECKING:
    import httpx
    import polars as pl
    from typing_extensions import TypeAlias

    from . import HTTPClient

logger = logging.getLogger(__name__)

#
# important traits and dataclasses
#


@dataclass_frozen
class ServiceFactory:
    http: HTTPClient

    def build_flight_list(self) -> FlightListService:
        return FlightListService(self)

    def build_playback(self) -> PlaybackService:
        return PlaybackService(self)

    def build_live_feed(self) -> LiveFeedService:
        return LiveFeedService(self)

    def build_live_feed_playback(self) -> LiveFeedPlaybackService:
        return LiveFeedPlaybackService(self)

    def build_airport_list(self) -> AirportListService:
        return AirportListService(self)

    def build_find(self) -> FindService:
        return FindService(self)

    def build_nearest_flights(self) -> NearestFlightsService:
        return NearestFlightsService(self)

    def build_live_flights_status(self) -> LiveFlightsStatusService:
        return LiveFlightsStatusService(self)

    def build_flight_details(self) -> FlightDetailsService:
        return FlightDetailsService(self)

    def build_top_flights(self) -> TopFlightsService:
        return TopFlightsService(self)

    def build_follow_flight(self) -> FollowFlightService:
        return FollowFlightService(self)

    def build_playback_flight(self) -> PlaybackFlightService:
        return PlaybackFlightService(self)


RequestT = TypeVar("RequestT")
"""Arguments for the request"""


@runtime_checkable
class SupportsFetch(Protocol[RequestT]):
    async def fetch(self, *args: Any, **kwargs: Any) -> APIResult[RequestT]:
        """Fetches data from the API."""
        ...


@dataclass_frozen
class APIResult(Generic[RequestT]):
    """Wraps the raw `Response` with request context.

    Note that at this stage, the response holds the *raw* bytes, possibly
    encoded with a scheme. Retrieve the raw bytes with `response.content` or
    parse it into json with `response.json()`.
    """

    request: RequestT
    response: httpx.Response


WriteLocation: TypeAlias = Union[FileLike, FR24Cache]


@runtime_checkable
class SupportsWriteTable(Protocol):
    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt,
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        """Writes the object to the given file path."""


#
# definitions for services and results
#


@dataclass_frozen
class FlightListService(SupportsFetch[FlightListParams]):
    """Flight list service."""

    _factory: ServiceFactory

    @static_check_signature(FlightListParams)
    async def fetch(
        self,
        reg: str | None = None,
        flight: str | None = None,
        page: int = 1,
        limit: int = 10,
        timestamp: IntoTimestamp | Literal["now"] | None = "now",
        filter_by: Literal["historic"] | None = None,
    ) -> FlightListResult:
        """Fetch the flight list.

        :param reg: Aircraft registration (e.g. `B-HUJ`)
        :param flight: Flight number (e.g. `CX8747`)
        :param page: Page number
        :param limit: Number of results per page - use `100` if authenticated.
        :param timestamp: Show flights with ATD before this Unix timestamp
        :param filter_by: If `historic`, do not return scheduled or live flights
        """
        params = FlightListParams(
            reg=reg,
            flight=flight,
            page=page,
            limit=limit,
            timestamp=timestamp,
            filter_by=filter_by,
        )
        response = await flight_list(
            self._factory.http.client,
            params,
            self._factory.http.json_headers,
            self._factory.http.auth,
        )
        return FlightListResult(
            request=params,
            response=response,
        )

    @dataclass(**dataclass_opts)
    class FetchAllArgs(FlightListParams):
        """Arguments for fetching all pages of the flight list."""

        delay: int = field(default=5)
        """Delay between requests in seconds."""
        max_pages: int | None = field(default=None)
        """Maximum number of pages to fetch."""

    @static_check_signature(FetchAllArgs)
    async def fetch_all(
        self,
        reg: str | None = None,
        flight: str | None = None,
        page: int = 1,
        limit: int = 10,
        timestamp: IntoTimestamp | Literal["now"] | None = "now",
        filter_by: Literal["historic"] | None = None,
        delay: int = 5,
        max_pages: int | None = None,
    ) -> AsyncIterator[FlightListResult]:
        """Fetch all pages of the flight list.

        :param reg: Aircraft registration (e.g. `B-HUJ`)
        :param flight: Flight number (e.g. `CX8747`)
        :param page: Page number
        :param limit: Number of results per page - use `100` if authenticated.
        :param timestamp: Show flights with ATD before this Unix timestamp
        :param filter_by: If `historic`, do not return scheduled or live flights
        :param delay: Delay between requests in seconds.
        :param max_pages: Maximum number of pages to fetch.
        """
        # TODO: something nasty with async generators is happening here
        # (httpx leak)
        more = True
        current_timestamp = timestamp
        while more:
            result = await self.fetch(
                reg=reg,
                flight=flight,
                page=page,
                limit=limit,
                timestamp=current_timestamp,
                filter_by=filter_by,
            )
            response_dict = result.to_dict()
            # shouldn't happen, but stop in case we overshot
            if (data := response_dict["result"]["response"]["data"]) is None:
                break
            yield result
            if max_pages is not None and page >= max_pages:
                break
            page += 1

            # NOTE: for the next request, we have to both:
            # - update the timestamp to the earliest STD in the current batch
            # - increment the page
            # weird, but it's how the API works
            current_timestamp = min(
                t
                for d in data
                if (t := d["time"]["scheduled"]["departure"]) is not None
            )

            more = response_dict["result"]["response"]["page"]["more"]
            await asyncio.sleep(delay)

    def new_result_collection(self) -> FlightListResultCollection:
        """Create an empty list of flight list API results.

        Methods `to_dict` and `to_polars` can be used collect all unique rows in
        each flight list.
        """
        return FlightListResultCollection()


@dataclass_frozen
class FlightListResult(
    APIResult[FlightListParams],
    SupportsToDict[FlightList],
    SupportsToPolars,
    SupportsWriteTable,
):
    """A single result from the flight list API."""

    def to_dict(self) -> FlightList:
        return flight_list_parse(self.response).unwrap()

    def to_polars(self) -> pl.DataFrame:
        return flight_list_df(self.to_dict())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.flight_list(self.request.kind).get_path(
                self.request.ident
            )
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


class FlightListResultCollection(
    list[FlightListResult],
    SupportsToDict[FlightList],
    SupportsToPolars,
    SupportsWriteTable,
):
    """A list of results from the flight list API."""

    def to_dict(self) -> FlightList:
        """Collects the raw bytes in each response into a single result.
        Duplicates are identified by their (flight id, time of departure),
        and are removed.

        No checking is made for the homogenity of the request parameters.
        """

        if len(self) == 0:
            return FLIGHT_LIST_EMPTY

        ident_hashes: set[int] = set()
        data = self[0].to_dict()
        flights_all = []
        for result in self:
            if (
                flights := result.to_dict()["result"]["response"]["data"]
            ) is None:
                continue
            for flight in flights:
                # NOTE: for future scheduled flights:
                # - the flight id is empty
                # - the standard time of departure is most certainly known
                # -> we use the STOD as the primary key for duplicates
                flight_id = flight["identification"]["id"]
                stod = flight["time"]["scheduled"]["departure"]
                ident_hash = hash((flight_id, stod))
                if ident_hash in ident_hashes:
                    if stod is not None:
                        logger.info(
                            f"skipping duplicate: {flight_id=} and {stod=}"
                        )
                        continue
                    else:
                        logger.warning(
                            f"unexpected empty STOD for {flight_id=}"
                        )
                ident_hashes.add(ident_hash)
                flights_all.append(flight)

        data["result"]["response"]["data"] = flights_all
        return data

    def to_polars(self) -> pl.DataFrame:
        return flight_list_df(self.to_dict())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if not self:
            raise ValueError(
                "cannot save an empty flight list, "
                "must contain at least one valid flight list response"
            )
        if isinstance(file, FR24Cache):
            file = file.flight_list(self[0].request.kind).get_path(
                self[0].request.ident
            )
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class PlaybackService(SupportsFetch[PlaybackParams]):
    """Playback service."""

    _factory: ServiceFactory

    @static_check_signature(PlaybackParams)
    async def fetch(
        self, flight_id: IntoFlightId, timestamp: IntoTimestamp | None = None
    ) -> PlaybackResult:
        """Fetch the playback data for a flight.

        :param flight_id: fr24 flight id, represented in hex
        :param timestamp: Actual time of departure (ATD) of the historic flight,
            Unix timestamp in seconds.
            Optional, but it is recommended to include it.
        """
        params = PlaybackParams(flight_id, timestamp)
        response = await playback(
            self._factory.http.client,
            params,
            self._factory.http.json_headers,
            self._factory.http.auth,
        )
        return PlaybackResult(
            request=params,
            response=response,
        )


@dataclass_frozen
class PlaybackResult(
    APIResult[PlaybackParams],
    SupportsToDict[Playback],
    SupportsToPolars,
    SupportsWriteTable,
):
    def to_dict(self) -> Playback:
        return playback_parse(self.response).unwrap()

    def to_polars(self) -> pl.DataFrame:
        return playback_df(self.to_dict())

    def metadata(self) -> dict[str, Any]:
        """Extracts flight metadata from the response."""
        return playback_metadata_dict(
            self.to_dict()["result"]["response"]["data"]["flight"]
        )

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.playback.get_path(self.request.flight_id)
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class LiveFeedService(SupportsFetch[LiveFeedParams]):
    """Live feed service."""

    _factory: ServiceFactory

    @static_check_signature(LiveFeedParams)
    async def fetch(
        self,
        bounding_box: BoundingBox,
        stats: bool = False,
        limit: int = 1500,
        maxage: int = 14400,
        fields: set[LiveFeedField] = (
            lambda: {"flight", "reg", "route", "type"}
        )(),  # type: ignore
    ) -> LiveFeedResult:
        """Fetch the live feed.

        :param stats: Whether to include stats in the given area.
        :param limit: Maximum number of flights (should be set to 1500 for
            unauthorized users, 2000 for authorized users).
        :param maxage: Maximum time since last message update, seconds.
        :param fields: Fields to include. For unauthenticated users,
        a maximum of 4 fields can be included.
        When authenticated, `squawk`, `vspeed`, `airspace`, `logo_id` and `age`
        can be included.
        """
        params = LiveFeedParams(
            bounding_box=bounding_box,
            stats=stats,
            limit=limit,
            maxage=maxage,
            fields=fields,
        )
        response = await live_feed(
            self._factory.http.client,
            params.to_proto(),
            self._factory.http.grpc_headers,
        )
        # NOTE: serverTimeMs in the protobuf response would be more accurate
        timestamp = parse_server_timestamp(response) or get_current_timestamp()
        return LiveFeedResult(
            request=params,
            response=response,
            timestamp=timestamp,
        )


@dataclass_frozen
class LiveFeedResult(
    APIResult[LiveFeedParams],
    SupportsToProto[LiveFeedResponse],
    SupportsToDict[dict[str, Any]],
    SupportsToPolars,
    SupportsWriteTable,
):
    timestamp: IntTimestampS

    def to_proto(self) -> LiveFeedResponse:
        return parse_data(self.response.content, LiveFeedResponse).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)

    def to_polars(self) -> pl.DataFrame:
        return live_feed_df(self.to_proto())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.live_feed.get_path(self.timestamp)
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class LiveFeedPlaybackService(SupportsFetch[LiveFeedPlaybackParams]):
    """Live feed service."""

    _factory: ServiceFactory

    @static_check_signature(LiveFeedPlaybackParams)
    async def fetch(
        self,
        bounding_box: BoundingBox,
        stats: bool = False,
        limit: int = 1500,
        maxage: int = 14400,
        fields: set[LiveFeedField] = (
            lambda: {"flight", "reg", "route", "type"}
        )(),  # type: ignore
        timestamp: IntoTimestamp | Literal["now"] = "now",
        duration: int = 7,
        hfreq: int | None = None,
    ) -> LiveFeedPlaybackResult:
        """Fetch a playback of the live feed.

        :param stats: Whether to include stats in the given area.
        :param limit: Maximum number of flights (should be set to 1500 for
            unauthorized users, 2000 for authorized users).
        :param maxage: Maximum time since last message update, seconds.
        :param fields: Fields to include. For unauthenticated users, a maximum
        of 4 fields can be included.
        When authenticated, `squawk`, `vspeed`, `airspace`, `logo_id` and `age`
        can be included.
        :param timestamp: Start timestamp
        :param duration: Duration of prefetch, `floor(7.5*(multiplier))` seconds

        For 1x playback, this should be 7 seconds.
        :param hfreq: High frequency mode
        """
        params = LiveFeedPlaybackParams(
            bounding_box=bounding_box,
            stats=stats,
            limit=limit,
            maxage=maxage,
            fields=fields,
            timestamp=timestamp,
            duration=duration,
            hfreq=hfreq,
        )
        response = await live_feed_playback(
            self._factory.http.client,
            params.to_proto(),
            self._factory.http.grpc_headers,
        )
        return LiveFeedPlaybackResult(
            request=params,
            response=response,
        )


@dataclass_frozen
class LiveFeedPlaybackResult(
    APIResult[LiveFeedPlaybackParams],
    SupportsToProto[PlaybackResponse],
    SupportsToDict[dict[str, Any]],
    SupportsToPolars,
    SupportsWriteTable,
):
    def to_proto(self) -> PlaybackResponse:
        return parse_data(self.response.content, PlaybackResponse).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)

    def to_polars(self) -> pl.DataFrame:
        return live_feed_playback_df(self.to_proto())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.live_feed.get_path(self.request.timestamp)
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class AirportListService(SupportsFetch[AirportListParams]):
    """Airport list service."""

    _factory: ServiceFactory

    @static_check_signature(AirportListParams)
    async def fetch(
        self,
        airport: str,
        mode: Literal["arrivals", "departures", "ground"],
        page: int = 1,
        limit: int = 10,
        timestamp: IntoTimestamp | Literal["now"] | None = "now",
    ) -> AirportListResult:
        """Fetch the airport list.

        :param airport: IATA airport code (e.g. `HKG`)
        :param mode: arrivals, departures or on ground aircraft
        :param page: Page number
        :param limit: Number of results per page - use `100` if authenticated.
        :param timestamp: Show flights with STA before this timestamp
        """
        params = AirportListParams(
            airport=airport,
            mode=mode,
            page=page,
            limit=limit,
            timestamp=timestamp,
        )
        response = await airport_list(
            self._factory.http.client,
            params,
            self._factory.http.json_headers,
            self._factory.http.auth,
        )
        return AirportListResult(
            request=params,
            response=response,
        )


@dataclass_frozen
class AirportListResult(
    APIResult[AirportListParams],
    SupportsToDict[AirportList],
):
    def to_dict(self) -> AirportList:
        """Parse the response into a dictionary."""
        return airport_list_parse(self.response).unwrap()


@dataclass_frozen
class FindService(SupportsFetch[FindParams]):
    """Find service."""

    _factory: ServiceFactory

    @static_check_signature(FindParams)
    async def fetch(self, query: str, limit: int = 50) -> FindResult:
        """Fetch the find results.

        :param query: Airport, schedule (HKG-CDG), or aircraft.
        """
        params = FindParams(query=query, limit=limit)
        response = await find(
            self._factory.http.client,
            params,
            self._factory.http.json_headers,
            self._factory.http.auth,
        )
        return FindResult(
            request=params,
            response=response,
        )


@dataclass_frozen
class FindResult(
    APIResult[FindParams],
    SupportsToDict[Find],
):
    """A single result from the find API."""

    def to_dict(self) -> Find:
        """Parse the response into a dictionary."""
        return find_parse(self.response).unwrap()


@dataclass_frozen
class NearestFlightsService(SupportsFetch[NearestFlightsParams]):
    """Nearest flights service."""

    _factory: ServiceFactory

    @static_check_signature(NearestFlightsParams)
    async def fetch(
        self, lat: float, lon: float, radius: int = 10000, limit: int = 1500
    ) -> NearestFlightsResult:
        """Fetch the nearest flights.

        :param lat: Latitude, degrees, -90 to 90
        :param lon: Longitude, degrees, -180 to 180
        :param radius: Radius, metres
        :param limit: Maximum number of aircraft to return
        """
        request = NearestFlightsParams(
            lat=lat,
            lon=lon,
            radius=radius,
            limit=limit,
        )
        response = await nearest_flights(
            self._factory.http.client,
            request.to_proto(),
            self._factory.http.grpc_headers,
        )
        timestamp = parse_server_timestamp(response) or get_current_timestamp()
        return NearestFlightsResult(
            request=request,
            response=response,
            timestamp=timestamp,
        )


@dataclass_frozen
class NearestFlightsResult(
    APIResult[NearestFlightsParams],
    SupportsToProto[NearestFlightsResponse],
    SupportsToDict[dict[str, Any]],
    SupportsToPolars,
    SupportsWriteTable,
):
    timestamp: IntTimestampS

    def to_proto(self) -> NearestFlightsResponse:
        return parse_data(
            self.response.content, NearestFlightsResponse
        ).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)

    def to_polars(self) -> pl.DataFrame:
        return nearest_flights_df(self.to_proto())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.nearest_flights.get_path(
                self.request.lon, self.request.lat, self.timestamp
            )
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class LiveFlightsStatusService(SupportsFetch[LiveFlightsStatusParams]):
    """Live flights status service."""

    _factory: ServiceFactory

    @static_check_signature(LiveFlightsStatusParams)
    async def fetch(
        self, flight_ids: Sequence[IntoFlightId]
    ) -> LiveFlightsStatusResult:
        """Fetch the live flights status.

        :param flight_ids: List of flight IDs to get status for
        """
        request = LiveFlightsStatusParams(flight_ids=flight_ids)
        response = await live_flights_status(
            self._factory.http.client,
            request.to_proto(),
            self._factory.http.grpc_headers,
        )
        timestamp = parse_server_timestamp(response) or get_current_timestamp()
        return LiveFlightsStatusResult(
            request=request,
            response=response,
            timestamp=timestamp,
        )


@dataclass_frozen
class LiveFlightsStatusResult(
    APIResult[LiveFlightsStatusParams],
    SupportsToProto[LiveFlightsStatusResponse],
    SupportsToDict[dict[str, Any]],
    SupportsToPolars,
    SupportsWriteTable,
):
    timestamp: IntTimestampS

    def to_proto(self) -> LiveFlightsStatusResponse:
        return parse_data(
            self.response.content, LiveFlightsStatusResponse
        ).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)

    def to_polars(self) -> pl.DataFrame:
        return live_flights_status_df(self.to_proto())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.live_flights_status.get_path(self.timestamp)
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class FollowFlightService:
    """Follow flight service for real-time streaming."""

    _factory: ServiceFactory

    @static_check_signature(FollowFlightParams)
    async def stream(
        self,
        flight_id: IntoFlightId,
        restriction_mode: (
            RestrictionVisibility.ValueType | str | bytes
        ) = RestrictionVisibility.NOT_VISIBLE,
    ) -> AsyncGenerator[FollowFlightResult, None]:
        """Stream real-time flight updates.

        :param flight_id: Flight ID to fetch details for.
        Must be live, or the response will contain an empty `DATA` frame error.
        :param restriction_mode: [FAA LADD](https://www.faa.gov/pilots/ladd)
            visibility mode.
        """
        request = FollowFlightParams(
            flight_id=flight_id, restriction_mode=restriction_mode
        )
        async for response in follow_flight_stream(
            self._factory.http.client,
            request.to_proto(),
            self._factory.http.grpc_headers,
        ):
            yield FollowFlightResult(
                request=request,
                response=response,
            )


@dataclass_frozen
class FollowFlightResult(
    SupportsToProto[FollowFlightResponse],
    SupportsToDict[dict[str, Any]],
):
    request: FollowFlightParams
    response: bytes

    def to_proto(self) -> FollowFlightResponse:
        return parse_data(self.response, FollowFlightResponse).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)


@dataclass_frozen
class TopFlightsService(SupportsFetch[TopFlightsParams]):
    """Top flights service."""

    _factory: ServiceFactory

    @static_check_signature(TopFlightsParams)
    async def fetch(self, limit: int = 10) -> TopFlightsResult:
        """Fetch the top flights.

        :param limit: Maximum number of top flights to return (1-10)
        """
        request = TopFlightsParams(limit=limit)
        response = await top_flights(
            self._factory.http.client,
            request.to_proto(),
            self._factory.http.grpc_headers,
        )
        timestamp = parse_server_timestamp(response) or get_current_timestamp()
        return TopFlightsResult(
            request=request,
            response=response,
            timestamp=timestamp,
        )


@dataclass_frozen
class TopFlightsResult(
    APIResult[TopFlightsParams],
    SupportsToProto[TopFlightsResponse],
    SupportsToDict[dict[str, Any]],
    SupportsToPolars,
    SupportsWriteTable,
):
    timestamp: IntTimestampS

    def to_proto(self) -> TopFlightsResponse:
        return parse_data(self.response.content, TopFlightsResponse).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)

    def to_polars(self) -> pl.DataFrame:
        return top_flights_df(self.to_proto())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.top_flights.get_path(self.timestamp)
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class FlightDetailsService(SupportsFetch[FlightDetailsParams]):
    """Flight details service."""

    _factory: ServiceFactory

    @static_check_signature(FlightDetailsParams)
    async def fetch(
        self,
        flight_id: IntoFlightId,
        restriction_mode: (
            RestrictionVisibility.ValueType | str | bytes
        ) = RestrictionVisibility.NOT_VISIBLE,
        verbose: bool = True,
    ) -> FlightDetailsResult:
        """Fetch flight details.

        :param flight_id: Flight ID to fetch details for. Must be live, or the
            response will contain an empty `DATA` frame error.
        :param restriction_mode: [FAA LADD](https://www.faa.gov/pilots/ladd)
            visibility mode.
        :param verbose: Whether to include
            [fr24.proto.v1_pb2.FlightDetailsResponse.flight_plan]
            and [fr24.proto.v1_pb2.FlightDetailsResponse.aircraft_details] in
            the response.
        """
        request = FlightDetailsParams(
            flight_id=flight_id,
            restriction_mode=restriction_mode,
            verbose=verbose,
        )
        response = await flight_details(
            self._factory.http.client,
            request.to_proto(),
            self._factory.http.grpc_headers,
        )
        timestamp = parse_server_timestamp(response) or get_current_timestamp()
        return FlightDetailsResult(
            request=request,
            response=response,
            timestamp=timestamp,
        )


@dataclass_frozen
class FlightDetailsResult(
    APIResult[FlightDetailsParams],
    SupportsToProto[FlightDetailsResponse],
    SupportsToDict[dict[str, Any]],
    SupportsToPolars,
    SupportsWriteTable,
):
    timestamp: IntTimestampS

    def to_proto(self) -> FlightDetailsResponse:
        return parse_data(self.response.content, FlightDetailsResponse).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)

    def to_polars(self) -> pl.DataFrame:
        return flight_details_df(self.to_proto())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.flight_details.get_path(
                self.request.flight_id, self.timestamp
            )
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )


@dataclass_frozen
class PlaybackFlightService(SupportsFetch[PlaybackFlightParams]):
    """Playback flight service."""

    _factory: ServiceFactory

    @static_check_signature(PlaybackFlightParams)
    async def fetch(
        self, flight_id: IntoFlightId, timestamp: IntoTimestamp
    ) -> PlaybackFlightResult:
        """Fetch playback flight details.

        :param flight_id: Flight ID to fetch details for. Must not be live, or
            the response will contain an empty `DATA` frame error.
        :param timestamp: Actual time of departure (ATD) of the historic flight
        """
        request = PlaybackFlightParams(
            flight_id=flight_id,
            timestamp=timestamp,
        )
        response = await playback_flight(
            self._factory.http.client,
            request.to_proto(),
            self._factory.http.grpc_headers,
        )
        return PlaybackFlightResult(
            request=request,
            response=response,
        )


@dataclass_frozen
class PlaybackFlightResult(
    APIResult[PlaybackFlightParams],
    SupportsToProto[PlaybackFlightResponse],
    SupportsToDict[dict[str, Any]],
    SupportsToPolars,
    SupportsWriteTable,
):
    def to_proto(self) -> PlaybackFlightResponse:
        return parse_data(
            self.response.content, PlaybackFlightResponse
        ).unwrap()

    def to_dict(self) -> dict[str, Any]:
        return MessageToDict(self.to_proto(), preserving_proto_field_name=True)

    def to_polars(self) -> pl.DataFrame:
        return playback_flight_df(self.to_proto())

    def write_table(
        self,
        file: WriteLocation,
        *,
        format: TabularFileFmt = "parquet",
        when_file_exists: FileExistsBehaviour = "backup",
    ) -> None:
        if isinstance(file, FR24Cache):
            file = file.playback_flight.get_path(
                self.request.flight_id, self.request.timestamp
            )
        write_table(
            self, file, format=format, when_file_exists=when_file_exists
        )
