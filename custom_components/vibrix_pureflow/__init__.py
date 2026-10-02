"""The Vibrix PureFlow integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST
from homeassistant.core import HomeAssistant

from .api import VibrixLocalApi
from .const import CONF_LOCAL_KEY, CONF_PROTOCOL_VERSION, PLATFORMS
from .coordinator import VibrixDataUpdateCoordinator


@dataclass
class VibrixRuntimeData:
    """Runtime data for a Vibrix config entry."""

    coordinator: VibrixDataUpdateCoordinator


type VibrixConfigEntry = ConfigEntry[VibrixRuntimeData]


async def async_setup_entry(
    hass: HomeAssistant, entry: VibrixConfigEntry
) -> bool:
    """Set up Vibrix PureFlow from a config entry."""
    api = VibrixLocalApi(
        host=entry.data[CONF_HOST],
        device_id=entry.data[CONF_DEVICE_ID],
        local_key=entry.data[CONF_LOCAL_KEY],
        protocol_version=entry.data[CONF_PROTOCOL_VERSION],
    )
    coordinator = VibrixDataUpdateCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = VibrixRuntimeData(coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: VibrixConfigEntry
) -> bool:
    """Unload a Vibrix PureFlow config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False

    await entry.runtime_data.coordinator.async_close()
    return True
