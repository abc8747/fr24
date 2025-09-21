from __future__ import annotations

import email.utils
import logging
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterator,
    Literal,
    NamedTuple,
    Protocol,
    Sequence,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import (
    assert_never,
    dataclass_transform,
    runtime_checkable,
)

dataclass_opts: dict[str, bool] = {}
if sys.version_info >= (3, 10):
    dataclass_opts["slots"] = True

if TYPE_CHECKING:
    from typing import NoReturn

    import httpx
    import polars as pl
    from typing_extensions import TypeAlias

    from .types import (
        IntFlightId,
        IntoFlightId,
        IntoTimestamp,
        IntTimestampS,
        StrFlightIdHex,
    )
    from .types.cache import TabularFileFmt

    _D = TypeVar("_D")

    @dataclass_transform(frozen_default=True)
    def dataclass_frozen(cls: type[_D]) -> type[_D]: ...
else:
    dataclass_frozen = dataclass(**dataclass_opts)

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;"
    "q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, zstd",  # prior to v0.2.0, this was `br`
    "Origin": "https://www.flightradar24.com",
    "Connection": "keep-alive",
    "Referer": "https://www.flightradar24.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-GPC": "1",
    "TE": "trailers",
}


@overload
def to_unix_timestamp(
    timestamp: IntoTimestamp | Literal["now"] | str,
) -> IntTimestampS | Literal["now"]: ...


@overload
def to_unix_timestamp(timestamp: None) -> None: ...


def to_unix_timestamp(
    timestamp: IntoTimestamp | str | Literal["now"] | None,
) -> IntTimestampS | Literal["now"] | None:
    """Casts timestamp-like object to a Unix timestamp in integer seconds."""
    if isinstance(timestamp, str):
        # TODO(abrah): should we eagerly return the current timestamp just like
        # `pd.Timestamp("now")`? we might want to defer this to the caller.
        if timestamp == "now":
            return "now"
        # try to interpret string as integer timestamp in seconds first
        try:
            return to_unix_timestamp(int(timestamp))
        except ValueError:
            pass
        # otherwise assume it's a format that `chronos` understands
        import polars as pl

        try:
            dt = pl.Series(values=(timestamp,)).str.to_datetime().item(0)
        except pl.exceptions.ComputeError:
            raise ValueError(
                f"invalid ISO8601/chronos timestamp: {timestamp!r}"
            )
        return int(dt.timestamp())
    if isinstance(timestamp, datetime):
        return int(timestamp.timestamp())
    if isinstance(timestamp, int):
        if timestamp > 4102462800:  # 2100-01-01
            raise ValueError(
                f"timestamp {timestamp} is too large, "
                "should be in seconds, not milliseconds"
            )
        return timestamp
    return None


def get_current_timestamp() -> IntTimestampS:
    """Returns the current Unix timestamp in seconds."""
    return int(time.time())


def parse_server_timestamp(
    response: httpx.Response,
) -> IntTimestampS | None:
    server_date: str = response.headers.get("date")
    if server_date is not None:
        return int(email.utils.parsedate_to_datetime(server_date).timestamp())
    return None


def to_flight_id(flight_id: IntoFlightId) -> IntFlightId:
    if isinstance(flight_id, (str, bytes)):
        return int(flight_id, 16)
    return flight_id


def to_flight_id_hex(flight_id: IntoFlightId) -> StrFlightIdHex:
    """Converts flight ID to a hex string."""
    if isinstance(flight_id, str):
        return flight_id.lower().removeprefix("0x")
    if isinstance(flight_id, bytes):
        flight_id = flight_id.decode()
    return f"{flight_id:x}"


@dataclass_frozen
class BarePath:
    path: Path


FileLike = Union[str, Path, IO[bytes], BarePath]


def format_bare_path(path: BarePath, format: TabularFileFmt) -> Path:
    if format == "parquet":
        suffix = ".parquet"
    elif format == "csv":
        suffix = ".csv"
    else:
        raise ValueError(f"unsupported format: `{format}`")
    return path.path.with_suffix(suffix)


FileExistsBehaviour: TypeAlias = Literal["backup", "error", "overwrite"]


def _handle_existing_file(
    path: Path, when_file_exists: FileExistsBehaviour
) -> None:
    if not path.exists():
        return
    if when_file_exists == "backup":
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        backup_path = path.with_suffix(f"{path.suffix}.bkp.{timestamp}")
        path.rename(backup_path)
        logger.info(
            f"file `{path}` already exists, moved it to `{backup_path}`"
        )
    elif when_file_exists == "error":
        raise FileExistsError(f"refused to overwrite existing file at `{path}`")
    elif when_file_exists == "overwrite":
        pass
    else:
        assert_never(when_file_exists)


def write_table(
    result: SupportsToPolars,
    file: FileLike,
    *,
    format: TabularFileFmt = "parquet",
    when_file_exists: FileExistsBehaviour = "backup",
    **kwargs: Any,
) -> None:
    """Writes the table as the specified format via polars.

    :param file: File path or writable file-like object. The path will be given
        an appropriate suffix if it is a [BarePath][fr24.utils.BarePath].
    """

    if isinstance(file, BarePath):
        file = format_bare_path(file, format)
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file, Path):
        _handle_existing_file(file, when_file_exists)
        file.parent.mkdir(parents=True, exist_ok=True)

    data = result.to_polars()
    if format == "parquet":
        # NOTE: saving metadata with polars is not yet implemented
        # this means that useful unstructured metadata (e.g. flight details)
        # cannot be saved without extra pyarrow dependency
        # https://github.com/pola-rs/polars/issues/5117
        data.write_parquet(file, **kwargs)
    elif format == "csv":
        data.write_csv(file, **kwargs)
    else:
        raise ValueError(f"unsupported format: `{format}`")
    logger.info(f"wrote {data.height} rows to `{file}`")


