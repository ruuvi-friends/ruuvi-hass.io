from homeassistant.const import (
    CONF_MONITORED_CONDITIONS,
    CONF_NAME, CONF_MAC, CONF_SENSORS, CONF_IP_ADDRESS,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    # States and units
    STATE_UNKNOWN, TEMP_CELSIUS, PERCENTAGE, PRESSURE_HPA,
    # Device classes
    DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_SIGNAL_STRENGTH, DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
)

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_TOTAL
)

# DOMAIN
DOMAIN = 'ruuvi'

# CONF
CONF_ADAPTER = 'adapter'
CONF_MAX_UPDATE_FREQUENCY = 'max_update_frequency'
CONF_BLUETOOTH = 'bluetooth'
CONF_GATEWAY = 'gateways'
CONF_RUUVI_PLATFORM_TYPE = 'platform_type'

# UNITS
MILI_G = "cm/s2"
MILI_VOLT = "mV"

# Sensor types are defined like: Name, units
SENSOR_TYPES = {
    'temperature': {
        'name': 'Temperature',
        'unit': TEMP_CELSIUS,
        'class': DEVICE_CLASS_TEMPERATURE,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'humidity': {
        'name': 'Humidity',
        'unit': PERCENTAGE,
        'class': DEVICE_CLASS_HUMIDITY,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'pressure': {
        'name': 'Pressure',
        'unit': PRESSURE_HPA,
        'class': DEVICE_CLASS_PRESSURE,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'acceleration': {
        'name': 'Acceleration',
        'unit': MILI_G,
        'class': None,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'acceleration_x': {
        'name': 'X Acceleration',
        'unit': MILI_G,
        'class': None,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'acceleration_y': {
        'name': 'Y Acceleration',
        'unit': MILI_G,
        'class': None,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'acceleration_z': {
        'name': 'Z Acceleration',
        'unit': MILI_G,
        'class': None,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'battery': {
        'name': 'Battery voltage',
        'unit': MILI_VOLT,
        'class': DEVICE_CLASS_VOLTAGE,
        'state_class': STATE_CLASS_MEASUREMENT
    },
    'movement_counter': {
        'name': 'Movement counter',
        'unit': 'count',
        'class': None,
        'state_class': STATE_CLASS_TOTAL_INCREASING
    },
    'rssi': {
        'name': 'Received Signal Strength Indicator',
        'unit': None,
        'class': DEVICE_CLASS_SIGNAL_STRENGTH,
        'state_class': STATE_CLASS_MEASUREMENT
    }
}
