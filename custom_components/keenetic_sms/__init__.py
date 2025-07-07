
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from datetime import timedelta
import aiohttp

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    url = entry.data["url"]
    interval = entry.data.get("scan_interval", 300)

    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            async with session.post(url, json={"command": "AT+CMGL=4"}) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP error: {resp.status}")
                data = await resp.json()
                return data.get("tty-out", [])
        except Exception as err:
            raise UpdateFailed(f"Update error: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Keenetic SMS",
        update_method=async_update_data,
        update_interval=timedelta(seconds=interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
