from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, CONF_GATEWAY, CONF_BLUETOOTH, CONF_ADAPTER,
    CONF_SENSORS, CONF_MAC, CONF_MAX_UPDATE_FREQUENCY, CONF_NAME,
    CONF_MONITORED_CONDITIONS, SENSOR_TYPES, CONF_RUUVI_PLATFORM_TYPE
)
from .entities import RuuviSensor
from .subscribers import RuuviBluetoothSubscriber

_LOGGER = logging.getLogger("ruuvi.homeassisstent.sensors")


async def get_sensor_set(hass, config):
    """Get a list of Sensor entities from a config entry."""

    mac_addresses = [resource[CONF_MAC].upper() for resource in config[CONF_SENSORS]]
    if not isinstance(mac_addresses, list):
        mac_addresses = [mac_addresses]

    devices = []

    for resource in config[CONF_SENSORS]:
        mac_address = resource[CONF_MAC].upper()
        max_update_freq = resource[CONF_MAX_UPDATE_FREQUENCY]
        default_name = "Ruuvitag " + mac_address.replace(":", "").lower()
        name = resource.get(CONF_NAME, default_name)
        for condition in resource.get(CONF_MONITORED_CONDITIONS, list(SENSOR_TYPES.keys())):
            devices.append(
                # self, mac_address, tag_name, sensor_type, max_update_frequency
                RuuviSensor(
                    mac_address, name, condition,
                    max_update_freq
                )
            )
    return devices


async def async_setup_entry(hass, config_entry, async_add_entities, discovery_info=None):
    """Set up ruuvi from a config flow."""
    config = config_entry.data
    entities = []
    if hass.data.get(DOMAIN, False) is False:
        hass.data[DOMAIN] = {}

    platform_type = config.get(CONF_ADAPTER).get(CONF_RUUVI_PLATFORM_TYPE)
    if platform_type == CONF_BLUETOOTH:
        entities = await get_sensor_set(hass, config)
        bluetooth_options = config.get(CONF_ADAPTER).get(CONF_BLUETOOTH)
        ruuvi_subscriber = RuuviBluetoothSubscriber(
            entities, bluetooth_options.get(CONF_ADAPTER)
        )
        hass.data[DOMAIN][config.entry_id] = ruuvi_subscriber

    elif platform_type == config.get(CONF_GATEWAY):
        # Not implemented
        entities = []
        raise

    async_add_entities(entities)
    ruuvi_subscriber.start()
    return True


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    """Set up Ruuvi from a config entry."""
    config = config_entry.data
    entities = []
    if hass.data.get(DOMAIN, False) is False:
        hass.data[DOMAIN] = {}

    if config.get(CONF_ADAPTER).get(CONF_RUUVI_PLATFORM_TYPE):
        bluetooth_conf = config.get(CONF_ADAPTER).get(CONF_BLUETOOTH)
        entities = await get_sensor_set(hass, bluetooth_conf.get(CONF_SENSORS))
        ruuvi_subscriber = RuuviBluetoothSubscriber(
            bluetooth_conf.get(CONF_ADAPTER), entities
        )
        hass.data[DOMAIN][config.entry_id] = ruuvi_subscriber

    elif config.get(CONF_GATEWAY):
        # Not implemented
        entities = []
        raise

    async_add_entities(entities)
    ruuvi_subscriber.start()
    return True
