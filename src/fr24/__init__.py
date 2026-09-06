from __future__ import annotations

import logging
import sys
from dataclasses import replace
from typing import TYPE_CHECKING

from .authentication import login
from .cache import PATH_CACHE, FR24Cache
from .clients import AsyncClientLike, default_client
from .configuration import FP_CONFIG_FILE, PATH_CONFIG
from .grpc import BoundingBox
from .json import get_json_headers
from .proto.headers import get_grpc_headers
from .service import ServiceFactory
from .static.bbox import LNGS_WORLD_STATIC
from .types.json import Authentication
from .utils import dataclass_frozen

if TYPE_CHECKING:
    from typing import Literal

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

    from .types.json import (
        TokenSubscriptionKey,
        UsernamePassword,
    )

logger = logging.getLogger(__name__)


class FR24:
    def __init__(
        self,
        client: AsyncClientLike | None = None,
    ) -> None:
        """See docs [quickstart](../usage/quickstart.md#initialisation).

        :param client: Async HTTP client to use. If omitted, an installed
            optional client backend is selected automatically.
        """
        auth = None
        resolved_client = default_client() if client is None else client
        self.http = HTTPClient(
            client=resolved_client,
            auth=auth,
            grpc_headers=get_grpc_headers(auth=auth),
            json_headers=get_json_headers(),
        )
        """The HTTP client for use in requests"""
        self._build_factory(self.http)

    def _build_factory(self, http: HTTPClient) -> None:
        factory = ServiceFactory(http)
        self.flight_list = factory.build_flight_list()
        """Flight list service."""
        self.playback = factory.build_playback()
        """Playback service."""
        self.live_feed = factory.build_live_feed()
        """Live feed service."""
        self.live_feed_playback = factory.build_live_feed_playback()
        """Live feed playback service."""
        self.airport_list = factory.build_airport_list()
        """Airport list service."""
        self.find = factory.build_find()
        """Find service."""
        self.nearest_flights = factory.build_nearest_flights()
        """Nearest flights service."""
        self.live_flights_status = factory.build_live_flights_status()
        """Live flights status service."""
        self.follow_flight = factory.build_follow_flight()
        """Follow flight service."""
        self.top_flights = factory.build_top_flights()
        """Top flights service."""
        self.flight_details = factory.build_flight_details()
        """Flight details service."""
        self.playback_flight = factory.build_playback_flight()
        """Playback flight service."""

    async def login(
        self,
        creds: (
            TokenSubscriptionKey | UsernamePassword | None | Literal["from_env"]
        ) = "from_env",
    ) -> None:
        """:param creds: Reads credentials from the environment variables or the
        config file if `creds` is set to `"from_env"` (default). Otherwise,
        provide the credentials directly.
        """
        self.http = await self.http.with_login(creds)
        self._build_factory(self.http)
        if (auth := self.http.auth) is None:
            logger.info("no authentication provided, using anonymous access")
        elif "subscription_key" in (message := auth.get("message", "")):
            logger.info(message)
        else:
            logger.info("using username and password")

    async def __aenter__(self) -> Self:
        await self.http.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.http.__aexit__(*args)


@dataclass_frozen
class HTTPClient:
    """HTTP client and request metadata shared by API services."""

    client: AsyncClientLike
    auth: Authentication | None
    grpc_headers: dict[str, str]
    json_headers: dict[str, str]

    async def with_login(
        self,
        creds: (
            TokenSubscriptionKey | UsernamePassword | Literal["from_env"] | None
        ) = "from_env",
    ) -> HTTPClient:
        auth = await login(self.client, creds)
        return replace(
            self,
            auth=auth,
            grpc_headers=get_grpc_headers(auth=auth),
            json_headers=get_json_headers(),
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.client.aclose()


BBOX_FRANCE_UIR = BoundingBox(42.0, 52.0, -8.0, 10.0)
"""Bounding box for france UIR"""

BBOXES_WORLD_STATIC = [
    BoundingBox(-90, 90, LNGS_WORLD_STATIC[i], LNGS_WORLD_STATIC[i + 1])
    for i in range(len(LNGS_WORLD_STATIC) - 1)
]
"""Default static bounding boxes covering the entire world"""

__all__ = [
    "BBOXES_WORLD_STATIC",
    "BBOX_FRANCE_UIR",
    "FP_CONFIG_FILE",
    "FR24",
    "PATH_CACHE",
    "PATH_CONFIG",
    "BoundingBox",
    "FR24Cache",
    "HTTPClient",
]
