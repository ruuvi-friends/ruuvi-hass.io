"""The Ruuvi integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, CONF_GATEWAY, CONF_BLUETOOTH, CONF_ADAPTER,
    CONF_SENSORS, CONF_MAC, CONF_MAX_UPDATE_FREQUENCY, CONF_NAME,
    CONF_MONITORED_CONDITIONS
)
from .sensor import RuuviSensor
from .subscribers import RuuviBluetoothSubscriber
PLATFORMS = ["sensor"]


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
        for condition in resource[CONF_MONITORED_CONDITIONS]:
            devices.append(
                RuuviSensor(
                    hass, mac_address, name, condition,
                    max_update_freq
                )
            )
    return devices


async def async_setup_entry(
        hass: HomeAssistant,
        config: ConfigEntry,
        async_add_entities: AddEntitiesCallback) -> bool:
    """Set up Ruuvi from a config entry."""

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
