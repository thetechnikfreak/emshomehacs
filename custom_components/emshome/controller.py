"""Sensor platform for EMSHome integration."""
import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import POWER_WATT

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    controller = hass.data["emshome"]["controller"]
    
    sensors = [
        EMSHomeChargingModeSensor(controller),
        EMSHomeChargingPowerSensor(controller),
        EMSHomeEVConnectedSensor(controller)
    ]
    
    async_add_entities(sensors, True)

class EMSHomeSensor(SensorEntity):
    """Base class for EMSHome sensors."""
    
    def __init__(self, controller):
        """Initialize the sensor."""
        self._controller = controller
        self._available = False
        
    @property
    def available(self):
        """Return True if entity is available."""
        return self._controller.available
        
    async def async_added_to_hass(self):
        """Register callbacks."""
        self._controller.register_listener(self._update_callback)
        
    async def async_will_remove_from_hass(self):
        """Clean up when entity is removed."""
        self._controller.remove_listener(self._update_callback)
        
    def _update_callback(self):
        """Call when data has been updated."""
        self.async_write_ha_state()

class EMSHomeChargingModeSensor(EMSHomeSensor):
    """Sensor for the current charging mode."""
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return "Current Charging Mode"
        
    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"emshome_charging_mode"
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._controller.data.get("charging_mode")
        
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:car-electric"

class EMSHomeChargingPowerSensor(EMSHomeSensor):
    """Sensor for the current charging power."""
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return "EV Charging Power Total"
        
    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"emshome_charging_power"
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._controller.data.get("charging_power")
        
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return POWER_WATT
        
    @property
    def device_class(self):
        """Return the device class of this entity."""
        return "power"
        
    @property
    def state_class(self):
        """Return the state class of this entity."""
        return "measurement"
        
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:flash"

class EMSHomeEVConnectedSensor(EMSHomeSensor):
    """Sensor for whether an EV is connected."""
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return "EV Connected Status"
        
    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"emshome_ev_connected"
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._controller.data.get("ev_connected")
        
    @property
    def icon(self):
        """Return the icon of the sensor."""
        connected = self._controller.data.get("ev_connected")
        return "mdi:ev-plug-type2" if connected else "mdi:ev-station"