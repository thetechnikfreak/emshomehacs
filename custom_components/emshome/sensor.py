# /config/custom_components/emshome/sensor.py

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the emshome sensors."""
    # Read the configuration parameters from the config passed by __init__.py
    ip_address = config.get('ip_address', '192.168.188.26')  # Default IP address if not provided
    password = config.get('password', 'PD%3Em9w%2F%3EU%23nn')  # Default password if not provided
    username = "admin"  # Username is always 'admin'
    client_id = "emos"
    client_secret = "56951025"

    session = async_get_clientsession(hass)

    # Fetch the access token using the provided password and other details
    access_token = await fetch_access_token(session, ip_address, username, password, client_id, client_secret)

    if access_token is None:
        _LOGGER.error("No access token found. Sensors will not be set up.")
        return

    # Create sensor entities dynamically
    sensors = [
        EMShomeSensor("Access Token", access_token, session, ip_address),
        EMShomeSensor("Current Charging Mode", access_token, session, ip_address),
        EMShomeSensor("EV Charging Power Total", access_token, session, ip_address)
    ]
    
    async_add_entities(sensors)

async def fetch_access_token(session, ip_address, username, password, client_id, client_secret):
    """Fetch the access token using provided credentials."""
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
            _LOGGER.error("Failed to fetch access token")
            return None

async def fetch_data(session, url, access_token):
    """Fetch data from the API."""
    headers = {**HEADERS, "Authorization": f"Bearer {access_token}"}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            _LOGGER.error("Failed to fetch data from %s", url)
            return None

class EMShomeSensor(Entity):
    """Representation of the emshome sensor."""

    def __init__(self, name, access_token, session, ip_address):
        """Initialize the sensor."""
        self._name = name
        self._access_token = access_token
        self._session = session
        self._ip_address = ip_address
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._name == "Access Token":
            self._state = self._access_token
        elif self._name == "Current Charging Mode":
            self._state = self.get_charging_mode()
        elif self._name == "EV Charging Power Total":
            self._state = self.get_ev_power_total()
        return self._state

    async def async_update(self):
        """Update the sensor state."""
        if self._name == "Current Charging Mode":
            self._state = await self.get_charging_mode()
        elif self._name == "EV Charging Power Total":
            self._state = await self.get_ev_power_total()

    async def get_charging_mode(self):
        """Get the current charging mode."""
        url = f"http://{self._ip_address}/api/e-mobility/config/chargemode"
        data = await fetch_data(self._session, url, self._access_token)
        if data:
            return data.get('mode')
        return None

    async def get_ev_power_total(self):
        """Get the EV charging power total."""
        url = f"http://{self._ip_address}/api/e-mobility/state"
        data = await fetch_data(self._session, url, self._access_token)
        if data:
            return data.get('EvChargingPower', {}).get('total')
        return None
