"""Config flow for Ruuvi."""
from homeassistant import config_entries

from typing import Any, Dict, Optional
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_flow

from .const import (
    DOMAIN, CONF_RUUVI_PLATFORM_TYPE, CONF_BLUETOOTH, CONF_GATEWAY,
    CONF_ADAPTER, CONF_SENSORS, CONF_RUUVI_PLATFORM_TYPE
)
from .schemas import (
    CONFIG_FLOW_CHOOSE_PLATFORM_SCHEMA,
    GATEWAY_ADAPTER_OPTIONS_SCHEMA,
    BLUETOOTH_ADAPTER_OPTIONS_SCHEMA,
    CONFIG_FLOW_ADD_ANOTHER_SCHEMA,
    BASE_RUUVI_TAG_SCHEMA
)


class RuuviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    metadata = {}
    data = {
        CONF_SENSORS: [],
        CONF_ADAPTER: {}
    }

    async def async_step_user(self, user_input=None):
        # CHOSE TYPE
        """Invoked when a user initiates a flow via the user interface."""
        return await self.async_step_choose_platform()

    async def async_step_choose_platform(self, user_input: Optional[Dict[str, Any]] = None):
        """
        Chooses if we're setuping a bluetooth or a Gateway
        """
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.data[CONF_ADAPTER][CONF_RUUVI_PLATFORM_TYPE] = user_input[CONF_RUUVI_PLATFORM_TYPE]
                if user_input[CONF_RUUVI_PLATFORM_TYPE] == CONF_BLUETOOTH:
                    return await self.async_step_configure_bluetooth()
                elif user_input[CONF_RUUVI_PLATFORM_TYPE] == CONF_GATEWAY:
                    return await self.async_step_configure_gateway()

        return self.async_show_form(
            step_id="choose_platform", data_schema=CONFIG_FLOW_CHOOSE_PLATFORM_SCHEMA, errors=errors
        )

    async def async_step_configure_bluetooth(self, user_input: Optional[Dict[str, Any]] = None):
        """
        Chooses if we're setuping a bluetooth or a Gateway
        """
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.data[CONF_ADAPTER][self.data[CONF_ADAPTER][CONF_RUUVI_PLATFORM_TYPE]] = user_input
            return await self.async_step_add_sensor()

        return self.async_show_form(
            step_id="configure_bluetooth", data_schema=BLUETOOTH_ADAPTER_OPTIONS_SCHEMA, errors=errors
        )

    async def async_step_configure_gateway(self, user_input: Optional[Dict[str, Any]] = None):
        """
        Chooses if we're setuping a bluetooth or a Gateway
        """
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                # TODO -- TODO
                return await self.async_step_add_sensor()

        return self.async_show_form(
            step_id="configure_gateway", data_schema=GATEWAY_ADAPTER_OPTIONS_SCHEMA, errors=errors
        )

    async def async_step_add_sensor(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                self.data[CONF_SENSORS].append(user_input)
                return await self.async_step_add_another()

        return self.async_show_form(
            step_id="add_sensor", data_schema=BASE_RUUVI_TAG_SCHEMA, errors=errors
        )

    async def async_step_add_another(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            # VALIDATE HERE
            if not errors:
                # If user ticked the box show this form again so they can add an
                # additional repo.
                if user_input.get("add_another", False):
                    return await self.async_step_add_sensor()

                # User is done adding repos, create the config entry.
                return self.async_create_entry(
                    title="Ruuvi Sensors",
                    data=self.data
                )

        return self.async_show_form(
            step_id="add_another", data_schema=CONFIG_FLOW_ADD_ANOTHER_SCHEMA, errors=errors
        )
