from __future__ import annotations

import sys
from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Protocol, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from curl_cffi.requests import AsyncSession, Headers
from curl_cffi.requests import Request as CurlRequest
from curl_cffi.requests import Response as CurlCffiResponse
from curl_cffi.requests.session import HttpMethod

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from . import AsyncClientLike, QueryValue, ResponseLike


class _CurlResponseLike(Protocol):
    status_code: int
    headers: Headers
    content: bytes

    def json(self) -> object: ...

    def raise_for_status(self) -> object: ...

    def aiter_content(self) -> AsyncIterator[bytes]: ...

    async def aclose(self) -> None: ...


class CurlResponse(ResponseLike):
    def __init__(self, response: CurlCffiResponse) -> None:
        self._response = cast(_CurlResponseLike, response)

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> Headers:
        return self._response.headers

    @property
    def content(self) -> bytes:
        return self._response.content

    @content.setter
    def content(self, value: bytes) -> None:
        self._response.content = value

    def json(self) -> object:
        return self._response.json()

    def raise_for_status(self) -> object:
        return self._response.raise_for_status()

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        async for chunk in self._response.aiter_content():
            yield chunk

    async def aclose(self) -> None:
        await self._response.aclose()


class CurlAsyncClient(AsyncClientLike):
    def __init__(
        self, session: AsyncSession[CurlCffiResponse] | None = None
    ) -> None:
        self._session = session or AsyncSession(impersonate="firefox")

    def build_request(
        self,
        method: str,
        url: str,
        *,
        content: bytes | None = None,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, QueryValue] | None = None,
    ) -> CurlRequest:
        if params:
            parts = urlsplit(url)
            query = [*parse_qsl(parts.query, keep_blank_values=True)]
            query.extend(_query_pairs(params))
            url = urlunsplit(parts._replace(query=urlencode(query)))

        request_headers = Headers(headers or {})
        body = content
        if data:
            body = urlencode(data).encode()
            if "content-type" not in request_headers:
                request_headers["content-type"] = (
                    "application/x-www-form-urlencoded"
                )
        return CurlRequest(
            url=url, headers=request_headers, method=method, body=body
        )

    async def send(
        self, request: CurlRequest, *, stream: bool = False
    ) -> ResponseLike:
        response = await self._session.request(
            cast(HttpMethod, request.method),
            request.url,
            headers=request.headers,
            content=request.body,
            stream=stream,
        )
        if not stream:
            # curl-cffi exposes decompressed bytes in response.content.
            response.headers.pop("content-encoding", None)
            response.headers["content-length"] = str(len(response.content))
        return CurlResponse(response)

    async def aclose(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()


def _query_pairs(params: Mapping[str, QueryValue]) -> Iterator[tuple[str, str]]:
    for key, value in params.items():
        if isinstance(value, (str, int, float, bool)):
            yield key, str(value)
            continue
        yield from ((key, str(item)) for item in value)
