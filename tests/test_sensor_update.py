"""The basic setup of the platform."""
import logging
from unittest.mock import patch
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent
from custom_components.ruuvi.sensor import (
    SENSOR_TYPES, RuuviSensor, RuuviSubscriber
)
from .const import DF_3_DATA, DF_5_DATA, STATE_UNKNOWN


_LOGGER = logging.getLogger(__name__)


async def test_df_3_data_update(hass: HomeAssistant):
    """Test platform setup."""

    with patch('custom_components.ruuvi.sensor.RuuviTagClient'):
        sensors = []
        for condition in SENSOR_TYPES.keys():
            sensors += [
                RuuviSensor(hass, "MA:CA:DD:RE:SS:00", "Ruuvitag macaddress00", condition, 10)
            ]
        subscriber = RuuviSubscriber('', sensors)
        component = component = EntityComponent(_LOGGER, 'sensor', hass)

        await component.async_add_entities(sensors)
        await hass.async_block_till_done()
        await hass.async_start()
        await hass.async_block_till_done()

    subscriber.handle_callback("MA:CA:DD:RE:SS:00", DF_3_DATA)

    await hass.async_block_till_done()
    for condition in SENSOR_TYPES.keys():
        print(hass.states)
        state = hass.states.get(f"sensor.ruuvitag_macaddress00_{condition}")
        assert state is not None
        assert state.state == str(DF_3_DATA.get(condition, STATE_UNKNOWN))


# FIXME - THERE IS A LOT OF BOILERPLATE HERE, WHEN IN THESE TESTS THE ONLY THING THAT CHANGES
# IS THE DATA PASSED TO HANDLE CALLBACK. REFACTOR ME PLEASE

async def test_df_5_data_update(hass: HomeAssistant):
    """Test platform setup."""

    with patch('custom_components.ruuvi.sensor.RuuviTagClient'):
        sensors = []
        for condition in SENSOR_TYPES.keys():
            sensors += [
                RuuviSensor(hass, "MA:CA:DD:RE:SS:00", "Ruuvitag macaddress00", condition, 10)
            ]
        subscriber = RuuviSubscriber('', sensors)
        component = component = EntityComponent(_LOGGER, 'sensor', hass)

        await component.async_add_entities(sensors)
        await hass.async_block_till_done()
        await hass.async_start()
        await hass.async_block_till_done()

    subscriber.handle_callback("MA:CA:DD:RE:SS:00", DF_5_DATA)

    await hass.async_block_till_done()
    for condition in SENSOR_TYPES.keys():
        print(hass.states)
        state = hass.states.get(f"sensor.ruuvitag_macaddress00_{condition}")
        assert state is not None
        assert state.state == str(DF_5_DATA.get(condition, STATE_UNKNOWN))
