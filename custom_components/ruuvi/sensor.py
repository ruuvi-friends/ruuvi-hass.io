import datetime
import logging
import collections

from .const import DOMAIN

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import dt

from homeassistant.const import (
    CONF_MONITORED_CONDITIONS,
    CONF_NAME, CONF_MAC, CONF_SENSORS, STATE_UNKNOWN,
    TEMP_CELSIUS, PERCENTAGE, PRESSURE_HPA
)

from simple_ruuvitag.ruuvi import RuuviTagClient

_LOGGER = logging.getLogger(__name__)

# Warnings form BLESON are polluting the home assistant logs and exhausting IO
logging.getLogger('bleson').setLevel(logging.ERROR)

CONF_ADAPTER = 'adapter'
MAX_UPDATE_FREQUENCY = 'max_update_frequency'

# In Ruuvi ble this defaults to hci0, so let's ruuvi decide on defaults
# https://github.com/ttu/ruuvitag-sensor/blob/master/ruuvitag_sensor/ble_communication.py#L51
DEFAULT_ADAPTER = '' 
DEFAULT_FORCE_UPDATE = False
DEFAULT_UPDATE_FREQUENCY = 10
DEFAULT_NAME = 'RuuviTag'

MILI_G = "cm/s2"
MILI_VOLT = "mV"

# Sensor types are defined like: Name, units
SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_CELSIUS],
    'humidity': ['Humidity', PERCENTAGE],
    'pressure': ['Pressure', PRESSURE_HPA],
    'acceleration': ['Acceleration', MILI_G],
    'acceleration_x': ['X Acceleration', MILI_G],
    'acceleration_y': ['Y Acceleration', MILI_G],
    'acceleration_z': ['Z Acceleration', MILI_G],
    'battery': ['Battery voltage', MILI_VOLT],
    'movement_counter': ['Movement counter', 'count'],
    'rssi': ['Received Signal Strength Indicator', '']
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SENSORS): vol.All(
                cv.ensure_list,
                [
                    vol.Schema(
                        {
                            vol.Required(CONF_MAC): cv.string,
                            vol.Optional(CONF_NAME): cv.string,
                            vol.Optional(
                                CONF_MONITORED_CONDITIONS,
                                default=list(SENSOR_TYPES)): vol.All(
                                    cv.ensure_list,
                                    [vol.In(SENSOR_TYPES)]),
                        }
                    )
                ],
        ),
        vol.Optional(CONF_ADAPTER, default=DEFAULT_ADAPTER): cv.string,
        vol.Optional(MAX_UPDATE_FREQUENCY, default=DEFAULT_UPDATE_FREQUENCY): cv.positive_int
    }
)

async def get_sensor_set(hass, config):
    """Get a list of Sensor entities from a config entry."""

    mac_addresses = [resource[CONF_MAC].upper() for resource in config[CONF_SENSORS]]
    if not isinstance(mac_addresses, list):
        mac_addresses = [mac_addresses]

    devs = []

    for resource in config[CONF_SENSORS]:
        mac_address = resource[CONF_MAC].upper()
        default_name = "Ruuvitag " + mac_address.replace(":","").lower()
        name = resource.get(CONF_NAME, default_name)
        for condition in resource[CONF_MONITORED_CONDITIONS]:
            devs.append(
              RuuviSensor(
                hass, mac_address, name, condition,
                config.get(MAX_UPDATE_FREQUENCY)
              )
            )
    return devs

async def async_setup_entry(hass, config_entry, async_add_entities, discovery_info=None):
    """Set up ruuvi from a config entry."""

    # TODO - RESOLVE DIFF UPDATE CONFIGS
    # RIGHT NOW WE'RE JUST SETTING UP EVERYTHIN AGAIN
    config = config_entry.data

    devs = await get_sensor_set(hass, config)
    
    devs_to_add = hass.data[DOMAIN]['subscriber'].update_devs(devs)
    async_add_entities(devs_to_add)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up ruuvi from a config entry."""

    # FIX ME - When setting up through platform this is not called?
    if hass.data.get(DOMAIN, False) is False:
      hass.data[DOMAIN] = {}

    devs = await get_sensor_set(hass, config)
    
    async_add_entities(devs)

    # FIX ME - WE'RE JUST REPLACING
    ruuvi_subscrber = RuuviSubscriber(config.get(CONF_ADAPTER), devs)
    hass.data[DOMAIN]['subscriber'] = ruuvi_subscrber
    ruuvi_subscrber.start()

class RuuviSubscriber(object):
    """
    Subscribes to a set of Ruuvi tags and update Hass sensors whenever a
    new value is received.
    """
    
    def __init__(self, adapter, sensors):
        self.adapter = adapter
        self.sensors = sensors
        self.sensors_dict = None
        self.sensors_dict = collections.defaultdict(list)
        for sensor in self.sensors:
            self.sensors_dict[sensor.mac_address].append(sensor)

    def start(self):
        self.client = RuuviTagClient(
            callback=self.handle_callback,
            mac_addresses=list(self.sensors_dict.keys()),
            bt_device=self.adapter)
        _LOGGER.info(f"Starting ruuvi client")
        self.client.start()

    def stop(self):
      self.client.stop()

    def update_devs(self, devs):
      # TODO - Right now we just replace
      # Cycle through and add
      self.sensors = devs
      for sensor in self.sensors:
          self.sensors_dict[sensor.mac_address].append(sensor)
      self.client.set_mac_addresses(list(self.sensors_dict.keys()))
      return devs
      
    def handle_callback(self, mac_address, data):
        sensors = self.sensors_dict[mac_address]
        tag_name = sensors[0].tag_name if sensors else None
        _LOGGER.debug(f"Data from {mac_address} ({tag_name}): {data}")

        if data is None:
            return

        for sensor in sensors:
            if sensor.sensor_type in data.keys():
                sensor.set_state(data[sensor.sensor_type])


class RuuviSensor(Entity):
    def __init__(self, hass, mac_address, tag_name, sensor_type, max_update_frequency):
        self.hass = hass
        self.mac_address = mac_address
        self.tag_name = tag_name
        self.sensor_type = sensor_type
        self.max_update_frequency = max_update_frequency
        self.update_time = dt.utcnow() - datetime.timedelta(days=360)
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        return f"{self.tag_name} {self.sensor_type}"

    @property
    def should_poll(self):
        return False

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return SENSOR_TYPES[self.sensor_type][1]

    @property
    def unique_id(self):
      return f"ruuvi.{self.mac_address}.{self.sensor_type}"

    def set_state(self, state):
        last_updated_seconds_ago = (dt.utcnow() - self.update_time) / datetime.timedelta(seconds=1)

        self._state = state

        if last_updated_seconds_ago < self.max_update_frequency:
          _LOGGER.debug(f"Updated throttled ({last_updated_seconds_ago} elapsed): {self.name}")
          return
        else:
          _LOGGER.debug(f"Updating {self.update_time} {self.name}: {self.state}")
          self.update_time = dt.utcnow()
          self.async_schedule_update_ha_state()