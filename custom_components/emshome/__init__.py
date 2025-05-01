# /config/custom_components/emshome/__init__.py

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the emshome component using YAML configuration."""
    _LOGGER.info("Setting up emshome component")

    # Extract IP and password from YAML configuration
    ip_address = config.get('emshome', {}).get('ip_address', '192.168.188.26')
    password = config.get('emshome', {}).get('password', 'DeinPasswort')
    username = "admin"  # Default username, could also be configurable if needed
    client_id = "emos"
    client_secret = "56951025"

    # Pass the configuration to the sensors
    await discovery.async_load_platform(hass, "sensor", "emshome", {
        "ip_address": ip_address,
        "username": username,
        "password": password,
    }, config)

    return True
