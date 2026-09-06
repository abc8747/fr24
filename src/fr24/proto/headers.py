from __future__ import annotations

import secrets
import time
from functools import lru_cache
from ..utils import DEFAULT_HEADERS

from ..types.json import Authentication

PLATFORM_VERSION = "25.061.0929"
# see ./README.md.


DEFAULT_HEADERS_GRPC = {
    **DEFAULT_HEADERS,
    "Accept": "*/*",
    "fr24-device-id": "web-000000000-000000000000000000000", # fingerprint
    "fr24-platform": f"web-{PLATFORM_VERSION}",
    "x-envoy-retry-grpc-on": "unavailable",
    "Content-Type": "application/grpc-web+proto",
    "X-User-Agent": "grpc-web-javascript/0.1",
    "X-Grpc-Web": "1",
    "DNT": "1",
}

NANOID_ALPHABET = "useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict"
BASE32_DIGITS = "0123456789abcdefghijklmnopqrstuv"


def jsnum_to_base32(n: int) -> str:
    if n < 0:
        raise ValueError(f"expected n to be non-negative, got {n}")
    if n == 0:
        return "0"

    out: list[str] = []
    while n:
        n, rem = divmod(n, 32)
        out.append(BASE32_DIGITS[rem])
    out.reverse()
    return "".join(out)


def _nanoid(size: int = 21) -> str:
    random_bytes = secrets.token_bytes(size)
    # default reads bytes in reverse: https://github.com/ai/nanoid/blob/main/non-secure/index.js
    return "".join(NANOID_ALPHABET[random_bytes[i] & 63] for i in range(size - 1, -1, -1))


def generate_device_id(*, now_ms: int, suffix_size: int = 21) -> str:
    return f"web-{jsnum_to_base32(now_ms)}-{_nanoid(suffix_size)}"


@lru_cache(maxsize=1)
def get_device_id() -> str:
    # nanoid part is generated once and reused from localStorage until the record is missing/invalid
    # and the date field is refreshed over time. but since we do not persist to disk,
    # we cache across requests to mimic that behaviour
    return generate_device_id(now_ms=int(time.time() * 1000))

def get_grpc_headers(*, auth: Authentication | None, device_id: None | str = None) -> dict[str, str]:
    headers = DEFAULT_HEADERS_GRPC.copy()
    if device_id is None:
        device_id = get_device_id()
    headers["fr24-device-id"] = device_id
    if auth is not None and (token := auth["userData"].get("accessToken")) is not None:
        headers["authorization"] = f"Bearer {token}"
    return headers
