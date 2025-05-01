# /config/custom_components/ems_home/__init__.py

"""The EMS Home component."""
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

def setup(hass: HomeAssistant, config: dict):
    """Set up the EMS Home component."""
    _LOGGER.info("Setting up EMS Home component")
    # Here you can initialize your services, sensors, etc.
    return True
