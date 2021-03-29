from homeassistant import config_entries
from typing import Any, Dict, Optional
from .const import DOMAIN
import voluptuous as vol
from .sensor import CONF_MAC, CONF_NAME, CONF_SENSORS, SENSOR_TYPES, CONF_MONITORED_CONDITIONS

import homeassistant.helpers.config_validation as cv

CONFIG_FLOW_RUUVI_ADD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME): cv.string
    }
)

config_schema = {}
for condition in SENSOR_TYPES.keys():
  config_schema[vol.Optional(condition)] = cv.boolean

CONFIG_FLOW_RUUVI_CONFIG_SCHEMA = vol.Schema(
  config_schema
)

ADD_ANOTHER_SCHEMA = vol.Schema(
  {
    vol.Optional("add_another"): cv.boolean
  }
)

class RuuviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input=None):
        """Invoked when a user initiates a flow via the user interface."""
        self.data = {
          CONF_SENSORS: []
        }
        self.previous_step_data = {}
        return await self.async_step_add_sensor()

    async def async_step_add_sensor(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if user_input is not None:
            # VALIDATE HERE
            if not errors:
                self.previous_step_data = {
                        CONF_MAC: user_input[CONF_MAC],
                        CONF_NAME: user_input.get(CONF_NAME, None),            
                }
                return await self.async_step_config_sensor()

        return self.async_show_form(
            step_id="add_sensor", data_schema=CONFIG_FLOW_RUUVI_ADD_SCHEMA, errors=errors
        )
  
    async def async_step_config_sensor(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            # VALIDATE HERE
            if not errors:
                # Input is valid, set data.
                self.data[CONF_SENSORS].append(
                    {
                        CONF_MAC: self.previous_step_data[CONF_MAC],
                        CONF_NAME: self.previous_step_data[CONF_NAME],
                        CONF_MONITORED_CONDITIONS: [x for x in SENSOR_TYPES.keys() if user_input.get(x, False)]
                    }
                )
                return await self.async_step_add_another()

        return self.async_show_form(
            step_id="config_sensor", data_schema=CONFIG_FLOW_RUUVI_CONFIG_SCHEMA, errors=errors
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
            step_id="add_another", data_schema=ADD_ANOTHER_SCHEMA, errors=errors
        )
