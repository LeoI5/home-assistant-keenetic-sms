from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN

DOMAIN = "keenetic_sms"

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KeeneticSMSSensor(coordinator)])

class KeeneticSMSSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Keenetic Last SMS"
        self._attr_unique_id = "keenetic_last_sms"

    @property
    def state(self):
        messages = self.coordinator.data or []
        if messages:
            return messages[-1]["content"]
        return STATE_UNKNOWN

    @property
    def extra_state_attributes(self):
        messages = self.coordinator.data or []
        if messages:
            last = messages[-1]
            return {
                "from": last["sender"],
                "date": last["date"],
                "message_count": len(messages),
            }
        return {
            "message_count": 0
        }

    async def async_update(self):
        await self.coordinator.async_request_refresh()
