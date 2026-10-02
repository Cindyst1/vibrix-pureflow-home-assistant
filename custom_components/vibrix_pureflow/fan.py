"""Fan platform for the Vibrix PureFlow integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from . import VibrixConfigEntry
from .const import (
    CONF_AUTO_MODE_VALUE,
    CONF_MANUAL_MODE_VALUE,
    CONF_MODE_DP,
    CONF_POWER_DP,
    CONF_SLEEP_MODE_VALUE,
    CONF_SPEED_DP,
    CONF_SPEED_VALUES,
)
from .entity import VibrixEntity
from .util import parse_csv_values, parse_scalar

PRESET_AUTO = "auto"
PRESET_SLEEP = "sleep"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VibrixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PureFlow fan entity."""
    async_add_entities([VibrixPureFlowFan(entry)])


class VibrixPureFlowFan(VibrixEntity, FanEntity):
    """Representation of the air purifier fan."""

    _attr_name = None
    _attr_icon = "mdi:air-purifier"

    def __init__(self, entry: VibrixConfigEntry) -> None:
        """Initialize the fan entity."""
        super().__init__(entry, "fan")
        self._power_dp = entry.data[CONF_POWER_DP]
        self._speed_dp = entry.data.get(CONF_SPEED_DP)
        self._mode_dp = entry.data.get(CONF_MODE_DP)
        self._speed_values = parse_csv_values(
            entry.data.get(CONF_SPEED_VALUES, "")
        )
        self._manual_mode_value = parse_scalar(
            entry.data.get(CONF_MANUAL_MODE_VALUE, "")
        )
        self._preset_values = {
            PRESET_AUTO: parse_scalar(
                entry.data.get(CONF_AUTO_MODE_VALUE, "")
            ),
            PRESET_SLEEP: parse_scalar(
                entry.data.get(CONF_SLEEP_MODE_VALUE, "")
            ),
        }
        self._preset_values = {
            preset: value
            for preset, value in self._preset_values.items()
            if value != ""
        }

        supported = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        if self._speed_dp and self._speed_values:
            supported |= FanEntityFeature.SET_SPEED
        if self._mode_dp and self._preset_values:
            supported |= FanEntityFeature.PRESET_MODE
        self._attr_supported_features = supported

    @property
    def is_on(self) -> bool | None:
        """Return whether the purifier is on."""
        value = self.coordinator.data.get(str(self._power_dp))
        return value if isinstance(value, bool) else None

    @property
    def percentage(self) -> int | None:
        """Return the current manual fan speed percentage."""
        if not self._speed_dp or not self._speed_values or not self.is_on:
            return 0 if self.is_on is False else None
        value = self.coordinator.data.get(str(self._speed_dp))
        if value not in self._speed_values:
            return None
        return ordered_list_item_to_percentage(self._speed_values, value)

    @property
    def speed_count(self) -> int:
        """Return the number of configured manual speeds."""
        return len(self._speed_values)

    @property
    def preset_modes(self) -> list[str] | None:
        """Return supported automatic modes."""
        if not self._mode_dp:
            return None
        return list(self._preset_values)

    @property
    def preset_mode(self) -> str | None:
        """Return the active automatic mode."""
        if not self._mode_dp:
            return None
        current = self.coordinator.data.get(str(self._mode_dp))
        return next(
            (
                preset
                for preset, value in self._preset_values.items()
                if value == current
            ),
            None,
        )

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the purifier, optionally with a mode or speed."""
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
            return
        if percentage is not None:
            await self.async_set_percentage(percentage)
            return
        await self.coordinator.async_set_values([(self._power_dp, True)])

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the purifier."""
        await self.coordinator.async_set_values([(self._power_dp, False)])

    async def async_set_percentage(self, percentage: int) -> None:
        """Set a configured manual speed."""
        if percentage == 0:
            await self.async_turn_off()
            return
        if not self._speed_dp or not self._speed_values:
            return

        values: list[tuple[str, Any]] = [(self._power_dp, True)]
        if self._mode_dp and self._manual_mode_value != "":
            values.append((self._mode_dp, self._manual_mode_value))
        values.append(
            (
                self._speed_dp,
                percentage_to_ordered_list_item(
                    self._speed_values, percentage
                ),
            )
        )
        await self.coordinator.async_set_values(values)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set automatic or sleep mode."""
        if preset_mode not in self._preset_values or not self._mode_dp:
            raise ValueError(f"Onbekende presetmodus: {preset_mode}")
        await self.coordinator.async_set_values(
            [
                (self._power_dp, True),
                (self._mode_dp, self._preset_values[preset_mode]),
            ]
        )
