"""HTTP transports used by FR24 services."""

from __future__ import annotations

from typing import Any, Protocol, cast

import httpx
from curl_cffi.requests import AsyncSession


class AsyncRequestSender(Protocol):
    """The subset of an async HTTP client used by JSON services."""

    async def send(self, request: httpx.Request) -> httpx.Response:
        ...


class BrowserAsyncClient:
    """An HTTPX-compatible sender with a browser TLS fingerprint.

    FR24's legacy JSON endpoints are protected by Cloudflare, which rejects
    requests made with a non-browser TLS fingerprint. gRPC endpoints continue
    to use HTTPX; this transport is only for the legacy JSON API.
    """

    def __init__(self) -> None:
        self._session: Any = AsyncSession(impersonate="chrome")

    async def send(self, request: httpx.Request) -> httpx.Response:
        response = await self._session.request(
            method=cast(Any, request.method),
            url=str(request.url),
            headers=dict(request.headers),
            data=request.content,
        )
        # curl_cffi has already decoded compressed content, whereas HTTPX
        # decodes it according to this header when constructing a response.
        headers = dict(response.headers)
        headers.pop("content-encoding", None)
        headers["content-length"] = str(len(response.content))
        return httpx.Response(
            status_code=response.status_code,
            headers=headers,
            content=response.content,
            request=request,
        )

    async def aclose(self) -> None:
        await self._session.close()
