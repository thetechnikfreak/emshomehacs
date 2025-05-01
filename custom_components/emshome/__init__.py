import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the emshome component."""
    _LOGGER.info("Setting up emshome component")

    # Register the sensors automatically
    await discovery.async_load_platform(hass, "sensor", "emshome", {}, entry)

    return True
