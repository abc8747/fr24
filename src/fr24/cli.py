from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise SystemExit("fr24 CLI requires Python 3.10 or newer. ")
    # technically 3.9 works but lack of X | Y is annoying
    # besides, typer>0.26 requires py3.10+


import asyncio
import inspect
import logging
from collections.abc import Callable, Sequence
from collections.abc import Set as AbstractSet
from pathlib import Path
from typing import (
    IO,
    Annotated,
    Any,
    Literal,
    NamedTuple,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

import typer
from rich.console import Console
from rich.logging import RichHandler

from . import BBOX_FRANCE_UIR, FR24, BoundingBox, FR24Cache, service
from .cache import PATH_CACHE
from .configuration import FP_CONFIG_FILE, PATH_CONFIG
from .service import LiveFeedPlaybackResult, LiveFeedResult, SupportsWriteTable
from .types import IntFlightId, IntoFlightId, IntoTimestamp
from .types.cache import TabularFileFmt
from .types.grpc import LiveFeedField
from .types.isqx import TimestampS
from .utils import (
    FileExistsBehaviour,
    ParamDetail,
    SphinxParser,
    to_flight_id,
    to_unix_timestamp,
)

stderr = Console(stderr=True)
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=stderr)],
)
logger = logging.getLogger(__name__)
app = typer.Typer(pretty_exceptions_show_locals=False, no_args_is_help=True)


@app.command()
def dirs() -> None:
    """Shows relevant directories"""
    stderr.print(f"Config: {PATH_CONFIG}")
    stderr.print(f" Cache: {PATH_CACHE}")


@app.command()
def tui() -> None:
    """Starts the TUI"""
    from .tui.tui import main as tui_main

    tui_main()


app_auth = typer.Typer()
app.add_typer(
    app_auth,
    name="auth",
    no_args_is_help=True,
    help="Commands for authentication",
)


@app_auth.command()
def show() -> None:
    """Shows authentication status"""

    ERR_MSG = (
        "[bold yellow]warning[/bold yellow]: not authenticated\n"
        "[bold cyan]help[/bold cyan]: "
        "provide your credentials in environment variables, either:\n"
        "- `fr24_username` and `fr24_password`, or\n"
        "- `fr24_subscription_key` and `fr24_token`\n"
        "[bold cyan]help[/bold cyan]: "
        "alternatively, create a template configuration file "
        f"at `{FP_CONFIG_FILE}` with the command `fr24 auth create`."
    )

    async def show_() -> None:
        async with FR24() as fr24:
            await fr24.login()
            if fr24.http.auth is None:
                stderr.print(ERR_MSG)
            else:
                stderr.print("[bold green]success[/bold green]: authenticated")
                stderr.print(fr24.http.auth)

    asyncio.run(show_())


@app_auth.command()
def create(
    force: Annotated[
        bool,
        typer.Option(help="Overwrite existing configuration file"),
    ] = False,
) -> None:
    """Create a template config file in the user config directory"""
    import shutil

    if FP_CONFIG_FILE.exists() and FP_CONFIG_FILE.is_file() and not force:
        logger.error(
            f"{FP_CONFIG_FILE} already exists, use `--force` to overwrite"
        )
        return

    fp_config_template = (
        Path(__file__).parent.parent.parent / "fr24.example.conf"
    )
    FP_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(fp_config_template, FP_CONFIG_FILE)
    stderr.print(
        "[bold green]success[/bold green]: "
        f"created template configuration file at {FP_CONFIG_FILE}"
    )


def get_console(path: Path | IO[bytes] | None) -> Console:
    return Console(stderr=path is not None and not isinstance(path, Path))


#
# generate commands dynamically
#

# in the future, we will allow writing raw data (bytes, proto, json, etc.)
# add `raw` to the `Fmts` and update the defaults accordingly.
Fmts: TypeAlias = tuple[Literal["table"], ...]
FMT_DEFAULT: Fmts = ("table",)

P = ParamSpec("P")
S_co = TypeVar("S_co", bound=SupportsWriteTable, covariant=True)


class ServiceCommand(Protocol[P, S_co]):
    __name__: str

    async def __call__(
        self, fr24: FR24, *args: P.args, **kwargs: P.kwargs
    ) -> S_co: ...


