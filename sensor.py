"""Support for eMShome sensors."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up eMShome sensors based on a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    client = data["client"]
    coordinator = data["coordinator"]
    
    entities = []
    
    # Add sensors for total power and each phase
    for sensor_type, sensor_info in SENSOR_TYPES.items():
        entities.append(
            EMSHomeSensor(
                coordinator,
                client,
                config_entry.data["host"],
                sensor_type,
                sensor_info,
            )
        )
    
    async_add_entities(entities)


class EMSHomeSensor(CoordinatorEntity, SensorEntity):
    """Representation of an eMShome sensor."""

    def __init__(self, coordinator, client, host, sensor_type, sensor_info):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.client = client
        self.host = host
        self.sensor_type = sensor_type
        self._attr_name = sensor_info["name"]
        self._attr_unit_of_measurement = sensor_info["unit"]
        self._attr_icon = sensor_info["icon"]
        self._attr_device_class = sensor_info["device_class"]
        self._attr_state_class = sensor_info["state_class"]
        
        # Set unique ID
        self._attr_unique_id = f"{host}_{sensor_type}"
        
        # Get the line number based on sensor type
        if sensor_type == "total_active_power":
            self.line = 0
        elif sensor_type == "l1_active_power":
            self.line = 1
        elif sensor_type == "l2_active_power":
            self.line = 2
        elif sensor_type == "l3_active_power":
            self.line = 3
        else:
            self.line = 0

    @property
    def device_info(self):
        """Return device information about this eMShome device."""
        return {
            "identifiers": {(DOMAIN, self.host)},
            "name": "eMShome Smart Meter",
            "manufacturer": "eMShome",
            "model": "Smart Meter",
            "sw_version": "Unknown",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.client.get_active_power(self.line)
