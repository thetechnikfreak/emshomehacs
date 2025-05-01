"""Constants for the eMShome integration."""

DOMAIN = "emshome"

# Configuration
CONF_HOST = "host"
CONF_PASSWORD = "password"

# Default values
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Data Keys - from the Arduino code
DATA_POINT_KEYS = {
    # Total power
    "total_active_power_positive": 1099528667391,
    "total_active_power_negative": 1099545444607,
    
    # L1 power
    "l1_active_power_positive": 1099864211711,
    "l1_active_power_negative": 1099880988927,
    
    # L2 power
    "l2_active_power_positive": 1100199756031,
    "l2_active_power_negative": 1100216533247,
    
    # L3 power
    "l3_active_power_positive": 1100535300351,
    "l3_active_power_negative": 1100552077567,
}

# Sensor types
SENSOR_TYPES = {
    "total_active_power": {
        "name": "Total Active Power",
        "unit": "W",
        "icon": "mdi:flash",
        "device_class": "power",
        "state_class": "measurement",
    },
    "l1_active_power": {
        "name": "L1 Active Power",
        "unit": "W",
        "icon": "mdi:flash",
        "device_class": "power",
        "state_class": "measurement",
    },
    "l2_active_power": {
        "name": "L2 Active Power",
        "unit": "W",
        "icon": "mdi:flash",
        "device_class": "power",
        "state_class": "measurement",
    },
    "l3_active_power": {
        "name": "L3 Active Power",
        "unit": "W",
        "icon": "mdi:flash",
        "device_class": "power",
        "state_class": "measurement",
    },
}
