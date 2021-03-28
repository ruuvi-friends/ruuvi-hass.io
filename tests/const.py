from custom_components.ruuvi.const import DOMAIN

from homeassistant.const import (
    CONF_PLATFORM, STATE_UNKNOWN
)

from custom_components.ruuvi.sensor import (
  CONF_SENSORS, CONF_MAC, CONF_NAME, SENSOR_TYPES, CONF_MONITORED_CONDITIONS,
  CONF_ADAPTER, MAX_UPDATE_FREQUENCY
)


MANDATORY_CONFIG_DATA = {
  CONF_PLATFORM: DOMAIN,
  CONF_SENSORS: [
    {
      CONF_MAC: "MA:CA:DD:RE:SS:00",
    }
  ]
}

FULL_CONFIG_DATA = {
  CONF_PLATFORM: DOMAIN,
  CONF_SENSORS: [{
    CONF_MAC: "MA:CA:DD:RE:SS:00",
    CONF_NAME: "Living room",
    CONF_MONITORED_CONDITIONS: SENSOR_TYPES.keys()
  }],
  CONF_ADAPTER: '',
  MAX_UPDATE_FREQUENCY: 5
}


# Newest firmware data
DF_5_DATA = {
  "data_format": 5,
  "humidity": 53.49,
  "temperature": 24.30,
  "pressure": 1000.44,
  "acceleration": 7,
  "acceleration_x": 4,
  "acceleration_y": -4,
  "acceleration_z": 1036,
  "tx_power": 4,
  "battery": 2977,
  "movement_counter": 66,
  "measurement_sequence_number": 205,
  "mac": "macaddress00"
}

# Older firmware data
DF_3_DATA = {
  "data_format": 5,
  "humidity": 53.49,
  "temperature": 24.30,
  "pressure": 1000.44,
  "acceleration": 7,
  "acceleration_x": 4,
  "acceleration_y": -4,
  "acceleration_z": 1036,
  "battery": 2977
}
