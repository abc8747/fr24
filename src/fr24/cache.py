from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from platformdirs import user_cache_dir

from .types.cache import (
    flight_details_schema,
    flight_list_schema,
    live_feed_schema,
    live_flights_status_schema,
    nearest_flights_schema,
    playback_flight_schema,
    playback_track_schema,
    top_flights_schema,
)
from .utils import (
    BarePath,
    dataclass_frozen,
    scan_table,
    to_flight_id,
    to_unix_timestamp,
)

if TYPE_CHECKING:
    from typing import Generator

    import polars as pl
    from typing_extensions import Literal

    from .types import IntoFlightId, IntoTimestamp
    from .types.cache import TabularFileFmt
    from .types.isqx import LatitudeDeg, LongitudeDeg


PATH_CACHE = Path(user_cache_dir("fr24"))


class FR24Cache:
    @classmethod
    def default(cls) -> FR24Cache:
        """Create a cache in the
        [default directory](../usage/cli.md#directories)."""
        return cls(PATH_CACHE)

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        flight_list_dir = self.path / "flight_list"

        self.flight_list = FlightListBy(
            reg=FlightListRegCache(Collection(flight_list_dir / "reg")),
            flight=FlightListFlightCache(
                Collection(flight_list_dir / "flight")
            ),
        )
        self.playback = PlaybackCache(Collection(self.path / "playback"))
        self.live_feed = TimestampedCache(
            Collection(self.path / "feed"), schema=live_feed_schema
        )
        self.nearest_flights = NearestFlightsCache(
            Collection(self.path / "nearest_flights")
        )
        self.live_flights_status = TimestampedCache(
            Collection(self.path / "live_flights_status"),
            schema=live_flights_status_schema,
        )
        self.top_flights = TimestampedCache(
            Collection(self.path / "top_flights"), schema=top_flights_schema
        )
        self.flight_details = FlightDetailsCache(
            Collection(self.path / "flight_details"),
            schema=flight_details_schema,
        )
        self.playback_flight = FlightDetailsCache(
            Collection(self.path / "playback_flight"),
            schema=playback_flight_schema,
        )
        # mkdir not necessary: write_table will create them automatically


class CacheLike(Protocol):
    collection: Collection

    def get_path(self, *args: Any, **kwargs: Any) -> BarePath:
        """Get the path to the cached file."""
        ...

    def scan_table(self, *args: Any, **kwargs: Any) -> pl.LazyFrame:
        """Lazily load a file from this collection."""
        ...


@dataclass_frozen
class GlobMixin(CacheLike):
    def glob(self, pattern: str) -> Generator[File, None, None]:
        """Yield all scannable files matching the given pattern."""
        for fp in self.collection.path.glob(pattern):
            yield File(fp)


@dataclass_frozen
class FlightListRegCache(GlobMixin):
    collection: Collection

    def get_path(self, reg: str) -> BarePath:
        return self.collection.new_bare_path(reg.upper())

    def scan_table(
        self, reg: str, *, format: TabularFileFmt = "parquet"
    ) -> pl.LazyFrame:
        """Lazily load a flight list file from this collection.

        :param reg: The aircraft registration number (e.g. `B-HUJ`).
        """
        return scan_table(
            self.get_path(reg), format=format, schema=flight_list_schema
        )


@dataclass_frozen
class FlightListFlightCache(GlobMixin):
    collection: Collection

    def get_path(self, flight: str) -> BarePath:
        return self.collection.new_bare_path(flight.upper())

    def scan_table(
        self, flight: str, *, format: TabularFileFmt = "parquet"
    ) -> pl.LazyFrame:
        """Lazily load a flight list file from this collection.

        :param flight: The flight number (e.g. `CX8747`).
        """
        return scan_table(
            self.get_path(flight), format=format, schema=flight_list_schema
        )


@dataclass_frozen
class FlightListBy:
    reg: FlightListRegCache
    flight: FlightListFlightCache

    def __call__(
        self, kind: Literal["reg", "flight"]
    ) -> FlightListRegCache | FlightListFlightCache:
        return getattr(self, kind)  # type: ignore


