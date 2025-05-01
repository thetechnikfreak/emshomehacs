# /config/custom_components/emshome/sensor.py

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp

_LOGGER = logging.getLogger(__name__)

# Enable debug logging for the integration in the Home Assistant configuration
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the emshome sensors."""
    ip_address = config.get('ip_address', '192.168.188.26')
    password = config.get('password', 'DeinPasswort')
    username = "admin"  # Default username, could also be configured in YAML
    client_id = "emos"
    client_secret = "56951025"

    session = async_get_clientsession(hass)

    # Log starting of sensor setup
    _LOGGER.debug("Starting to set up EMShome sensors with IP: %s", ip_address)

    # Fetch the Access Token
    access_token = await fetch_access_token(session, ip_address, username, password, client_id, client_secret)

    if access_token is None:
        _LOGGER.error("No access token found. Sensors will not be set up.")
        return

    # Log token retrieved
    _LOGGER.debug("Access token obtained: %s", access_token)

    # Create sensor entities
    sensors = [
        EMShomeSensor("Current Charging Mode", access_token, session, ip_address),
        EMShomeSensor("EV Charging Power Total", access_token, session, ip_address)
    ]
    
    async_add_entities(sensors)

async def fetch_access_token(session, ip_address, username, password, client_id, client_secret):
    """Fetch the access token with the provided credentials."""
    url = f"http://{ip_address}/api/web-login/token"
    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }
    
    _LOGGER.debug("Requesting access token from: %s", url)

    try:
        async with session.post(url, data=payload) as response:
            if response.status == 200:
                data = await response.json()
                _LOGGER.debug("Response from access token request: %s", data)
                return data.get('access_token')
            else:
                _LOGGER.error("Failed to get access token. Response status: %d", response.status)
                _LOGGER.debug("Response content: %s", await response.text())
                return None
    except Exception as e:
        _LOGGER.error("Error during access token request: %s", str(e))
        return None

class EMShomeSensor(Entity):
    """Representation of an EMShome sensor."""

    def __init__(self, name, access_token, session, ip_address):
        self._name = name
        self._access_token = access_token
        self._session = session
        self._ip_address = ip_address
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        # Example logic to update the state for each sensor
        if self._name == "Current Charging Mode":
            self._state = await self.fetch_charging_mode()
        elif self._name == "EV Charging Power Total":
            self._state = await self.fetch_charging_power()

    async def fetch_charging_mode(self):
        """Fetch the current charging mode from the API."""
        url = f"http://{self._ip_address}/api/e-mobility/config/chargemode"
        headers = {"Authorization": f"Bearer {self._access_token}"}

        _LOGGER.debug("Requesting current charging mode from: %s", url)

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Response for charging mode: %s", data)
                    return data.get("mode")
                else:
                    _LOGGER.error("Failed to get charging mode. Response status: %d", response.status)
                    _LOGGER.debug("Response content: %s", await response.text())
                    return None
        except Exception as e:
            _LOGGER.error("Error during charging mode request: %s", str(e))
            return None

    async def fetch_charging_power(self):
        """Fetch the EV charging power from the API."""
        url = f"http://{self._ip_address}/api/e-mobility/state"
        headers = {"Authorization": f"Bearer {self._access_token}"}

        _LOGGER.debug("Requesting EV charging power from: %s", url)

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Response for EV charging power: %s", data)
                    return data.get("EvChargingPower.total")
                else:
                    _LOGGER.error("Failed to get EV charging power. Response status: %d", response.status)
                    _LOGGER.debug("Response content: %s", await response.text())
                    return None
        except Exception as e:
            _LOGGER.error("Error during EV charging power request: %s", str(e))
            return None
