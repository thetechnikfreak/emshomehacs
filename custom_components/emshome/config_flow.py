import logging
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .api import EMShomeApiClient
from .const import CONF_LEGACY_IP_ADDRESS, DOMAIN

_LOGGER = logging.getLogger(__name__)

class EMShomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EMShome."""
    
    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._ip_address = None
        self._password = None

    async def async_step_user(self, user_input=None):
        """Handle the user step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_data_schema(),
            )

        self._ip_address = user_input[CONF_HOST]
        self._password = user_input[CONF_PASSWORD]
        await self.async_set_unique_id(self._ip_address)
        self._abort_if_unique_id_configured()

        if not await self._validate_input():
            return self.async_show_form(
                step_id="user",
                errors={"base": "cannot_connect"},
                data_schema=self._get_data_schema(),
            )

        return self.async_create_entry(
            title=self._ip_address,
            data={
                CONF_HOST: self._ip_address,
                CONF_PASSWORD: self._password,
                # Keep legacy key for backwards compatibility with older versions.
                CONF_LEGACY_IP_ADDRESS: self._ip_address,
            },
        )

    def _get_data_schema(self):
        """Return the data schema for user input."""
        from homeassistant.helpers import config_validation as cv

        return vol.Schema({
            vol.Required(CONF_HOST, default="192.168.188.26"): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
        })

    async def _validate_input(self):
        """Validate user credentials against the device API."""
        try:
            session = async_get_clientsession(self.hass)
            api = EMShomeApiClient(session, self._ip_address, self._password)
            if not await api.authenticate():
                return False
            return await api.async_get_chargemode() is not None
        except Exception as err:  # broad catch to keep flow stable for network errors
            _LOGGER.debug("Validation failed: %s", err)
            return False
