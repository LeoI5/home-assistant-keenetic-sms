
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import re

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KeeneticSMSSensor(coordinator)], True)

class KeeneticSMSSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Keenetic SMS"
        self._attr_unique_id = "keenetic_sms_decoded"
        self._attr_icon = "mdi:message-text"

    @property
    def state(self):
        return self._parse_sms(self.coordinator.data)

    def _parse_sms(self, lines):
        def decode_ucs2(pdu):
            try:
                match = re.search(r'([0-9A-Fa-f]{40,})$', pdu)
                if not match:
                    return ""
                hex_part = match.group(1)
                return bytes.fromhex(hex_part).decode('utf-16-be')
            except Exception:
                return "[decode error]"

        pdu_lines = [lines[i + 1] for i in range(len(lines) - 1) if lines[i].startswith("+CMGL:")]
        decoded = [decode_ucs2(pdu) for pdu in pdu_lines]
        return "\n\n".join(decoded)
