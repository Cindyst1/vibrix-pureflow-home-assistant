"""Local LAN client for Vibrix PureFlow devices."""

from __future__ import annotations

from typing import Any

import tinytuya


class VibrixApiError(Exception):
    """Base exception for local device communication."""


class VibrixLocalApi:
    """Synchronous TinyTuya wrapper used from Home Assistant's executor."""

    def __init__(
        self,
        host: str,
        device_id: str,
        local_key: str,
        protocol_version: str,
    ) -> None:
        """Initialize the local API client."""
        self._device = tinytuya.Device(
            dev_id=device_id,
            address=host,
            local_key=local_key,
            version=float(protocol_version),
            connection_timeout=5,
            connection_retry_limit=1,
            connection_retry_delay=1,
        )

    def status(self) -> dict[str, Any]:
        """Fetch and normalize all reported datapoints."""
        response = self._device.status()
        self._raise_for_error(response)

        dps = response.get("dps") if isinstance(response, dict) else None
        if not isinstance(dps, dict) or not dps:
            raise VibrixApiError("Het apparaat gaf geen datapoints terug")

        return {str(dp_id): value for dp_id, value in dps.items()}

    def set_values(self, values: list[tuple[str, Any]]) -> None:
        """Write one or more datapoint values."""
        response = self._device.set_multiple_values(dict(values))
        self._raise_for_error(response)

    def close(self) -> None:
        """Close a possible lingering socket."""
        self._device.close()

    @staticmethod
    def _raise_for_error(response: Any) -> None:
        """Turn TinyTuya error dictionaries into exceptions."""
        if response is None:
            raise VibrixApiError("Geen antwoord van het apparaat")
        if not isinstance(response, dict):
            raise VibrixApiError("Onverwacht antwoord van het apparaat")

        error = response.get("Error") or response.get("error")
        error_code = response.get("Err")
        if error or error_code:
            detail = error or "onbekende fout"
            if error_code:
                detail = f"{detail} (code {error_code})"
            raise VibrixApiError(str(detail))
