import datetime
import logging
import collections

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.entity import Entity
from homeassistant.util import dt

from homeassistant.const import (
    CONF_MONITORED_CONDITIONS,
    CONF_NAME, CONF_MAC, CONF_SENSORS, STATE_UNKNOWN,
    TEMP_CELSIUS, PERCENTAGE, PRESSURE_HPA
)

from simple_ruuvitag.ruuvi import RuuviTagClient

_LOGGER = logging.getLogger(__name__)

CONF_ADAPTER = 'adapter'
MAX_UPDATE_FREQUENCY = 'max_update_frequency'
EXPIRE_AFTER = 'expire_after'

# In Ruuvi ble this defaults to hci0, so let's ruuvi decide on defaults
# https://github.com/ttu/ruuvitag-sensor/blob/master/ruuvitag_sensor/ble_communication.py#L51
DEFAULT_ADAPTER = '' 
DEFAULT_FORCE_UPDATE = False
DEFAULT_UPDATE_FREQUENCY = 10
DEFAULT_NAME = 'RuuviTag'
DEFAULT_EXPIRE_AFTER = 5

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
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SENSORS): vol.All(
                cv.ensure_list,
                [
                    vol.Schema(
                        {
                            vol.Required(CONF_MAC): cv.string,
                            vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
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
        vol.Optional(MAX_UPDATE_FREQUENCY, default=DEFAULT_UPDATE_FREQUENCY): cv.positive_int,
        vol.Optional(EXPIRE_AFTER, default=DEFAULT_EXPIRE_AFTER): cv.positive_int,
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up ruuvi from a config entry."""
    mac_addresses = [resource[CONF_MAC].upper() for resource in config[CONF_SENSORS]]
    if not isinstance(mac_addresses, list):
        mac_addresses = [mac_addresses]

    devs = []

    for resource in config[CONF_SENSORS]:
        mac_address = resource[CONF_MAC].upper()
        name = resource.get(CONF_NAME, mac_address)
        for condition in resource[CONF_MONITORED_CONDITIONS]:
            devs.append(
              RuuviSensor(
                hass, mac_address, name, condition,
                config.get(MAX_UPDATE_FREQUENCY),
                config.get(EXPIRE_AFTER)
              )
            )
    
    async_add_entities(devs)
    
    RuuviSubscriber(config.get(CONF_ADAPTER), devs).start()

class RuuviSubscriber(object):
    """
    Subscribes to a set of Ruuvi tags and update Hass sensors whenever a
    new value is received.
    """
    
    def __init__(self, adapter, sensors):
        self.adapter = adapter
        self.sensors = sensors
        self.sensors_dict = None

    def start(self):
        self.sensors_dict = collections.defaultdict(list)
        for sensor in self.sensors:
            self.sensors_dict[sensor.mac_address].append(sensor)

        self.client = RuuviTagClient(
            callback=self.handle_callback,
            mac_addresses=list(self.sensors_dict.keys()),
            bt_device=self.adapter)
        _LOGGER.info(f"Starting ruuvi client")
        self.client.start()

    async def handle_callback(self, mac_address, data):
        sensors = self.sensors_dict[mac_address]
        tag_name = sensors[0].tag_name if sensors else None
        _LOGGER.debug(f"Data from {mac_address} ({tag_name}): {data}")

        if data is None:
            return

        for sensor in sensors:
            if sensor.sensor_type in data.keys():
                sensor.set_state(data[sensor.sensor_type])

class RuuviSensor(Entity):
    def __init__(self, hass, mac_address, tag_name, sensor_type, max_update_frequency, expire_after):
        self.hass = hass
        self.mac_address = mac_address
        self.tag_name = tag_name
        self.sensor_type = sensor_type
        self.max_update_frequency = max_update_frequency
        self.expire_after = expire_after * 60
        self.update_time = dt.utcnow()
        self._state = None

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

    async def set_state(self, state):
        last_updated_seconds_ago = (dt.utcnow() - self.update_time) / datetime.timedelta(seconds=1)

        self._state = state
        self.update_time = dt.utcnow()
        _LOGGER.debug(f"Updated {self.update_time} {self.name}: {self.state}")

        if last_updated_seconds_ago < self.max_update_frequency:
          _LOGGER.debug(f"Updated throttled ({last_updated_seconds_ago} elapsed): {self.name}")
          return
        else:
          self.async_schedule_update_ha_state()

        async_call_later(self.hass, EXPIRE_AFTER, self.expire_state_if_old)

    async def expire_state_if_old(self, delay):
        state_age_seconds = (dt.utcnow() - self.update_time) / datetime.timedelta(seconds=1)
        if state_age_seconds >= self.expire_after:
            _LOGGER.debug(f"{self.name}: Expire state due to age")
            self._state = STATE_UNKNOWN
            self.async_schedule_update_ha_state()
