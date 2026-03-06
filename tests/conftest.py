import logging
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import httpx
import pytest

from fr24 import FR24, FR24Cache


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


@pytest.fixture(scope="session", autouse=True)
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(http1=False, http2=True) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def cache() -> FR24Cache:
    base_dir = Path(tempfile.gettempdir()) / "fr24"
    cache = FR24Cache(base_dir)
    return cache


@pytest.fixture(scope="session", autouse=True)
async def fr24() -> AsyncGenerator[FR24, None]:
    async with FR24() as fr24:
        yield fr24
