from datetime import datetime
from typing import TypeVar, Union

from typing_extensions import TypeAlias

from .isqx import TimestampS

M = TypeVar("M")
"""Method"""


IntoTimestamp: TypeAlias = Union[TimestampS[int], datetime]
"""A type that can be converted to a timestamp (in seconds)."""


IntFlightId: TypeAlias = int
"""Flight ID as an integer."""
StrFlightIdHex: TypeAlias = str
"""Flight ID as a hexadecimal string."""
IntoFlightId: TypeAlias = Union[IntFlightId, StrFlightIdHex, bytes]
"""A type that can be converted to a flight ID."""
