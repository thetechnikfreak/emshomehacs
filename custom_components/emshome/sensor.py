# /config/custom_components/emshome/sensor.py

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the emshome sensors."""
    ip_address = config.get('ip_address', '192.168.188.26')
    password = config.get('password', 'DeinPasswort')
    username = "admin"  # Default username, could also be configured in YAML
    client_id = "emos"
    client_secret = "56951025"

    session = async_get_clientsession(hass)

    # Fetch the Access Token
    access_token = await fetch_access_token(session, ip_address, username, password, client_id, client_secret)

    if access_token is None:
        _LOGGER.error("No access token found. Sensors will not be set up.")
        return

    # Create sensor entities
    sensors = [
        EMShomeSensor("Access Token", access_token, session, ip_address),
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
    async with session.post(url, data=payload) as response:
        if response.status == 200:
            data = await response.json()
            return data.get('access_token')
        else:
            _LOGGER.error("Error fetching access token")
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
        if self._name == "Access Token":
            self._state = self._access_token
        elif self._name == "Current Charging Mode":
            self._state = await self.fetch_charging_mode()
        elif self._name == "EV Charging Power Total":
            self._state = await self.fetch_charging_power()

    async def fetch_charging_mode(self):
        """Fetch the current charging mode from the API."""
        url = f"http://{self._ip_address}/api/e-mobility/config/chargemode"
        headers = {"Authorization": f"Bearer {self._access_token}"}
        async with self._session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("mode")
            return None

    async def fetch_charging_power(self):
        """Fetch the EV charging power from the API."""
        url = f"http://{self._ip_address}/api/e-mobility/state"
        headers = {"Authorization": f"Bearer {self._access_token}"}
        async with self._session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("EvChargingPower.total")
            return None
