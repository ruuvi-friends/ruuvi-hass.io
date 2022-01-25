from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, CONF_GATEWAY, CONF_BLUETOOTH, CONF_ADAPTER,
    CONF_SENSORS, CONF_MAC, CONF_MAX_UPDATE_FREQUENCY, CONF_NAME,
    CONF_MONITORED_CONDITIONS, SENSOR_TYPES
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
        for condition in resource.get(CONF_MONITORED_CONDITIONS, SENSOR_TYPES.keys()):
            devices.append(
                # self, mac_address, tag_name, sensor_type, max_update_frequency
                RuuviSensor(
                    mac_address, name, condition,
                    max_update_freq
                )
            )
    return devices


async def async_setup_entry(hass, config_entry, async_add_entities, discovery_info=None):
    """Set up ruuvi from a config entry."""
    config = config_entry.data
    print("SETUP ENTRY")
    print(config)
    devs = await get_sensor_set(hass, config)
    devs_to_add = hass.data[DOMAIN][config.entry_id].update_devs(devs)
    async_add_entities(devs_to_add)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Ruuvi from a config entry."""
    
    print("SETUP ENTRY")
    print(config)

    entities = []
    if hass.data.get(DOMAIN, False) is False:
        hass.data[DOMAIN] = {}

    if config.get(CONF_BLUETOOTH):
        bluetooth_conf = config.get(CONF_BLUETOOTH)
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
    hass.config_entries.async_setup_platforms(config, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok