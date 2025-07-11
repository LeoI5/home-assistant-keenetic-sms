from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from .coordinator import KeeneticSMSDataUpdateCoordinator

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["keenetic_sms"][entry.entry_id]
    async_add_entities([KeeneticSMSSensor(coordinator)], True)

class KeeneticSMSSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: KeeneticSMSDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_name = "Keenetic SMS"

    @property
    def state(self):
        msgs = self.coordinator.data or []
        return msgs[-1]["date"] if msgs else None

    @property
    def extra_state_attributes(self):
        msgs = self.coordinator.data or []
        return {
            "message_count": len(msgs),
            "messages": {
                str(i + 1): {"from": m["sender"], "time": m["date"], "text": m["content"]}
                for i, m in enumerate(msgs)
            }
        }