def register_command(
    app: typer.Typer,
    signature_from: Callable[P, Any],
    *,
    fmts: Fmts = FMT_DEFAULT,
) -> Callable[[ServiceCommand[P, SupportsWriteTable]], Callable[P, None]]:
    def decorator(command_func: ServiceCommand[P, S_co]) -> Callable[P, None]:
        async def command_body(*args: P.args, **kwargs: P.kwargs) -> None:
            path = kwargs.pop("output")
            if path == "-":
                path = sys.stdout.buffer
            elif path == "cache":
                path = FR24Cache.default()
            output_format = kwargs.pop("format")
            when_file_exists = kwargs.pop("when_file_exists")
            if "fields" in kwargs:
                kwargs["fields"] = set(kwargs["fields"])

            async with FR24() as fr24:
                await fr24.login()
                result = await command_func(fr24, *args, **kwargs)
                result.write_table(
                    path,  # type: ignore
                    format=output_format,  # type: ignore
                    when_file_exists=when_file_exists,  # type: ignore
                )

        def cli_command(*args: P.args, **kwargs: P.kwargs) -> None:
            asyncio.run(command_body(*args, **kwargs))

        cli_command.__signature__, cli_command.__doc__ = create_typer_signature(  # type: ignore
            signature_from=signature_from,
            fmts=fmts,
            default_filename=command_func.__name__,
        )
        app.command(name=command_func.__name__.replace("_", "-"))(cli_command)
        return cli_command

    return decorator


class TyperSignature(NamedTuple):
    signature: inspect.Signature
    command_description: str | None


def create_typer_signature(
    signature_from: Any, *, fmts: Fmts, default_filename: str
) -> TyperSignature:
    hints: dict[str, type] = get_type_hints(signature_from, include_extras=True)
    sig = inspect.signature(signature_from)
    command_description: str = ""
    param_docs: dict[str, ParamDetail] = {}
    if docstring := signature_from.__doc__:
        for doc_fragment in SphinxParser(docstring):
            if isinstance(doc_fragment, str):
                command_description += doc_fragment
            elif isinstance(doc_fragment, ParamDetail):
                param_docs[doc_fragment.name] = doc_fragment
    new_params = []
    for param in sig.parameters.values():
        if param.name == "self":
            continue
        detail = param_docs.get(param.name)
        help_text = detail.description if detail else None
        type_hint = hints[param.name]
        param_overrides = get_typer_parameter_override(type_hint)
        kwargs = param_overrides.get("kwargs", {})
        if param.default is inspect.Parameter.empty:
            kwargs["show_default"] = False
        if extra_help := param_overrides.get("extra_help"):
            help_text = (
                extra_help if help_text is None else f"{help_text}{extra_help}"
            )
        new_annotation = Annotated[  # type: ignore
            param_overrides.get("hint") or type_hint,
            typer.Option(help=help_text, **kwargs),
        ]
        default = param.default
        if isinstance(default, AbstractSet):
            default = sorted(default)  # to make the cli output determinsitic
        new_params.append(
            param.replace(annotation=new_annotation, default=default)
        )
    if fmts:
        default_fmt = "parquet" if "table" in fmts else "json"
        new_params.extend(
            [
                inspect.Parameter(
                    "output",
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=Annotated[
                        str,
                        typer.Option(
                            "-o",
                            "--output",
                            help=(
                                "Save results to a specific filepath. "
                                "If `-`, results will be printed to stdout. "
                                "If `cache`, results will be saved to the "
                                "default cache."
                            ),
                            parser=parse_output,
                            metavar="filepath|cache|-",
                        ),
                    ],
                    default=f"{default_filename}.{default_fmt}",
                ),
                inspect.Parameter(
                    "format",
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=Annotated[
                        TabularFileFmt,
                        typer.Option("-f", "--format", help="Output format"),
                    ],
                    default=default_fmt,
                ),
                inspect.Parameter(
                    "when_file_exists",
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=Annotated[
                        FileExistsBehaviour,
                        typer.Option(
                            help="Action when output file path already exists."
                        ),
                    ],
                    default="backup",
                ),
            ]
        )
    return TyperSignature(
        inspect.Signature(parameters=new_params, return_annotation=None),
        command_description or None,
    )


def parse_bounding_box(value: str) -> BoundingBox:
    try:
        south, north, west, east = map(float, value.split(","))
    except ValueError as exc:
        raise typer.BadParameter(
            "expected four comma-separated numbers"
        ) from exc
    return BoundingBox(south, north, west, east)


