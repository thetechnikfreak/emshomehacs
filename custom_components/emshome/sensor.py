"""Sensor platform for the eMShome integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import EMShomeApiClient
from .const import (
    DOMAIN,
    SENSOR_CHARGING_MODE,
    SENSOR_EV_POWER_TOTAL,
    SENSOR_KEYS,
    SENSOR_PV_PERCENTAGE,
    SERVICE_SET_CHARGING_MODE,
    SERVICE_SET_PERCENTAGE,
)
from .coordinator import EMShomeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS: dict[str, dict[str, Any]] = {
    SENSOR_CHARGING_MODE: {
        "translation_key": SENSOR_CHARGING_MODE,
        "icon": "mdi:ev-station",
    },
    SENSOR_PV_PERCENTAGE: {
        "translation_key": SENSOR_PV_PERCENTAGE,
        "icon": "mdi:solar-power",
        "native_unit_of_measurement": PERCENTAGE,
    },
    SENSOR_EV_POWER_TOTAL: {
        "translation_key": SENSOR_EV_POWER_TOTAL,
        "icon": "mdi:flash",
        "native_unit_of_measurement": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up eMShome sensors for a config entry."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator: EMShomeDataUpdateCoordinator = runtime["coordinator"]
    api: EMShomeApiClient = runtime["api"]

    entities = [
        EMShomeSensor(coordinator=coordinator, entry=entry, sensor_key=sensor_key)
        for sensor_key in SENSOR_KEYS
    ]
    async_add_entities(entities)

    async def handle_set_mode(call: ServiceCall) -> None:
        mode: str = call.data["mode"]
        minpvpowerquota: int | None = call.data.get("minpvpowerquota")
        if not await api.async_set_charging_mode(mode, minpvpowerquota):
            _LOGGER.error("Failed to set charging mode to %s", mode)
            return
        await coordinator.async_request_refresh()

    async def handle_set_percentage(call: ServiceCall) -> None:
        percentage: int = call.data["prozentage"]
        if not await api.async_set_percentage(percentage):
            _LOGGER.error("Failed to set percentage to %s", percentage)
            return
        await coordinator.async_request_refresh()

    services = runtime.setdefault("services", [])

    if not hass.services.has_service(DOMAIN, SERVICE_SET_CHARGING_MODE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_CHARGING_MODE,
            handle_set_mode,
            schema=vol.Schema(
                {
                    vol.Required("mode"): vol.In(["lock", "pv", "grid", "hybrid"]),
                    vol.Optional("minpvpowerquota"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=100)
                    ),
                }
            ),
        )
        services.append((SERVICE_SET_CHARGING_MODE, handle_set_mode))

    if not hass.services.has_service(DOMAIN, SERVICE_SET_PERCENTAGE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_PERCENTAGE,
            handle_set_percentage,
            schema=vol.Schema(
                {
                    vol.Required("prozentage"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=100)
                    )
                }
            ),
        )
        services.append((SERVICE_SET_PERCENTAGE, handle_set_percentage))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload sensor services for this config entry."""
    runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    for service_name, _ in runtime.get("services", []):
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
    runtime["services"] = []
    return True


class EMShomeSensor(CoordinatorEntity[EMShomeDataUpdateCoordinator], SensorEntity):
    """Representation of an eMShome sensor."""

    def __init__(
        self,
        coordinator: EMShomeDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._entry = entry
        self._attr_has_entity_name = True

        description = SENSOR_DESCRIPTIONS[sensor_key]
        self._attr_translation_key = description["translation_key"]
        self._attr_icon = description.get("icon")
        self._attr_device_class = description.get("device_class")
        self._attr_native_unit_of_measurement = description.get("native_unit_of_measurement")
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Describe the parent eMShome device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="eMShome Smart Meter",
            manufacturer="eMShome",
            model="Smart Meter",
            configuration_url=f"http://{self.coordinator.api.host}",
        )

    @property
    def native_value(self) -> Any:
        """Return the current value from coordinator data."""
        return self.coordinator.data.get(self._sensor_key)