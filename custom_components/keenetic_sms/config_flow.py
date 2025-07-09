from homeassistant import config_entries

class KeeneticSMSConfigFlow(config_entries.ConfigFlow, domain="keenetic_sms"):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Keenetic SMS", data={})
        return self.async_show_form(step_id="user")
