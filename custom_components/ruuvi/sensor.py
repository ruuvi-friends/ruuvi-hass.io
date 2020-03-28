import datetime
import logging
import time

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_FORCE_UPDATE, CONF_MONITORED_CONDITIONS,
    CONF_NAME, CONF_MAC, CONF_RESOURCES
)

from simple_ruuvitag.ruuvi import RuuviTagClient

_LOGGER = logging.getLogger(__name__)

CONF_ADAPTER = 'adapter'
CONF_TIMEOUT = 'timeout'
CONF_POLL_INTERVAL = 'poll_interval'

# In Ruuvi ble this defaults to hci0, so let's ruuvi decide on defaults
# https://github.com/ttu/ruuvitag-sensor/blob/master/ruuvitag_sensor/ble_communication.py#L51
DEFAULT_ADAPTER = '' 
DEFAULT_FORCE_UPDATE = False
DEFAULT_NAME = 'RuuviTag'
DEFAULT_TIMEOUT = 5
MAX_POLL_INTERVAL = 10  # in seconds

# Sensor types are defined like: Name, units
SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_CELSIUS],
    'humidity': ['Humidity', '%'],
    'pressure': ['Pressure', 'hPa'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_RESOURCES): vol.All(
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
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(
            CONF_POLL_INTERVAL,
            default=MAX_POLL_INTERVAL): cv.positive_int,
        vol.Optional(CONF_ADAPTER, default=DEFAULT_ADAPTER): cv.string,
    }
)

def setup_platform(hass, config, add_devices, discovery_info = None):
    mac_addresses = [resource[CONF_MAC] for resource in config[CONF_RESOURCES]]
    if not isinstance(mac_addresses, list):
        mac_addresses = [mac_addresses]

    probe = RuuviProbe(
            RuuviTagClient,
            mac_addresses,
            config.get(CONF_TIMEOUT),
            config.get(CONF_POLL_INTERVAL),
            config.get(CONF_ADAPTER)
        )

    devs = []

    for resource in config[CONF_RESOURCES]:
        mac_address = resource[CONF_MAC]
        name = resource.get(CONF_NAME, mac_address)
        for condition in resource[CONF_MONITORED_CONDITIONS]:
            qualified_name = "{} {}".format(name, condition)

            devs.append(RuuviSensor(
                probe, mac_address, condition, qualified_name
            ))
    add_devices(devs)


class RuuviProbe(object):
    def __init__(self, RuuviTagClient, mac_addresses, timeout, max_poll_interval, adapter):
        self.mac_addresses = mac_addresses
        self.timeout = timeout
        self.max_poll_interval = max_poll_interval
        self.last_poll = datetime.datetime.now()
        self.adapter = adapter

        self.ble_client = RuuviTagClient()
        self.ble_client.setup(mac_addresses=mac_addresses)

        # This is likely not needed, but it's here in case multiple
        # sensors (Hass entities) are requesting updates in parallel
        # and might try to trigger polling at the same time
        self.already_pooling = False  # TODO: Turn me into a semaphore

        self.default_condition = {
            'humidity': None, 
            'identifier': None, 
            'pressure': None, 
            'temperature': None
        }
        self.conditions = {mac: self.default_condition for mac in self.mac_addresses}

    def poll(self):
        if (datetime.datetime.now() - self.last_poll).total_seconds() < self.max_poll_interval:
            # No need probe every time each HASS Sensor Sensor wants new data.
            return

        # This is likely not needed, but see comment above
        if self.already_pooling:
            time.sleep(self.timeout)
            return

        try:
            self.already_pooling = True
            self.ble_client.start()
            start_pool_time = datetime.datetime.now()

            # update flags
            ready = False
            timeout = False

            while not ready or not timeout:
                if len(self.ble_client.get_current_datas()) == len(self.mac_addresses):
                    ready = True

                if (datetime.datetime.now() - start_pool_time).total_seconds() > self.timeout:
                    timeout = True

            # We either got data for all the sensors, or we time outed. 
            # Let's return what we have
            self.conditions = self.ble_client.get_current_datas(consume=True)
            self.ble_client.stop()
            self.already_pooling = False
        except:
            _LOGGER.exception("Error on polling sensors")
        self.last_poll = datetime.datetime.now()


class RuuviSensor(Entity):
    def __init__(self, poller, mac_address, sensor_type, name):
        self.poller = poller
        self._name = name
        self.mac_address = mac_address
        self.sensor_type = sensor_type

        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return SENSOR_TYPES[self.sensor_type][1]

    def update(self):
        self.poller.poll()
        self._state = self.poller.conditions.get(self.mac_address, {}).get(self.sensor_type)