def parse_timestamp(value: str) -> TimestampS[int] | Literal["now"]:
    try:
        return to_unix_timestamp(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def parse_past_timestamp(value: str) -> TimestampS[int]:
    timestamp = parse_timestamp(value)
    if timestamp == "now":
        raise typer.BadParameter(
            "this command does not support `now` as a timestamp."
        )
    return timestamp


def parse_flight_id(value: str) -> IntFlightId:
    try:
        return to_flight_id(value)
    except ValueError as exc:
        raise typer.BadParameter(f"invalid flight ID: {value!r}") from exc


def parse_output(value: str) -> Path | Literal["cache", "-"]:
    if value == "-" or value == "cache":
        return value
    path = Path(value).resolve()
    if path.is_dir():
        raise typer.BadParameter(
            f"expected a file path, got a directory: {path!r}"
        )
    return path


def parse_live_feed_field(value: str) -> LiveFeedField:
    if value not in get_args(LiveFeedField):
        raise typer.BadParameter(f"invalid live feed field: {value!r}")
    return value  # type: ignore


class TyperOptionKwargs(TypedDict, total=False):
    parser: Callable[[str], object]
    metavar: str
    show_default: bool


class TyperParamOverride(TypedDict, total=False):
    hint: type
    kwargs: TyperOptionKwargs
    extra_help: str


_IntoTimestampArgs = set(get_args(IntoTimestamp))
_IntoFlightIdArgs = set(get_args(IntoFlightId))


def get_typer_parameter_override(type_: type) -> TyperParamOverride:
    origin = get_origin(type_)
    type_args = set(get_args(type_))
    if type_ is BoundingBox:
        example = ", ".join(f"{v:.1f}" for v in BBOX_FRANCE_UIR)
        return {
            "hint": str,
            "kwargs": {
                "parser": parse_bounding_box,
                "metavar": "south,north,west,east",
            },
            "extra_help": f"Example (france UIR): `{example}`",
        }
    if origin in (set, AbstractSet) and LiveFeedField in type_args:
        return {
            "hint": list[str],
            "kwargs": {
                "parser": parse_live_feed_field,
                "metavar": "[" + "|".join(get_args(LiveFeedField)) + "]",
            },
        }
    if _IntoTimestampArgs.issubset(type_args):
        return {
            "hint": str,
            "kwargs": {
                "parser": (
                    parse_timestamp
                    if Literal["now"] in type_args
                    else parse_past_timestamp
                ),
                "metavar": "timestamp_s",
            },
        }
    if type_args == _IntoFlightIdArgs:
        return {
            "hint": str,
            "kwargs": {"parser": parse_flight_id, "metavar": "flight_id"},
        }
    if origin is Sequence and IntoFlightId in type_args:
        return {
            "hint": list[str],
            "kwargs": {"parser": parse_flight_id, "metavar": "flight_id"},
        }
    return {}


@register_command(app, signature_from=service.FlightListService.fetch)
async def flight_list(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.FlightListResult:
    return await fr24.flight_list.fetch(*args, **kwargs)


@register_command(app, signature_from=service.FlightListService.fetch_all)
async def flight_list_all(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.FlightListResultCollection:
    results = fr24.flight_list.new_result_collection()
    async for result in fr24.flight_list.fetch_all(*args, **kwargs):
        results.append(result)
    return results


@register_command(app, signature_from=service.PlaybackService.fetch)
async def playback(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.PlaybackResult:
    return await fr24.playback.fetch(*args, **kwargs)


@register_command(app, signature_from=service.LiveFeedService.fetch)
async def live_feed(fr24: FR24, *args: Any, **kwargs: Any) -> LiveFeedResult:
    return await fr24.live_feed.fetch(*args, **kwargs)


@register_command(app, signature_from=service.LiveFeedPlaybackService.fetch)
async def live_feed_playback(
    fr24: FR24, *args: Any, **kwargs: Any
) -> LiveFeedPlaybackResult:
    return await fr24.live_feed_playback.fetch(*args, **kwargs)


# not registering airport_list (unstructured data)
# not registering find (unstructured data)


@register_command(app, signature_from=service.NearestFlightsService.fetch)
async def nearest_flights(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.NearestFlightsResult:
    return await fr24.nearest_flights.fetch(*args, **kwargs)


@register_command(app, signature_from=service.LiveFlightsStatusService.fetch)
async def live_flights_status(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.LiveFlightsStatusResult:
    return await fr24.live_flights_status.fetch(*args, **kwargs)


@register_command(app, signature_from=service.FlightDetailsService.fetch)
async def flight_details(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.FlightDetailsResult:
    return await fr24.flight_details.fetch(*args, **kwargs)


@register_command(app, signature_from=service.TopFlightsService.fetch)
async def top_flights(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.TopFlightsResult:
    return await fr24.top_flights.fetch(*args, **kwargs)


# not registering follow flight (streaming)


@register_command(app, signature_from=service.PlaybackFlightService.fetch)
async def playback_flight(
    fr24: FR24, *args: Any, **kwargs: Any
) -> service.PlaybackFlightResult:
    return await fr24.playback_flight.fetch(*args, **kwargs)


if __name__ == "__main__":
    app()
