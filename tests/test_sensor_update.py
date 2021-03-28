"""The basic setup of the platform."""

from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry


from custom_components.ruuvi.const import DOMAIN
from custom_components.ruuvi.sensor import (
  CONF_SENSORS, CONF_MAC, CONF_NAME, SENSOR_TYPES, CONF_MONITORED_CONDITIONS,
  CONF_ADAPTER, MAX_UPDATE_FREQUENCY, EXPIRE_AFTER
)

from custom_components.ruuvi.sensor import RuuviSensor, RuuviSubscriber

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

RUUVI_CONFIG_DATA = {
  CONF_SENSORS: [
    {
      CONF_MAC: "MA:CA:DD:RE:SS:00",
      CONF_NAME: "Sauna"
    }
  ]
}

async def test_updates_sensor_state(hass):
    sensor = RuuviSensor(hass, "MA:CA:DD:RE:SS:00", "Sauna", "temperature", 0, 1000)
    subscriber = RuuviSubscriber('', [sensor])
    subscriber.handle_callback(
      "MA:CA:DD:RE:SS:00",
      DF_5_DATA
    )

