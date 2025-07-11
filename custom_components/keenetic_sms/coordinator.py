import asyncio
import logging
import re
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from smspdudecoder.easy import read_incoming_sms
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class KeeneticSMSDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host: str, interval: int):
        super().__init__(hass, _LOGGER, name="Keenetic SMS",
                         update_interval=timedelta(seconds=interval))
        self.session = async_get_clientsession(hass)
        self._url = f"{host}/rci/interface/UsbLte0/tty/send"

    async def _async_update_data(self):
        try:
            resp = await self.session.post(self._url, json={"command": "AT+CMGL=4"})
            resp.raise_for_status()
            json_data = await resp.json()
            lines = json_data.get("tty-out", [])
            messages = self._parse_sms(lines)

            if len(messages) >= 4:
                oldest = min(messages, key=lambda x: x["date"])
                idx = oldest["index"]
                _LOGGER.info("Deleting oldest SMS index=%s date=%s", idx, oldest["date"])
                await self.session.post(self._url, json={"command": f"AT+CMGD={idx}"})
                await asyncio.sleep(1)
                resp = await self.session.post(self._url, json={"command": "AT+CMGL=4"})
                resp.raise_for_status()
                lines = (await resp.json()).get("tty-out", [])
                messages = self._parse_sms(lines)

            messages = sorted(messages, key=lambda x: x["date"])
            return messages

        except Exception as e:
            _LOGGER.error("Error updating SMS data: %s", e)
            return []

    def _parse_sms(self, lines: list[str]) -> list[dict]:
        messages = []
        for i in range(len(lines) - 1):
            if lines[i].startswith("+CMGL:"):
                m = re.match(r"\+CMGL: (\d+),", lines[i])
                if not m:
                    continue
                idx = int(m.group(1))
                pdu = lines[i + 1]
                try:
                    sms = read_incoming_sms(pdu)
                    messages.append({
                        "index": idx,
                        "sender": sms["sender"],
                        "content": sms["content"],
                        "date": sms["date"]
                    })
                except Exception as ex:
                    _LOGGER.warning("Failed to decode SMS idx=%s: %s", idx, ex)
        return messages
