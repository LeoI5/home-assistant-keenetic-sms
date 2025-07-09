import asyncio
import logging
import aiohttp
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from smspdudecoder.easy import read_incoming_sms

_LOGGER = logging.getLogger(__name__)

API_URL = "http://192.168.0.1:81/rci/interface/UsbLte0/tty/send"

class KeeneticSMSDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="Keenetic SMS",
            update_interval=timedelta(seconds=60),  # можно сделать настраиваемым
        )
        self.session = aiohttp.ClientSession()

    async def _async_update_data(self):
        try:
            async with self.session.post(API_URL, json={"command": "AT+CMGL=4"}) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP error: {resp.status}")
                json_data = await resp.json()
                lines = json_data.get("tty-out", [])

            return self._parse_sms(lines)

        except Exception as err:
            _LOGGER.error("Error updating SMS data: %s", err)
            return []

    def _parse_sms(self, lines):
        messages = []
        for i in range(len(lines) - 1):
            if lines[i].startswith("+CMGL:"):
                pdu = lines[i + 1]
                try:
                    sms_data = read_incoming_sms(pdu)
                    messages.append({
                        "sender": sms_data["sender"],
                        "content": sms_data["content"],
                        "date": sms_data["date"]
                    })
                except Exception as e:
                    _LOGGER.warning("Failed to decode SMS: %s", e)
        return messages
