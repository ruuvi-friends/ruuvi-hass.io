import logging
import collections
from .const import SENSOR_TYPES
from simple_ruuvitag.ruuvi import RuuviTagClient

_LOGGER = logging.getLogger("ruuvi.homeassisstent.devices")


class RuuviSubscriber(object):
    """
    Subscribes to a set of Ruuvi tags and update Hass sensors whenever a
    new value is received or polled
    """

    def __init__(self, sensors):
        self.sensors_dict = None
        self.update_devices(sensors)

    def update_devices(self, sensors):
        # remove all sensors not in a list
        self.sensors_dict = collections.defaultdict(
            lambda: {key: None for key in SENSOR_TYPES.keys()}
        )
        for sensor in sensors:
            self.sensors_dict[sensor.mac_address][sensor.sensor_type] = sensor

    def stop(self):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()


class RuuviBluetoothSubscriber(RuuviSubscriber):
    def __init__(self, sensors, adapter):
        self.adapter = adapter
        super().__init__(sensors)

    def start(self):
        self.client = RuuviTagClient(
            callback=self.handle_callback,
            mac_addresses=list(self.sensors_dict.keys()),
            bt_device=self.adapter)
        _LOGGER.info("Starting ruuvi client")
        self.client.start()

    def stop(self):
        self.client.stop()

    def handle_callback(self, mac_address, data):
        sensors = [i for i in self.sensors_dict[mac_address].values() if i]
        tag_name = sensors[0].tag_name if sensors else None
        _LOGGER.debug(f"Data from {mac_address} ({tag_name}): {data}")

        if data is None:
            return

        for sensor in sensors:
            if sensor.sensor_type in data.keys():
                sensor.set_state(data[sensor.sensor_type])

    def update_devices(self, sensors):
        # TODO - Right now we just replace
        # Cycle through and add
        self.sensors = sensors
        for sensor in self.sensors:
            self.sensors_dict[sensor.mac_address].append(sensor)
        self.client.set_mac_addresses(list(self.sensors_dict.keys()))
        return self.sensors


class RuuviGatewayPoolSubscriber(RuuviSubscriber):
    """
    Gateway Poll subscriber uses polling to query data from
    RuuviGateway
    """
    # NOT IMPLEMENTED YET

