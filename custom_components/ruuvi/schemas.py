
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .const import (
    SENSOR_TYPES, CONF_SENSORS, CONF_NAME,
    CONF_MONITORED_CONDITIONS, CONF_ADAPTER, CONF_MAC,
    CONF_MAX_UPDATE_FREQUENCY,
    CONF_BLUETOOTH, CONF_GATEWAY, CONF_IP_ADDRESS, CONF_RUUVI_PLATFORM_TYPE
)

from .defaults import (
    DEFAULT_UPDATE_FREQUENCY,
    DEFAULT_ADAPTER
)

from homeassistant.components.sensor import PLATFORM_SCHEMA


CONFIG_FLOW_CHOOSE_PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_RUUVI_PLATFORM_TYPE
        ): vol.In([CONF_BLUETOOTH, CONF_GATEWAY])
    }
)

CONFIG_FLOW_ADD_ANOTHER_SCHEMA = vol.Schema(
    {
        vol.Optional("add_another"): cv.boolean
    }
)

BASE_RUUVI_TAG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        # Monitored conditions is removed because of the config flow
        # does not like monitored conditions
        vol.Optional(
            CONF_MAX_UPDATE_FREQUENCY,
            default=DEFAULT_UPDATE_FREQUENCY): cv.positive_int
    }
)

RUUVI_TAG_SCHEMA = BASE_RUUVI_TAG_SCHEMA.extend(
    {
        vol.Optional(
            CONF_MONITORED_CONDITIONS,
            default=list(SENSOR_TYPES.keys())): vol.All(
                cv.ensure_list,
                [vol.In(SENSOR_TYPES.keys())]),
    }
)


BLUETOOTH_ADAPTER_OPTIONS_SCHEMA = vol.Schema({
    vol.Optional(CONF_ADAPTER, default=DEFAULT_ADAPTER): cv.string,
})


GATEWAY_ADAPTER_OPTIONS_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SENSORS): vol.All(
            cv.ensure_list,
            [RUUVI_TAG_SCHEMA],
        ),
        vol.Required(CONF_ADAPTER): vol.Schema({
            vol.Required(
                CONF_RUUVI_PLATFORM_TYPE
            ): vol.In([CONF_BLUETOOTH, CONF_GATEWAY]),
            vol.Optional(CONF_BLUETOOTH): BLUETOOTH_ADAPTER_OPTIONS_SCHEMA,
            vol.Optional(CONF_GATEWAY): GATEWAY_ADAPTER_OPTIONS_SCHEMA
        })
    }
)
