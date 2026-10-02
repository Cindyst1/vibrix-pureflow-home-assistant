"""Data coordinator for the Vibrix PureFlow integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VibrixApiError, VibrixLocalApi
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class VibrixDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate local polling and serialized writes."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: VibrixLocalApi,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self._device_lock = asyncio.Lock()
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=config_entry.data.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                )
            ),
            always_update=False,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch current datapoints from the purifier."""
        try:
            async with self._device_lock:
                return await self.hass.async_add_executor_job(self.api.status)
        except VibrixApiError as err:
            raise UpdateFailed(str(err)) from err
        except OSError as err:
            raise UpdateFailed(f"Netwerkfout: {err}") from err
        except Exception as err:
            raise UpdateFailed(
                f"Onverwachte lokale communicatiefout ({type(err).__name__})"
            ) from err

    async def async_set_values(self, values: list[tuple[str, Any]]) -> None:
        """Write one or more values in order and refresh once."""
        try:
            async with self._device_lock:
                await self.hass.async_add_executor_job(
                    self.api.set_values, values
                )
        except (VibrixApiError, OSError) as err:
            raise HomeAssistantError(
                f"Kon opdracht niet naar de PureFlow sturen: {err}"
            ) from err
        except Exception as err:
            raise HomeAssistantError(
                "Kon opdracht niet naar de PureFlow sturen "
                f"({type(err).__name__})"
            ) from err

        await self.async_request_refresh()

    async def async_close(self) -> None:
        """Close the underlying client."""
        async with self._device_lock:
            await self.hass.async_add_executor_job(self.api.close)
