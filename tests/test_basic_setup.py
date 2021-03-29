"""The basic setup of the platform."""
from unittest.mock import MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ruuvi.sensor import (
  SENSOR_TYPES
)

from custom_components.ruuvi.sensor import (
  async_setup_platform
)

from .const import FULL_CONFIG_DATA, MANDATORY_CONFIG_DATA, ONLY_CERTAIN_CONDITIONS_CONFIG_DATA


async def test_full_setup_platform(hass: HomeAssistant):
    """Test platform setup."""
    async_add_entities = MagicMock()

    with patch('custom_components.ruuvi.sensor.RuuviTagClient') as ruuvi_ble_client:
      await async_setup_platform(hass, FULL_CONFIG_DATA, async_add_entities, None)
      assert async_add_entities.called


async def test_basic_setup_component(hass: HomeAssistant):
    """Test platform setup."""

    with patch('custom_components.ruuvi.sensor.RuuviTagClient') as ruuvi_ble_client:
      assert await async_setup_component(hass, "sensor",
            {
                "sensor": [
                    MANDATORY_CONFIG_DATA,
                ]
            },
        )
      await hass.async_block_till_done()
      await hass.async_start()
      await hass.async_block_till_done()
    for condition in SENSOR_TYPES.keys():
      state = hass.states.get(f"sensor.ruuvitag_macaddress00_{condition}")
      assert state is not None

async def test_monitored_conditions_setup(hass: HomeAssistant):
    """Test platform setup."""

    with patch('custom_components.ruuvi.sensor.RuuviTagClient') as ruuvi_ble_client:
      assert await async_setup_component(hass, "sensor",
            {
                "sensor": [
                    ONLY_CERTAIN_CONDITIONS_CONFIG_DATA,
                ]
            },
        )
      await hass.async_block_till_done()
      await hass.async_start()
      await hass.async_block_till_done()

    expected_conditions = ['temperature', 'pressure']
    non_expected_conditions = SENSOR_TYPES.keys() - expected_conditions

    for condition in expected_conditions:
      state = hass.states.get(f"sensor.ruuvitag_macaddress00_{condition}")
      assert state is not None

    for condition in non_expected_conditions:
      state = hass.states.get(f"sensor.ruuvitag_macaddress00_{condition}")
      assert state is None

