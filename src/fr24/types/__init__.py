from datetime import datetime
from typing import Callable, TypeVar, Union, cast

from typing_extensions import Concatenate, ParamSpec, TypeAlias

#
# In this library, we have a clear separation between
# the low level api (e.g. `fr24.json.flight_list`) and
# higher-level OOP wrappers (e.g. `fr24.flight_list.fetch()`).
#
# Low level APIs accept a `dataclass` as request params
# (e.g. `FlightListParams`) which has extensive documentation for each member.
# To avoid having to rewrite same documentation for its higher level counterpart
# , the following decorator copies the signature from a target `dataclass`.
#
# IDEs will show the correct signature for the higher-level function and MyPy
# will also be happy with it.
#

T = TypeVar("T")
"""origin return type"""
P = ParamSpec("P")
"""origin parameter type"""
S = TypeVar("S")
"""Extra `self` in target method"""
R = TypeVar("R")
"""Actual return type"""


def overwrite_args_signature_from(
    _origin: Callable[P, T],
) -> Callable[
    [Callable[Concatenate[S, ...], R]], Callable[Concatenate[S, P], R]
]:
    """
    Override the argument signature of some target callable with that of an
    `origin` callable. Keeps the target return type intact.

    # Examples

    ```pycon
    >>> from typing import Any
    >>> from fr24.types import overwrite_args_signature_from
    >>> def foo(a: int, b: int) -> float:
    ...     ...
    >>> @overwrite_args_signature_from(foo)
    ... def bar(args: Any, kwargs: Any) -> str:
    ...     return str(foo(*args, **kwargs))
    >>> # IDEs will now show `bar` as having signature
    >>> # `Callable[[int, int], str]`
    ```
    """
    # NOTE: when mkdocs builds the docs, it will not show the signature of `foo`
    # but rather the signature of `bar`.

    def decorator(
        target: Callable[Concatenate[S, ...], R],
    ) -> Callable[Concatenate[S, P], R]:
        return cast(Callable[Concatenate[S, P], R], target)

    return decorator


IntTimestampS: TypeAlias = int
"""Unix timestamp in integer seconds."""
IntTimestampMs: TypeAlias = int
"""Unix timestamp in integer milliseconds."""
IntoTimestamp: TypeAlias = Union[IntTimestampS, datetime]
"""A type that can be converted to a timestamp (in seconds)."""


IntFlightId: TypeAlias = int
"""Flight ID as an integer."""
StrFlightIdHex: TypeAlias = str
"""Flight ID as a hexadecimal string."""
IntoFlightId: TypeAlias = Union[IntFlightId, StrFlightIdHex, bytes]
"""A type that can be converted to a flight ID."""
