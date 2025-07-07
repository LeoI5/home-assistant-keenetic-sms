
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL, CONF_SCAN_INTERVAL

from .const import DOMAIN

class KeeneticSMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Keenetic SMS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_URL): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=300): int,
            }),
            errors=errors,
        )
