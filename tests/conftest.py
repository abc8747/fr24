import logging
import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
import pytest

from fr24 import FR24, FR24Cache
from fr24.clients.curl import CurlAsyncClient


def pytest_configure(config: pytest.Config) -> None:
    try:
        from rich.logging import RichHandler

        handlers = [RichHandler()]
    except ImportError:
        handlers = []
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=handlers
    )


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def httpx_aclient() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(http1=False, http2=True) as client:
        yield client


@pytest.fixture(scope="session")
async def curl_client() -> AsyncGenerator[CurlAsyncClient, None]:
    async with CurlAsyncClient() as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def cache() -> FR24Cache:
    base_dir = Path(tempfile.gettempdir()) / "fr24"
    cache = FR24Cache(base_dir)
    return cache


@pytest.fixture(scope="session", autouse=True)
async def fr24(
    curl_client: CurlAsyncClient,
) -> FR24:
    return FR24(curl_client)
