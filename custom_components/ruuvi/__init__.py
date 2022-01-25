"""The Ruuvi integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN
)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ruuvi from a config entry."""
    # TODO Scaffold the subscribers here.
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True
