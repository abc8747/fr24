from __future__ import annotations

import base64
import configparser
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, cast

from .clients import AsyncClientLike
from .configuration import FP_CONFIG_FILE
from .types.json import (
    Authentication,
    TokenSubscriptionKey,
    UsernamePassword,
)
from .utils import DEFAULT_HEADERS

logger = logging.getLogger(__name__)


def get_credentials(
    fp_config_file: Path = FP_CONFIG_FILE,
) -> TokenSubscriptionKey | UsernamePassword | None:
    """Reads credentials from the environment variables, overriding it with
    the config file if it exists.
    """
    username = os.environ.get("fr24_username", None)
    password = os.environ.get("fr24_password", None)
    subscription_key = os.environ.get("fr24_subscription_key", None)
    token = os.environ.get("fr24_token", None)

    if fp_config_file.exists():
        config = configparser.ConfigParser()
        config.read(fp_config_file.as_posix())

        username = config.get("global", "username", fallback=None)
        password = config.get("global", "password", fallback=None)
        subscription_key = config.get(
            "global", "subscription_key", fallback=None
        )
        token = config.get("global", "token", fallback=None)

    if username and password:
        return {"username": username, "password": password}
    if subscription_key and token:
        return {"subscriptionKey": subscription_key, "token": token}
    return None


async def login(
    client: AsyncClientLike,
    creds: (
        TokenSubscriptionKey | UsernamePassword | None | Literal["from_env"]
    ) = "from_env",
    fp_config_file: Path = FP_CONFIG_FILE,
) -> None | Authentication:
    """Read credentials and returns the credentials needed to access the API.

    By default, credentials are read from the environment variables or the
    config file if `creds_override` is not set. Then, if the credentials:
    - `username` and `password` is set: makes a POST request to the login
    endpoint
    - `subscription_key` and `token` is set: returns immediately
    - otherwise, `None` is returned
    """
    creds = get_credentials(fp_config_file) if creds == "from_env" else creds

    if creds is None:
        return None
    if (u := creds.get("username")) and (p := creds.get("password")):
        return await login_with_username_password(client, u, p)  # type: ignore[arg-type]
    if s := creds.get("subscriptionKey"):
        t = creds.get("token")
        return await login_with_token_subscription_key(client, s, t)  # type: ignore[arg-type]

    logger.warning(
        "expected username+password or subscriptionKey+Optional[token] pair,"
        "but one or both are missing. falling back to anonymous access."
    )
    return None


async def login_with_username_password(
    client: AsyncClientLike,
    username: str,
    password: str,
) -> Authentication | None:
    """Retrieve bearer token and subscription key from the API.

    Bearer: `json['userData']['accessToken']`
    `token=` query param: `json['userData']['subscriptionKey']`
    """
    request = client.build_request(
        "POST",
        "https://www.flightradar24.com/user/login",
        data={"email": username, "password": password},
        headers=DEFAULT_HEADERS,
    )
    response = await client.send(request)
    response.raise_for_status()
    auth = response.json()
    if not isinstance(auth, dict) or not isinstance(auth.get("userData"), dict):
        message = (
            auth.get("msg", auth.get("message", "unknown error"))
            if isinstance(auth, dict)
            else "invalid response"
        )
        logger.warning("FR24 login did not return credentials: %s", message)
        return None
    return cast(Authentication, auth)


async def login_with_token_subscription_key(
    _client: AsyncClientLike,
    subscription_key: str,
    token: str | None,
) -> Authentication | None:
    """Login with subscription key and/or token.
    Falls back to anonymous access if token is expired or invalid.
    """
    if token is None:
        return {
            "userData": {
                "subscriptionKey": subscription_key,
            },
            "message": "using environment `subscription_key`",
        }

    try:
        payload = json.loads(base64.b64decode(token.split(".")[1]))
    except (IndexError, ValueError) as e:
        logger.warning(
            f"failed to parse token: {e}. falling back to anonymous access"
        )
        return None

    exp = payload["exp"]
    exp_f = datetime.fromtimestamp(exp, timezone.utc).isoformat()
    if time.time() > exp:
        logger.warning(
            f"token has expired at {exp_f}. falling back to anonymous access"
        )
        return None

    return {
        "user": {
            "id": payload.get("userId"),
        },
        "userData": {
            "subscriptionKey": subscription_key,
            "accessToken": token,
            "dateExpires": exp,
        },
        "message": "using environment `subscription_key` and `token`",
    }
