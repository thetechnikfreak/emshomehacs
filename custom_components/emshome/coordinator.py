"""Coordinator for eMShome sensor data."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EMShomeApiClient
from .const import (
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    SENSOR_CHARGING_MODE,
    SENSOR_EV_POWER_TOTAL,
    SENSOR_PV_PERCENTAGE,
)

_LOGGER = logging.getLogger(__name__)


class EMShomeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Handle fetching all sensor values from eMShome."""

    def __init__(self, hass: HomeAssistant, api: EMShomeApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="eMShome coordinator",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL_SECONDS),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API and normalize it for sensors."""
        chargemode = await self.api.async_get_chargemode()
        state = await self.api.async_get_state()

        if chargemode is None and state is None:
            raise UpdateFailed("Could not fetch any data from device")

        return {
            SENSOR_CHARGING_MODE: (chargemode or {}).get("mode"),
            SENSOR_PV_PERCENTAGE: (chargemode or {}).get("minpvpowerquota"),
            SENSOR_EV_POWER_TOTAL: ((state or {}).get("EvChargingPower") or {}).get("total"),
        }