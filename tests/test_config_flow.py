
"""Tests for the config flow."""
from unittest import mock

from homeassistant.const import CONF_MAC, CONF_NAME, CONF_PATH
from pytest_homeassistant_custom_component.common import AsyncMock, patch, MockConfigEntry

from custom_components.ruuvi import config_flow
from custom_components.ruuvi.const import DOMAIN


async def test_flow_user_init(hass):
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )

    # Note, the user step is now empty, which will later be used to 
    # choose betweek Gateway and Ruuvi Sensors. Right now we get
    # forwarded right away to the Add Sensor

    expected = {
        "data_schema": config_flow.CONFIG_FLOW_RUUVI_ADD_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "ruuvi",
        "step_id": "add_sensor",
        "type": "form",
    }
    assert expected == result


async def test_flow_add_sensor_data_valid(hass):
    """Test we advance to the next step when valid sensor is submitted."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "add_sensor"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"], user_input={CONF_MAC: "MA:CA:DD:RE:SS:00", CONF_NAME: "Sauna"}
    )
    assert "config_sensor" == result["step_id"]
    assert "form" == result["type"]


@patch('custom_components.ruuvi.sensor.RuuviTagClient')
async def test_flow_configure_sensor_data_valid(_ruuvi_tag_client, hass):
    """Test we advance to the next step when valid sensor is submitted."""

    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_MAC: "MA:CA:DD:RE:SS:00", CONF_NAME: "Sauna"}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={
          "temperature": True,
          "humidity": True,
          "pressure": True,
          "acceleration": True,
          "acceleration_x": True,
          "acceleration_y": True,
          "acceleration_z": True,
          "battery": True,
          "movement_counter": True
        }
    )
    assert "add_another" == result["step_id"]
    assert "form" == result["type"]


async def test_flow_add_another_data_valid(hass):
    """Test we advance to the next step when valid sensor is submitted."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "add_another"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"], user_input={"add_another": True}
    )
    assert "add_sensor" == result["step_id"]
    assert "form" == result["type"]


@patch('custom_components.ruuvi.sensor.RuuviTagClient')
async def test_flow_complete(_ruuvi_tag_client, hass):
    """Test we advance to the next step when valid sensor is submitted."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "add_another"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"], user_input={"add_another": False}
    )
    assert "create_entry" == result["type"]