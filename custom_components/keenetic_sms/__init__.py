
import asyncio
import logging
import aiohttp
import voluptuous as vol
from homeassistant.const import CONF_URL
from homeassistant.helpers import discovery
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta

from .const import DOMAIN, CONF_INTERVAL

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_URL): str,
        vol.Optional(CONF_INTERVAL, default=300): int,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    conf = config[DOMAIN]
    url = conf[CONF_URL]
    interval = conf[CONF_INTERVAL]

    coordinator = KeeneticSMSCoordinator(hass, url, interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN] = coordinator

    hass.async_create_task(discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config))
    return True

class KeeneticSMSCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, interval):
        self.url = url
        super().__init__(
            hass,
            _LOGGER,
            name="Keenetic SMS",
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json={"command": "AT+CMGL=4"}) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status}")
                    data = await resp.json()
                    return data.get("tty-out", [])
        except Exception as e:
            raise UpdateFailed(f"Error fetching SMS: {e}")
