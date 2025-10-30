import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import aiohttp
import voluptuous as vol
from urllib.parse import urlencode

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up EMShome sensors from a config entry."""
    ip_address = entry.data.get('ip_address')
    password = entry.data.get('password')
    username = "admin"
    client_id = "emos"
    client_secret = "56951025"

    session = async_get_clientsession(hass)

    _LOGGER.debug("Setting up sensors for IP %s", ip_address)

    access_token = await fetch_access_token(session, ip_address, username, password, client_id, client_secret)
    if not access_token:
        _LOGGER.error("Failed to retrieve access token.")
        return

    sensors = [
        EMShomeSensor("Current Charging Mode", access_token, session, ip_address),
        EMShomeSensor("Current PV Prozentage", access_token, session, ip_address),
        EMShomeSensor("EV Charging Power Total", access_token, session, ip_address),
    ]
    async_add_entities(sensors)
    async def handle_set_mode(call):
        mode = call.data.get("mode")
        _LOGGER.debug("Received service call to set mode: %s", mode)
        await set_charging_mode(session, ip_address, access_token, mode)

    hass.services.async_register(
        "emshome", "set_charging_mode", handle_set_mode,
        schema=vol.Schema({vol.Required("mode"): vol.In(["lock", "pv", "grid", "hybrid"])})
    )
    async def handle_set_prozentage(call):
        prozentage = call.data.get("prozentage")
        _LOGGER.debug("Received service call to set prozentage: %s", prozentage)
        await set_prozentage(session, ip_address, access_token, prozentage)

    hass.services.async_register(
        "emshome", "prozentage", handle_set_prozentage,
        schema=vol.Schema({vol.Required("prozentage"): vol.All(vol.Coerce(int), vol.Range(min=1, max=100))})
    )

async def fetch_access_token(session, ip_address, username, password, client_id, client_secret):
    """Fetch the access token with the provided credentials."""
    url = f"http://{ip_address}/api/web-login/token"
    
    # URL-encode the data payload manually
    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }
    
    # URL-encode the payload
    encoded_payload = urlencode(payload)

    # Headers to mimic the fetch request
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "x-requested-with": "XMLHttpRequest",
    }

    _LOGGER.debug("Requesting access token from: %s with payload: %s", url, encoded_payload)

    try:
        async with session.post(url, data=encoded_payload, headers=headers) as response:
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
        elif self._name == "Current PV Prozentage":
            self._state = await self.fetch_prozentage()

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
                    charging_power = data.get("EvChargingPower", {}).get("total")
                    _LOGGER.debug("Parsed EV charging power: %s", charging_power)
                    _LOGGER.debug("Full EV state response: %s", data)
                    return charging_power
                else:
                    _LOGGER.error("Failed to get EV charging power. Response status: %d", response.status)
                    _LOGGER.debug("Response content: %s", await response.text())
                    return None
        except Exception as e:
            _LOGGER.error("Error during EV charging power request: %s", str(e))
            return None
    async def fetch_prozentage(self):
        """Fetch the EV prozentage from API"""
        url = f"http://{self._ip_address}/api/e-mobility/config/chargemode"
        headers = {"Authorization": f"Bearer {self._access_token}"}

        _LOGGER.debug("Requesting EV prozentage from: %s", url)

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    prozentage = data.get("minpvpowerquota")
                    _LOGGER.debug("Parsed EV prozentage: %s", prozentage)
                    _LOGGER.debug("Full EV  response: %s", data)
                    return prozentage
                else:
                    _LOGGER.error("Failed to get EV prozentage. Response status: %d", response.status)
                    _LOGGER.debug("Response content: %s", await response.text())
                    return None
        except Exception as e:
            _LOGGER.error("Error during EV prozentage request: %s", str(e))
            return None

async def set_charging_mode(session, ip_address, access_token, mode):
    """Send a PUT request to set the charging mode."""
    url = f"http://{ip_address}/api/e-mobility/config/chargemode"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "host": ip_address,
    }
    payload = {
        "mode": mode,
        "mincharginpowerquota": None,
        "minpvpowerquota": 0
    }

    _LOGGER.debug("Sending PUT to %s with payload: %s", url, payload)

    try:
        async with session.put(url, headers=headers, json=payload) as response:
            if response.status == 200:
                _LOGGER.info("Successfully set charging mode to %s", mode)
            else:
                _LOGGER.error("Failed to set charging mode. Status: %d", response.status)
                _LOGGER.debug("Response content: %s", await response.text())
    except Exception as e:
        _LOGGER.error("Error setting charging mode: %s", str(e))
        
async def set_prozentage(session, ip_address, access_token, prozentage):
    """Send a PUT request to set the prozentage."""
    url = f"http://{ip_address}/api/e-mobility/config/chargemode"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "host": ip_address,
    }
    payload = {
        "mode": "hybrid",
        "mincharginpowerquota": None,
        "minpvpowerquota": prozentage
    }

    _LOGGER.debug("Sending PUT to %s with payload: %s", url, payload)

    try:
        async with session.put(url, headers=headers, json=payload) as response:
            if response.status == 204:
                _LOGGER.info("Successfully set prozentage to %s", prozentage)
            else:
                _LOGGER.error("Failed to set prozentage stus: %d", response.status)
                _LOGGER.debug("Response content: %s", await response.text())
    except Exception as e:
        _LOGGER.error("Error setting prozentage: %s", str(e))