@dataclass_frozen
class PlaybackCache(GlobMixin):
    collection: Collection

    def get_path(self, flight_id: IntoFlightId) -> BarePath:
        ident = f"{to_flight_id(flight_id):0x}".upper()
        return self.collection.new_bare_path(ident)

    def scan_table(
        self, flight_id: IntoFlightId, *, format: TabularFileFmt = "parquet"
    ) -> pl.LazyFrame:
        """Lazily load a playback file.

        :param flight_id: The flight ID of the record.
        """
        return scan_table(
            self.get_path(flight_id),
            format=format,
            schema=playback_track_schema,
        )


# not allowing `now` literal for cache because it doesn't make sense
@dataclass_frozen
class TimestampedCache(GlobMixin):
    collection: Collection
    schema: dict[str, pl.DataType] | None

    def get_path(self, timestamp: IntoTimestamp | str) -> BarePath:
        ts = to_unix_timestamp(timestamp)
        if ts is None or ts == "now":
            raise ValueError(f"invalid timestamp for cache: {timestamp}")
        return self.collection.new_bare_path(str(ts))

    def scan_table(
        self,
        timestamp: IntoTimestamp | str,
        *,
        format: TabularFileFmt = "parquet",
    ) -> pl.LazyFrame:
        """Lazily load a timestamped file.

        :param timestamp: A timestamp-like object, see
            [fr24.utils.to_unix_timestamp][]. The `now` literal is not allowed.
        """
        return scan_table(
            self.get_path(timestamp), format=format, schema=self.schema
        )


@dataclass_frozen
class NearestFlightsCache(GlobMixin):
    collection: Collection

    def get_path(
        self,
        lon: LongitudeDeg[float],
        lat: LatitudeDeg[float],
        timestamp: IntoTimestamp | str,
    ) -> BarePath:
        lon6 = int(lon * 1e6)
        lat6 = int(lat * 1e6)
        ts = to_unix_timestamp(timestamp)
        if ts is None or ts == "now":
            raise ValueError(f"invalid timestamp for cache: {timestamp}")
        return self.collection.new_bare_path(f"{lon6}_{lat6}_{ts}")

    def scan_table(
        self,
        lon: LongitudeDeg[float],
        lat: LatitudeDeg[float],
        timestamp: IntoTimestamp | str,
        *,
        format: TabularFileFmt = "parquet",
    ) -> pl.LazyFrame:
        """Lazily load a nearest flights file.

        :param lat: Latitude of the center point.
        :param lon: Longitude of the center point.
        :param timestamp: A timestamp-like object, see
            [fr24.utils.to_unix_timestamp][]. The `now` literal is not allowed.
        """
        return scan_table(
            self.get_path(lon, lat, timestamp),
            format=format,
            schema=nearest_flights_schema,
        )


@dataclass_frozen
class FlightDetailsCache(GlobMixin):
    collection: Collection
    schema: dict[str, pl.DataType] | None

    def get_path(
        self, flight_id: IntoFlightId, timestamp: IntoTimestamp | str
    ) -> BarePath:
        fid = f"{to_flight_id(flight_id):0x}".upper()
        ts = to_unix_timestamp(timestamp)
        if ts is None or ts == "now":
            raise ValueError(f"invalid timestamp for cache: {timestamp}")
        return self.collection.new_bare_path(f"{fid}_{ts}")

    def scan_table(
        self,
        flight_id: IntoFlightId,
        timestamp: IntoTimestamp | str,
        *,
        format: TabularFileFmt = "parquet",
    ) -> pl.LazyFrame:
        """Lazily load a flight details file.

        :param flight_id: The flight ID of the record.
        :param timestamp: A timestamp-like object, see
            [fr24.utils.to_unix_timestamp][]. The `now` literal is not allowed.
        """
        return scan_table(
            self.get_path(flight_id, timestamp),
            format=format,
            schema=self.schema,
        )


@dataclass_frozen
class Collection:
    """A directory containing scannable files."""

    path: Path

    def new_bare_path(self, ident: str) -> BarePath:
        """Returns the bare path (without the file extension) to the file."""
        return BarePath(self.path / ident)


class File(Path):
    @property
    def format(self) -> TabularFileFmt:
        # TODO: perform validation, though it is not critical
        return self.suffix[1:]  # type: ignore

    def scan_table(self) -> pl.LazyFrame:
        """Lazily load this file."""
        return scan_table(self, format=self.format)
