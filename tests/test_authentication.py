from __future__ import annotations

from urllib.parse import parse_qs

import httpx
import pytest

from fr24.authentication import login_with_username_password
from fr24.proto.headers import get_grpc_headers


class FakeClient:
    request: httpx.Request | None = None

    async def send(self, request: httpx.Request) -> httpx.Response:
        self.request = request
        return httpx.Response(
            200,
            json={"userData": {"accessToken": "token"}},
            request=request,
        )


@pytest.mark.anyio
async def test_login_uses_request_sender() -> None:
    client = FakeClient()

    result = await login_with_username_password(
        client, "me@example.com", "secret"
    )

    assert result is not None
    assert result["userData"]["accessToken"] == "token"
    assert client.request is not None
    assert client.request.url == "https://www.flightradar24.com/user/login"
    assert parse_qs(client.request.content.decode()) == {
        "email": ["me@example.com"],
        "password": ["secret"],
    }


@pytest.mark.anyio
async def test_login_returns_none_without_credentials() -> None:
    class FailedLoginClient:
        async def send(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"success": False}, request=request)

    result = await login_with_username_password(
        FailedLoginClient(), "me@example.com", "bad-password"
    )

    assert result is None
    assert "authorization" not in get_grpc_headers(auth={"success": False})
