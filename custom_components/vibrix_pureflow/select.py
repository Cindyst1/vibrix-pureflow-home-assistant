"""Select platform for the Vibrix PureFlow integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VibrixConfigEntry
from .const import CONF_COUNTDOWN_DP, CONF_COUNTDOWN_VALUES
from .entity import VibrixEntity
from .util import parse_csv_values


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VibrixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the configured countdown selector."""
    if entry.data.get(CONF_COUNTDOWN_DP):
        async_add_entities([VibrixCountdownSelect(entry)])


class VibrixCountdownSelect(VibrixEntity, SelectEntity):
    """Select when the purifier should turn off."""

    _attr_translation_key = "countdown"
    _attr_icon = "mdi:timer-outline"

    def __init__(self, entry: VibrixConfigEntry) -> None:
        """Initialize the countdown selector."""
        super().__init__(entry, "countdown")
        self._dp_id = entry.data[CONF_COUNTDOWN_DP]
        values = parse_csv_values(entry.data.get(CONF_COUNTDOWN_VALUES, ""))
        self._values: dict[str, Any] = {str(value): value for value in values}
        self._attr_options = list(self._values)

    @property
    def current_option(self) -> str | None:
        """Return the active countdown option."""
        current = self.coordinator.data.get(str(self._dp_id))
        return next(
            (
                option
                for option, raw_value in self._values.items()
                if raw_value == current
            ),
            None,
        )

    async def async_select_option(self, option: str) -> None:
        """Set the countdown option."""
        await self.coordinator.async_set_values(
            [(self._dp_id, self._values[option])]
        )
