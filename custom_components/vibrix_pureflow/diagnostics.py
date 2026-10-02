"""Diagnostics support for Vibrix PureFlow."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST
from homeassistant.core import HomeAssistant

from . import VibrixConfigEntry
from .const import CONF_LOCAL_KEY

TO_REDACT = {CONF_DEVICE_ID, CONF_HOST, CONF_LOCAL_KEY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: VibrixConfigEntry
) -> dict[str, Any]:
    """Return redacted config and current local datapoints."""
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "datapoints": entry.runtime_data.coordinator.data,
        "last_update_success": (
            entry.runtime_data.coordinator.last_update_success
        ),
    }