def scan_table(
    file: FileLike,
    *,
    format: TabularFileFmt = "parquet",
    schema: dict[str, pl.DataType] | None = None,
) -> pl.LazyFrame:
    """
    Reads the table as the specified format via polars.

    :param file: File path or readable file-like object. The path will be given
        an appropriate suffix if it is a [BarePath][fr24.utils.BarePath].
    :param schema: The schema to enforce when reading the table. For CSV files,
        this should be specified to properly parse datetimes from strings.
    """
    import polars as pl

    if isinstance(file, BarePath):
        file = format_bare_path(file, format)

    if format == "parquet":
        return pl.scan_parquet(file, schema=schema)
    elif format == "csv":
        return pl.scan_csv(file, schema=schema)
    else:
        raise ValueError(f"unsupported format: `{format}`")


#
# important traits to perform conversions to other formats
# Into<TypedDict | google.protobuf.Message | pl.DataFrame>
# subclassing is not necessary, but recommended for static type checking
#

DictT_co = TypeVar("DictT_co", covariant=True)
"""The dictionary representation of an object, e.g. `TypedDict`."""


@runtime_checkable
class SupportsToDict(Protocol[DictT_co]):
    def to_dict(self) -> DictT_co:
        """Converts the object into a dictionary."""
        ...


@runtime_checkable
class SupportsToPolars(Protocol):
    def to_polars(self) -> pl.DataFrame:
        """Converts the object into a polars dataframe."""
        ...


# instead of raising exceptions:
# - in `fr24.json`: return a result type that stores the response body or any
#   errors
# - in `fr24.grpc`: return a result type that stores the parsed protocol buffer
#   or any gRPC errors

T = TypeVar("T")
E = TypeVar("E")


@dataclass_frozen
class Ok(Generic[T]):
    _value: T

    def ok(self) -> T:
        return self._value

    def err(self) -> None:
        return None

    def is_ok(self) -> Literal[True]:
        return True

    def is_err(self) -> Literal[False]:
        return False

    def unwrap(self) -> T:
        return self._value


@dataclass_frozen
class Err(Generic[E]):
    _value: E

    def ok(self) -> None:
        return None

    def err(self) -> E:
        return self._value

    def is_ok(self) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    def unwrap(self) -> NoReturn:
        raise UnwrapError(
            self, f"called `Result.unwrap()` on errored result: {self._value!r}"
        )


class UnwrapError(Exception):
    def __init__(self, err: Any, message: str) -> None:
        self._err = err
        super().__init__(message)

    @property
    def err(self) -> Any:
        return self._err


Result: TypeAlias = Union[Ok[T], Err[E]]
"""A type that represents either success (`Ok`) or failure (`Err`)."""

M = TypeVar("M", bound=Callable[..., Any])


def static_check_signature(dataclass: Any) -> Callable[[M], M]:
    '''Marker to signal the static analyser that the decorated method or
    function should be checked against the signature of the given dataclass.

    Many of our low level APIs use 1) parameters stored in a single flat
    dataclass, and 2) functions that take in this dataclass:
    ```py
    @dataclass
    class LiveFeedParams:
        bbox_south: float
        """Latitude, minimum, degrees"""
        bbox_north: float
        bbox_west: float
        bbox_east: float
        flight_id: int
        # ... other params ...

    def live_feed(params: LiveFeedParams, ...):
        ...
    ```
    but service methods and CLIs expect a flat signature:
    ```py
    from fr24.utils import static_check_signature

    @static_check_signature(LiveFeedParams)
    def live_feed_cli(
        bbox_south: float,
        bbox_north: float,
        bbox_west: float,
        bbox_east: float,
        flight_id: int
        # ... other params ...
    ):
        """:param bbox_south: The southern latitude of the bounding box.
        ..."""
        ...
    ```
    `./scripts/check_signature.py` uses static analysis to:

    1. scan for all uses of the decorator
    2. for each member of the dataclass, collect all docstrings, members names
       and types
    3. for each argument of the decorated method, parse the sphinx docstring,
       names and types
    4. compare them.
    '''

    def decorator(method: M) -> M:
        return method

    return decorator


# for use in cli
_SPHINX_PARAM = re.compile(r"\s*:param\s+(?P<name>\w+):\s*(?P<doc>.*)")


class ParamDetail(NamedTuple):
    name: str
    description: str


@dataclass
class SphinxParser:
    """A poor man's parser for Sphinx docstrings and its `:param:` directive."""

    text: str
    name: str | None = None
    doc_lines: list[str] = field(default_factory=list)

    def __iter__(self) -> Iterator[str | ParamDetail]:
        for line in self.text.splitlines():
            if match := _SPHINX_PARAM.match(line):
                if self.name is not None:
                    yield ParamDetail(
                        self.name, _join_doc_lines(self.doc_lines)
                    )
                elif self.doc_lines:  # header
                    yield _join_doc_lines(self.doc_lines)
                self.name = match.group("name")
                self.doc_lines = [match.group("doc")]
            else:
                self.doc_lines.append(line)
        if self.name:
            yield ParamDetail(self.name, _join_doc_lines(self.doc_lines))
        else:
            yield _join_doc_lines(self.doc_lines)


def _join_doc_lines(doc_frags: Sequence[str]) -> str:
    return " ".join(line.strip() for line in doc_frags)
