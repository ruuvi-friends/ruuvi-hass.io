import logging
from homeassistant.util import dt
from .const import DOMAIN, STATE_UNKNOWN, SENSOR_TYPES
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger("ruuvi.homeassisstent.sensors")


class RuuviSensor(SensorEntity):
    """
    A Ruuvi sensor is an individual metric a ruuvi tag collects.
    """

    def __init__(self, mac_address, tag_name, sensor_type, max_update_frequency):
        self.mac_address = mac_address
        self.tag_name = tag_name
        self.sensor_type = sensor_type
        self.max_update_frequency = max_update_frequency
        self.update_time = None
        self._state = STATE_UNKNOWN

        self.metadata = SENSOR_TYPES[self.sensor_type]
        self._attr_device_class = self.metadata['class']
        self._attr_state_class = self.metadata['state_class']
        self._attr_unit_of_measurement = self.metadata['unit']

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.mac_address)
            },
            "name": self.tag_name,
            "manufacturer": "Ruuvi Innovations Ltd (Oy)",
            # "model": "",
            # "sw_version": "",
        }

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
        return self._attr_unit_of_measurement

    @property
    def unique_id(self):
        return f"ruuvi.{self.mac_address}.{self.sensor_type}"

    def set_state(self, state):
        if self.update_time:
            last_updated_seconds_ago = (dt.utcnow() - self.update_time) / dt.timedelta(seconds=1)
        else:
            last_updated_seconds_ago = 9999999

        self._state = state

        if last_updated_seconds_ago < self.max_update_frequency:
            _LOGGER.debug(f"Updated throttled ({last_updated_seconds_ago} elapsed): {self.name}")
            return
        else:
            _LOGGER.debug(f"Updating {self.update_time} {self.name}: {self.state}")
            self.update_time = dt.utcnow()
            self.async_schedule_update_ha_state()
