import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EMShomeApiClient
from .const import CONF_LEGACY_IP_ADDRESS, DOMAIN
from .coordinator import EMShomeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the emshome component from YAML (not used with UI config)."""
    _LOGGER.debug("emshome: async_setup called, but config_flow handles setup")
    return True  # This is required, even if only config_flow is used

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up emshome from a config entry (UI)."""
    host = entry.data.get(CONF_HOST) or entry.data.get(CONF_LEGACY_IP_ADDRESS)
    password = entry.data.get(CONF_PASSWORD)

    if not host or not password:
        _LOGGER.error("Missing host/password in config entry")
        return False

    session = async_get_clientsession(hass)
    api = EMShomeApiClient(session=session, host=host, password=password)
    if not await api.authenticate():
        _LOGGER.error("Authentication failed for eMShome host %s", host)
        return False

    coordinator = EMShomeDataUpdateCoordinator(hass=hass, api=api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle unloading of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok
