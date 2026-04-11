"""API client for eMShome devices."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any
from urllib.parse import urlencode

import aiohttp

from .const import DEFAULT_CLIENT_ID, DEFAULT_CLIENT_SECRET, DEFAULT_USERNAME

_LOGGER = logging.getLogger(__name__)


class EMShomeApiClient:
    """Small client for the eMShome device API."""

    def __init__(self, session: aiohttp.ClientSession, host: str, password: str) -> None:
        self._session = session
        self._host = host
        self._password = password
        self._access_token: str | None = None

    @property
    def host(self) -> str:
        """Return configured host."""
        return self._host

    def _url(self, path: str) -> str:
        return f"http://{self._host}{path}"

    async def authenticate(self) -> bool:
        """Fetch and store an access token."""
        payload = urlencode(
            {
                "grant_type": "password",
                "client_id": DEFAULT_CLIENT_ID,
                "client_secret": DEFAULT_CLIENT_SECRET,
                "username": DEFAULT_USERNAME,
                "password": self._password,
            }
        )

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/x-www-form-urlencoded",
            "x-requested-with": "XMLHttpRequest",
        }

        try:
            async with self._session.post(
                self._url("/api/web-login/token"),
                data=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    _LOGGER.debug("Authentication failed with status %s", response.status)
                    return False

                data = await response.json()
                self._access_token = data.get("access_token")
                return bool(self._access_token)
        except aiohttp.ClientError as err:
            _LOGGER.debug("Authentication request failed: %s", err)
            return False

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_payload: Mapping[str, Any] | None = None,
        retries: int = 1,
    ) -> tuple[int, Any]:
        """Perform an authenticated request and return status + parsed JSON/text."""
        if not self._access_token and not await self.authenticate():
            return 401, None

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "host": self._host,
        }

        try:
            async with self._session.request(
                method,
                self._url(path),
                headers=headers,
                json=json_payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 401 and retries > 0 and await self.authenticate():
                    return await self._request_json(
                        method,
                        path,
                        json_payload=json_payload,
                        retries=retries - 1,
                    )

                if response.status == 204:
                    return response.status, None

                if "application/json" in response.headers.get("Content-Type", ""):
                    return response.status, await response.json()

                return response.status, await response.text()
        except aiohttp.ClientError as err:
            _LOGGER.debug("Request %s %s failed: %s", method, path, err)
            return 0, None

    async def async_get_chargemode(self) -> dict[str, Any] | None:
        """Return charging mode config payload."""
        status, data = await self._request_json("GET", "/api/e-mobility/config/chargemode")
        if status == 200 and isinstance(data, dict):
            return data
        return None

    async def async_get_state(self) -> dict[str, Any] | None:
        """Return EV state payload."""
        status, data = await self._request_json("GET", "/api/e-mobility/state")
        if status == 200 and isinstance(data, dict):
            return data
        return None

    async def async_set_charging_mode(self, mode: str, minpvpowerquota: int | None) -> bool:
        """Set charging mode and optional quota."""
        if minpvpowerquota is None:
            minpvpowerquota = {
                "pv": 100,
                "grid": 0,
                "hybrid": 50,
                "lock": 0,
            }[mode]

        payload = {
            "mode": mode,
            "mincharginpowerquota": None,
            "minpvpowerquota": minpvpowerquota,
        }
        status, _ = await self._request_json(
            "PUT",
            "/api/e-mobility/config/chargemode",
            json_payload=payload,
        )
        return status in (200, 204)

    async def async_set_percentage(self, percentage: int) -> bool:
        """Set hybrid percentage quota."""
        payload = {
            "mode": "hybrid",
            "mincharginpowerquota": None,
            "minpvpowerquota": percentage,
        }
        status, _ = await self._request_json(
            "PUT",
            "/api/e-mobility/config/chargemode",
            json_payload=payload,
        )
        return status in (200, 204)