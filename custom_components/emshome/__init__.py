# /config/custom_components/emshome/__init__.py

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the emshome component."""
    _LOGGER.info("Setting up emshome component")

    # Fetch IP address and password from configuration
    ip_address = entry.data.get("ip_address", "192.168.188.26")  # Default IP if not provided
    password = entry.data.get("password", "PD%3Em9w%2F%3EU%23nn")  # Default password if not provided
    username = "admin"  # Username is always 'admin'

    # Register the sensors automatically
    await discovery.async_load_platform(hass, "sensor", "emshome", {
        "ip_address": ip_address,
        "username": username,
        "password": password,
    }, entry)

    return True
