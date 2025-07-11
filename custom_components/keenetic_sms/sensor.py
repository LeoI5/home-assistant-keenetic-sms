import logging
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .coordinator import KeeneticSMSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["keenetic_sms"]
    async_add_entities([KeeneticSMSSensor(coordinator)], True)


class KeeneticSMSSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: KeeneticSMSDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_name = "Keenetic SMS"

    @property
    def state(self):
        messages = self.coordinator.data or []
        if messages:
            return messages[-1]["date"]
        return None

    @property
    def extra_state_attributes(self):
        messages = self.coordinator.data or []
        return {
            "message_count": len(messages),
            "messages": {
                str(i + 1): {
                    "from": m["sender"],
                    "time": m["date"],
                    "text": m["content"]
                }
                for i, m in enumerate(messages)
            }
        }
