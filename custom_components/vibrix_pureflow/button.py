"""Button platform for the Vibrix PureFlow integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VibrixConfigEntry
from .const import CONF_FILTER_RESET_DP
from .entity import VibrixEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VibrixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the configured filter reset button."""
    if entry.data.get(CONF_FILTER_RESET_DP):
        async_add_entities([VibrixFilterResetButton(entry)])


class VibrixFilterResetButton(VibrixEntity, ButtonEntity):
    """Reset the reported filter life after replacement."""

    _attr_translation_key = "filter_reset"
    _attr_icon = "mdi:air-filter"

    def __init__(self, entry: VibrixConfigEntry) -> None:
        """Initialize the filter reset button."""
        super().__init__(entry, "filter_reset")
        self._dp_id = entry.data[CONF_FILTER_RESET_DP]

    async def async_press(self) -> None:
        """Send the momentary filter reset command."""
        await self.coordinator.async_set_values([(self._dp_id, True)])
