
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
            CONF_RUUVI_PLATFORM_TYPE,
            default=CONF_BLUETOOTH,
        ): vol.In([CONF_BLUETOOTH, CONF_GATEWAY])
    }
)

CONFIG_FLOW_ADD_ANOTHER_SCHEMA = vol.Schema(
    {
        vol.Optional("add_another"): cv.boolean
    }
)


RUUVI_TAG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(
            CONF_MONITORED_CONDITIONS,
            default=list(SENSOR_TYPES)): vol.All(
                cv.ensure_list,
                [vol.In(SENSOR_TYPES)]),
        vol.Optional(
            CONF_MAX_UPDATE_FREQUENCY,
            default=DEFAULT_UPDATE_FREQUENCY): cv.positive_int
    }
)


BLUETOOTH_ADAPTER_OPTIONS_SCHEMA = vol.Schema({
    vol.Optional(CONF_ADAPTER, default=DEFAULT_ADAPTER): cv.string,
})

BLUETOOTH_ADAPTER_SCHEMA = BLUETOOTH_ADAPTER_OPTIONS_SCHEMA.extend(
    {
        vol.Required(CONF_SENSORS): vol.All(
            cv.ensure_list,
            [RUUVI_TAG_SCHEMA],
        ),
    }
)

GATEWAY_ADAPTER_OPTIONS_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,
})


GATEWAY_ADAPTER_SCHEMA = GATEWAY_ADAPTER_OPTIONS_SCHEMA.extend(
    {
        vol.Required(CONF_SENSORS): vol.All(
            cv.ensure_list,
            [RUUVI_TAG_SCHEMA],
        ),
    }
)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_BLUETOOTH): vol.All(
            cv.ensure_list,
            [BLUETOOTH_ADAPTER_SCHEMA],
        ),
        vol.Optional(CONF_GATEWAY): vol.All(
            cv.ensure_list,
            [GATEWAY_ADAPTER_SCHEMA],
        ),
    }
)
