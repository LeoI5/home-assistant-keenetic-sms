import asyncio
import logging
import aiohttp
import re
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
            # Чтение SMS
            async with self.session.post(API_URL, json={"command": "AT+CMGL=4"}) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP error: {resp.status}")
                json_data = await resp.json()
                lines = json_data.get("tty-out", [])

            messages = self._parse_sms(lines)

            # Удаление, если сообщений слишком много
            if len(messages) >= 4:
                oldest = min(messages, key=lambda x: x["date"])
                index = oldest["index"]
                _LOGGER.info("Deleting oldest SMS index=%s, date=%s", index, oldest["date"])
                await self._send_at_command(f"AT+CMGD={index}")

                # Перечитать список после удаления
                await asyncio.sleep(1)
                async with self.session.post(API_URL, json={"command": "AT+CMGL=4"}) as resp:
                    json_data = await resp.json()
                    lines = json_data.get("tty-out", [])
                    messages = self._parse_sms(lines)

            # Сортировка от самого старого к новому
            messages = sorted(messages, key=lambda x: x["date"])
            return messages

        except Exception as err:
            _LOGGER.error("Error updating SMS data: %s", err)
            return []

    def _parse_sms(self, lines):
        messages = []
        for i in range(len(lines) - 1):
            if lines[i].startswith("+CMGL:"):
                match = re.match(r"\+CMGL: (\d+),", lines[i])
                if not match:
                    continue
                index = int(match.group(1))
                pdu = lines[i + 1]
                try:
                    sms_data = read_incoming_sms(pdu)
                    messages.append({
                        "index": index,
                        "sender": sms_data["sender"],
                        "content": sms_data["content"],
                        "date": sms_data["date"]
                    })
                except Exception as e:
                    _LOGGER.warning("Failed to decode SMS (index=%s): %s", index, e)
        return messages

    async def _send_at_command(self, command):
        try:
            async with self.session.post(API_URL, json={"command": command}) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to send AT command '%s': %s", command, resp.status)
        except Exception as e:
            _LOGGER.error("Error sending AT command '%s': %s", command, e)
