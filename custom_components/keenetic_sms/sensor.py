
from homeassistant.helpers.entity import Entity
from .const import DOMAIN
import re

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    coordinator = hass.data[DOMAIN]
    async_add_entities([KeeneticSMSSensor(coordinator)], True)

class KeeneticSMSSensor(Entity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Keenetic SMS"
        self._attr_unique_id = "keenetic_sms_decoded"
        self._attr_icon = "mdi:message-text"

    async def async_update(self):
        await self.coordinator.async_request_refresh()

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
