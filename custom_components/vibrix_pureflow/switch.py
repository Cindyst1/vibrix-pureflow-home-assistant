"""Switch platform for the Vibrix PureFlow integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VibrixConfigEntry
from .const import CONF_CHILD_LOCK_DP, CONF_DISPLAY_DP, CONF_IONIZER_DP
from .entity import VibrixEntity


@dataclass(frozen=True, kw_only=True)
class VibrixSwitchDescription(SwitchEntityDescription):
    """Describe a PureFlow switch."""

    dp_config_key: str


SWITCHES = (
    VibrixSwitchDescription(
        key="ionizer",
        translation_key="ionizer",
        dp_config_key=CONF_IONIZER_DP,
        icon="mdi:creation",
    ),
    VibrixSwitchDescription(
        key="child_lock",
        translation_key="child_lock",
        dp_config_key=CONF_CHILD_LOCK_DP,
        icon="mdi:lock",
    ),
    VibrixSwitchDescription(
        key="display",
        translation_key="display",
        dp_config_key=CONF_DISPLAY_DP,
        icon="mdi:monitor",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VibrixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up configured PureFlow switches."""
    async_add_entities(
        VibrixPureFlowSwitch(entry, description)
        for description in SWITCHES
        if entry.data.get(description.dp_config_key)
    )


class VibrixPureFlowSwitch(VibrixEntity, SwitchEntity):
    """Representation of a boolean PureFlow datapoint."""

    entity_description: VibrixSwitchDescription

    def __init__(
        self,
        entry: VibrixConfigEntry,
        description: VibrixSwitchDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(entry, description.key)
        self.entity_description = description
        self._dp_id = entry.data[description.dp_config_key]

    @property
    def is_on(self) -> bool | None:
        """Return the switch state."""
        value = self.dp_value(self.entity_description.dp_config_key)
        return value if isinstance(value, bool) else None

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn on the feature."""
        await self.coordinator.async_set_values([(self._dp_id, True)])

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn off the feature."""
        await self.coordinator.async_set_values([(self._dp_id, False)])
