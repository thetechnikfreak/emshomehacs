import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

DOMAIN = "emshome"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the emshome component from YAML (not used with UI config)."""
    _LOGGER.debug("emshome: async_setup called, but config_flow handles setup")
    return True  # This is required, even if only config_flow is used

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up emshome from a config entry (UI)."""
    _LOGGER.info("Setting up EMShome entry with data: %s", entry.data)

    # Pass the config entry to your platform(s)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle unloading of an entry."""
    _LOGGER.info("Unloading EMShome entry")
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
