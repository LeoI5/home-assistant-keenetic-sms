from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import KeeneticSMSDataUpdateCoordinator

DOMAIN = "keenetic_sms"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = KeeneticSMSDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN] = coordinator

    # ✅ Новый корректный способ
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unloaded:
        hass.data.pop(DOMAIN, None)
    return unloaded
