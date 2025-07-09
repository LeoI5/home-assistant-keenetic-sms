from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNKNOWN
from datetime import datetime

DOMAIN = "keenetic_sms"

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KeeneticSMSDumpSensor(coordinator)])

class KeeneticSMSDumpSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Keenetic SMS Dump"
        self._attr_unique_id = "keenetic_sms_dump"

    @property
    def state(self):
        messages = self.coordinator.data or []
        if messages:
            return datetime.now().isoformat(timespec="seconds")
        return STATE_UNKNOWN

    @property
    def extra_state_attributes(self):
        messages = self.coordinator.data or []
        result = {}

        for idx, msg in enumerate(messages):
            result[f"sms_{idx+1:02d}_from"] = msg["sender"]
            result[f"sms_{idx+1:02d}_time"] = msg["date"]
            result[f"sms_{idx+1:02d}_text"] = msg["content"]

        result["message_count"] = len(messages)
        return result

    async def async_update(self):
        await self.coordinator.async_request_refresh()
