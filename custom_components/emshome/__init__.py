"""The eMShome integration."""
import logging
import async_timeout
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, CONF_PASSWORD

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .emshome_client import EMSHomeClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the eMShome component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up eMShome from a config entry."""
    host = entry.data[CONF_HOST]
    password = entry.data[CONF_PASSWORD]

    client = EMSHomeClient(host, password)

    # Validate the connection
    if not await client.authenticate():
        return False

    coordinator = EMSHomeDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    # Start the websocket listener
    await client.start_listening()

    # Set up all platforms (modern method)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await client.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class EMSHomeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching eMShome data."""

    def __init__(self, hass, client):
        """Initialize the data update coordinator."""
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from eMShome."""
        try:
            async with async_timeout.timeout(10):
                # Return existing data, websocket updates happen automatically
                return self.client.data
        except Exception as error:
            raise UpdateFailed(f"Error communicating with eMShome: {error}")
