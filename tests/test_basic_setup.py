"""The basic setup of the platform."""

from homeassistant.setup import async_setup_component

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ruuvi.const import DOMAIN
from custom_components.ruuvi.sensor import (
  CONF_SENSORS, CONF_MAC, CONF_NAME, SENSOR_TYPES, CONF_MONITORED_CONDITIONS,
  CONF_ADAPTER, MAX_UPDATE_FREQUENCY, EXPIRE_AFTER
)

MANDATORY_CONFIG_DATA = {
  CONF_SENSORS: [
    {
      CONF_MAC: "MA:CA:DD:RE:SS:00",
    }
  ]
}

FULL_CONFIG_DATA = {
  CONF_SENSORS: [{
    CONF_MAC: "MA:CA:DD:RE:SS:00",
    CONF_NAME: "Living room",
    CONF_MONITORED_CONDITIONS: SENSOR_TYPES.keys()
  }],
  CONF_ADAPTER: '',
  MAX_UPDATE_FREQUENCY: 5,
  EXPIRE_AFTER: 5
}

async def test_setup_ruuvi_empty_platform(hass):
    """Test creation of lights."""

    """Test a successful setup component."""
    await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()


async def test_setup_ruuvi_basic_platform(hass):
    """Test creation of lights."""

    """Test a successful setup component."""
    await async_setup_component(hass, DOMAIN, MANDATORY_CONFIG_DATA)
    await hass.async_block_till_done()

async def test_setup_ruuvi_full_platform(hass):
    """Test creation of lights."""

    """Test a successful setup component."""
    await async_setup_component(hass, DOMAIN, FULL_CONFIG_DATA)
    await hass.async_block_till_done()