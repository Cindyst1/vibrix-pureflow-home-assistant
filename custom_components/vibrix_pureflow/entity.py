"""Base entity for the Vibrix PureFlow integration."""

from __future__ import annotations

from typing import Any

from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VibrixConfigEntry
from .const import DOMAIN
from .coordinator import VibrixDataUpdateCoordinator


class VibrixEntity(CoordinatorEntity[VibrixDataUpdateCoordinator]):
    """Base class shared by all PureFlow entities."""

    _attr_has_entity_name = True

    def __init__(self, entry: VibrixConfigEntry, unique_suffix: str) -> None:
        """Initialize a PureFlow entity."""
        coordinator = entry.runtime_data.coordinator
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = (
            f"{entry.data[CONF_DEVICE_ID]}_{unique_suffix}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return the purifier device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.data[CONF_DEVICE_ID])},
            manufacturer="Vibrix",
            model="PureFlow15 Pro",
            name=self.entry.title,
        )

    def dp_value(self, config_key: str) -> Any:
        """Return the current value for a configured datapoint."""
        dp_id = self.entry.data.get(config_key)
        if not dp_id:
            return None
        return self.coordinator.data.get(str(dp_id))
