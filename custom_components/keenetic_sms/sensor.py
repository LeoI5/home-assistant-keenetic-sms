from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN

DOMAIN = "keenetic_sms"

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KeeneticSMSSensor(coordinator)])

class KeeneticSMSSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Keenetic SMS"
        self._attr_unique_id = "keenetic_sms"

    @property
    def state(self):
        messages = self.coordinator.data or []
        if messages:
            # Отдаём дату последнего SMS (в ISO формате)
            return messages[-1]["date"]
        return STATE_UNKNOWN

    @property
    def extra_state_attributes(self):
        messages = self.coordinator.data or []
        result = {"message_count": len(messages)}
        for idx, msg in enumerate(messages):
            result[f"sms_{idx+1:02d}_from"] = msg["sender"]
            result[f"sms_{idx+1:02d}_time"] = msg["date"]
            result[f"sms_{idx+1:02d}_text"] = msg["content"]
        return result

    async def async_update(self):
        await self.coordinator.async_request_refresh()
