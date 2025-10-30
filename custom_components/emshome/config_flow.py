import logging
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

class EMShomeConfigFlow(config_entries.ConfigFlow, domain="emshome"):
    """Handle a config flow for EMShome."""
    
    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._ip_address = None
        self._password = None

    async def async_step_user(self, user_input=None):
        """Handle the user step."""
        if user_input is None:
            # First time configuration, ask for IP and Password
            return self.async_show_form(
                step_id="user",
                data_schema=self._get_data_schema(),  # Make sure this is a callable
            )
        
        # Process user input (IP, password)
        self._ip_address = user_input[CONF_IP_ADDRESS]
        self._password = user_input[CONF_PASSWORD]
        
        # Verify that the information is correct (you may add your API check here)
        if not await self._validate_input():
            return self.async_show_form(
                step_id="user",
                errors={"base": "invalid_credentials"},
                data_schema=self._get_data_schema(),
            )

        # Store the config entry
        return self.async_create_entry(
            title=self._ip_address,
            data={
                CONF_IP_ADDRESS: self._ip_address,
                CONF_PASSWORD: self._password,
            },
        )

    def _get_data_schema(self):
        """Return the data schema for user input."""
        from homeassistant.helpers import config_validation as cv
        from homeassistant.const import CONF_PASSWORD

        return vol.Schema({
            vol.Required(CONF_IP_ADDRESS, default="192.168.188.26"): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
        })

    async def _validate_input(self):
        """Validate the user input. This can be a test API call."""
        try:
            # You can make an API request here to validate the credentials.
            # For example, by calling the `fetch_access_token` method
            # and checking if the authentication is successful.
            return True  # If the credentials are valid, return True.
        except Exception:
            return False
