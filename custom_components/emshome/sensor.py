# /config/custom_components/emshome/sensor.py

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

# Define constants for the API URLs and headers
API_URL = "http://192.168.188.26/api"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, /",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "192.168.188.26",
}

async def fetch_access_token(session):
    """Fetch the access token."""
    url = f"{API_URL}/web-login/token"
    payload = {
        "grant_type": "password",
        "client_id": "emos",
        "client_secret": "56951025",
        "username": "admin",
        "password": "PD%3Em9w%2F%3EU%23nn"
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

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the emshome sensors."""
    session = async_get_clientsession(hass)

    # Fetch the access token
    access_token = await fetch_access_token(session)

    if access_token is None:
        _LOGGER.error("No access token found. Sensors will not be set up.")
        return

    # Create sensor entities dynamically
    sensors = [
        EMShomeSensor("Access Token", access_token, session),
        EMShomeSensor("Current Charging Mode", access_token, session),
        EMShomeSensor("EV Charging Power Total", access_token, session)
    ]
    
    async_add_entities(sensors)

class EMShomeSensor(Entity):
    """Representation of the emshome sensor."""

    def __init__(self, name, access_token, session):
        """Initialize the sensor."""
        self._name = name
        self._access_token = access_token
        self._session = session
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
        url = f"{API_URL}/e-mobility/config/chargemode"
        data = await fetch_data(self._session, url, self._access_token)
        if data:
            return data.get('mode')
        return None

    async def get_ev_power_total(self):
        """Get the EV charging power total."""
        url = f"{API_URL}/e-mobility/state"
        data = await fetch_data(self._session, url, self._access_token)
        if data:
            return data.get('EvChargingPower', {}).get('total')
        return None
