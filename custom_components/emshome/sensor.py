# /config/custom_components/ems_home/sensor.py

from homeassistant.helpers.entity import Entity
import requests
import logging

_LOGGER = logging.getLogger(__name__)

def get_access_token():
    """Fetch the access token from the API."""
    url = "http://192.168.188.26/api/web-login/token"
    payload = {
        "grant_type": "password",
        "client_id": "emos",
        "client_secret": "56951025",
        "username": "admin",
        "password": "PD%3Em9w%2F%3EU%23nn"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get('access_token')
    _LOGGER.error("Failed to fetch access token: %s", response.text)
    return None

def get_charging_mode(access_token):
    """Fetch the current charging mode from the API."""
    url = "http://192.168.188.26/api/e-mobility/config/chargemode"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('mode')
    _LOGGER.error("Failed to fetch charging mode: %s", response.text)
    return None

def get_ev_power_total(access_token):
    """Fetch the EV charging power total from the API."""
    url = "http://192.168.188.26/api/e-mobility/state"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('EvChargingPower', {}).get('total')
    _LOGGER.error("Failed to fetch EV charging power total: %s", response.text)
    return None

class EMSHomeSensor(Entity):
    """Representation of the EMS Home sensor."""

    def __init__(self, name, access_token):
        self._name = name
        self._access_token = access_token
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._name == "Access Token":
            self._state = get_access_token()
        elif self._name == "Current Charging Mode":
            self._state = get_charging_mode(self._access_token)
        elif self._name == "EV Charging Power Total":
            self._state = get_ev_power_total(self._access_token)
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:flash"

