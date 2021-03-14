import datetime
import logging
import time
import collections

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE, PRESSURE_HPA
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import call_later
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_FORCE_UPDATE, CONF_MONITORED_CONDITIONS,
    CONF_NAME, CONF_MAC, CONF_SENSORS
)

from simple_ruuvitag.ruuvi import RuuviTagClient

_LOGGER = logging.getLogger(__name__)

CONF_ADAPTER = 'adapter'

# In Ruuvi ble this defaults to hci0, so let's ruuvi decide on defaults
# https://github.com/ttu/ruuvitag-sensor/blob/master/ruuvitag_sensor/ble_communication.py#L51
DEFAULT_ADAPTER = '' 
DEFAULT_FORCE_UPDATE = False
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
    }
)

EXPIRE_AFTER = 5*60

def setup_platform(hass, config, add_devices, discovery_info = None):
    mac_addresses = [resource[CONF_MAC].upper() for resource in config[CONF_SENSORS]]
    if not isinstance(mac_addresses, list):
        mac_addresses = [mac_addresses]

    devs = []

    for resource in config[CONF_SENSORS]:
        mac_address = resource[CONF_MAC].upper()
        name = resource.get(CONF_NAME, mac_address)
        for condition in resource[CONF_MONITORED_CONDITIONS]:
            devs.append(RuuviSensor(hass, mac_address, name, condition))
    add_devices(devs)
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
    def __init__(self, hass, mac_address, tag_name, sensor_type):
        self.hass = hass
        self.mac_address = mac_address
        self.tag_name = tag_name
        self.sensor_type = sensor_type
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

    def set_state(self, state):
        self._state = state
        self.update_time = datetime.datetime.now()
        _LOGGER.debug(f"Updated {self.update_time} {self.name}: {self.state}")
        self.schedule_update_ha_state()
