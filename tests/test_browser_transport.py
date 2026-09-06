import httpx
import pytest

from fr24.transport import BrowserAsyncClient


class FakeResponse:
    def __init__(self) -> None:
        self.status_code = 200
        self.headers = {
            "content-encoding": "gzip",
            "content-type": "application/json",
        }
        self.content = b'{"ok": true}'


class FakeSession:
    async def request(self, **kwargs: object) -> FakeResponse:
        return FakeResponse()


@pytest.mark.anyio
async def test_browser_transport_returns_decoded_httpx_response() -> None:
    client = BrowserAsyncClient()
    client._session = FakeSession()

    response = await client.send(httpx.Request("GET", "https://example.test"))

    assert response.json() == {"ok": True}
    assert "content-encoding" not in response.headers
    assert response.headers["content-length"] == str(len(b'{"ok": true}'))
