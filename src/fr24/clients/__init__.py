from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Mapping, Sequence
from importlib.util import find_spec
from typing import (
    Callable,
    Protocol,
    Union,
)


class RequestLike(Protocol):
    @property
    def method(self) -> str: ...


class HeadersLike(Protocol):
    def get(self, key: str, default: str | None = None) -> str | None: ...


class ResponseLike(Protocol):
    @property
    def status_code(self) -> int: ...

    @property
    def headers(self) -> HeadersLike: ...

    @property
    def content(self) -> bytes: ...

    def json(self) -> object: ...

    def raise_for_status(self) -> object: ...

    def aiter_bytes(self) -> AsyncIterator[bytes]: ...

    async def aclose(self) -> None: ...


QueryScalar = Union[str, int, float, bool]
QueryValue = Union[QueryScalar, Sequence[QueryScalar]]


class HTTPStatusError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"HTTP request failed with status {status_code}")
        self.status_code = status_code


class AsyncClientLike(Protocol):
    def build_request(
        self,
        method: str,
        url: str,
        *,
        content: bytes | None = None,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, QueryValue] | None = None,
    ) -> RequestLike: ...

    @property
    def send(self) -> Callable[..., Awaitable[ResponseLike]]: ...

    async def aclose(self) -> None: ...


def default_client() -> AsyncClientLike:
    if find_spec("curl_cffi") is not None:
        from .curl import CurlAsyncClient

        return CurlAsyncClient()
    if find_spec("httpx") is not None:
        from httpx import AsyncClient as HTTPXAsyncClient

        return HTTPXAsyncClient(http2=True)
    raise RuntimeError(
        "error: no HTTP client installed\n"
        "= help: fr24 does not come with a default HTTP client. "
        "Install 'fr24[curl]' or 'fr24[httpx]'"
    )
