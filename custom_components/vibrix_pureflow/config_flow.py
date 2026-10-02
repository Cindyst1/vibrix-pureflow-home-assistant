"""Config flow for the Vibrix PureFlow integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import VibrixApiError, VibrixLocalApi
from .const import (
    CONF_AIR_QUALITY_DP,
    CONF_AUTO_MODE_VALUE,
    CONF_CHILD_LOCK_DP,
    CONF_COUNTDOWN_DP,
    CONF_COUNTDOWN_VALUES,
    CONF_DISPLAY_DP,
    CONF_FILTER_LIFE_DP,
    CONF_FILTER_RESET_DP,
    CONF_IONIZER_DP,
    CONF_LOCAL_KEY,
    CONF_MANUAL_MODE_VALUE,
    CONF_MODE_DP,
    CONF_PM25_DP,
    CONF_POWER_DP,
    CONF_PROTOCOL_VERSION,
    CONF_SCAN_INTERVAL,
    CONF_SLEEP_MODE_VALUE,
    CONF_SPEED_DP,
    CONF_SPEED_VALUES,
    CONF_VOC_DP,
    DEFAULT_COUNTDOWN_VALUES,
    DEFAULT_PROTOCOL_VERSION,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SPEED_VALUES,
    DOMAIN,
    NOT_CONFIGURED,
    OPTIONAL_DP_KEYS,
    PROTOCOL_VERSIONS,
)
from .util import format_dps, parse_csv_values

_LOGGER = logging.getLogger(__name__)

LOCAL_KEY_SELECTOR = TextSelector(
    TextSelectorConfig(
        type=TextSelectorType.PASSWORD,
        autocomplete="current-password",
    )
)


class CannotConnect(Exception):
    """Raised when local validation fails."""


async def async_validate_input(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate local credentials and return current datapoints."""
    api = VibrixLocalApi(
        host=data[CONF_HOST],
        device_id=data[CONF_DEVICE_ID],
        local_key=data[CONF_LOCAL_KEY],
        protocol_version=data[CONF_PROTOCOL_VERSION],
    )
    try:
        return await hass.async_add_executor_job(api.status)
    except (VibrixApiError, OSError) as err:
        raise CannotConnect from err
    finally:
        await hass.async_add_executor_job(api.close)


class VibrixPureFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vibrix PureFlow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._connection_data: dict[str, Any] = {}
        self._dps: dict[str, Any] = {}
        self._mapping_defaults: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle local connection settings."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if len(user_input[CONF_LOCAL_KEY]) != 16:
                errors[CONF_LOCAL_KEY] = "invalid_local_key"
            if not errors:
                try:
                    self._dps = await async_validate_input(
                        self.hass, user_input
                    )
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception(
                        "Unexpected error validating PureFlow device"
                    )
                    errors["base"] = "unknown"
                else:
                    await self.async_set_unique_id(
                        user_input[CONF_DEVICE_ID]
                    )
                    self._abort_if_unique_id_configured(
                        {CONF_HOST: user_input[CONF_HOST]}
                    )
                    self._connection_data = user_input
                    return await self.async_step_mapping()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Vibrix PureFlow15"): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_DEVICE_ID): vol.All(
                    str, vol.Length(min=10, max=32)
                ),
                vol.Required(CONF_LOCAL_KEY): LOCAL_KEY_SELECTOR,
                vol.Required(
                    CONF_PROTOCOL_VERSION,
                    default=DEFAULT_PROTOCOL_VERSION,
                ): vol.In(PROTOCOL_VERSIONS),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update local connection settings and datapoint mappings."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_LOCAL_KEY] = (
                user_input.get(CONF_LOCAL_KEY) or entry.data[CONF_LOCAL_KEY]
            )
            if len(user_input[CONF_LOCAL_KEY]) != 16:
                errors[CONF_LOCAL_KEY] = "invalid_local_key"
            if not errors:
                try:
                    self._dps = await async_validate_input(
                        self.hass, user_input
                    )
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception(
                        "Unexpected error reconfiguring PureFlow device"
                    )
                    errors["base"] = "unknown"
                else:
                    await self.async_set_unique_id(
                        user_input[CONF_DEVICE_ID]
                    )
                    self._abort_if_unique_id_mismatch()
                    self._connection_data = {
                        CONF_NAME: entry.title,
                        **user_input,
                    }
                    self._mapping_defaults = dict(entry.data)
                    return await self.async_step_mapping()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST, default=entry.data[CONF_HOST]
                ): str,
                vol.Required(
                    CONF_DEVICE_ID, default=entry.data[CONF_DEVICE_ID]
                ): vol.All(str, vol.Length(min=10, max=32)),
                vol.Optional(CONF_LOCAL_KEY, default=""): LOCAL_KEY_SELECTOR,
                vol.Required(
                    CONF_PROTOCOL_VERSION,
                    default=entry.data[CONF_PROTOCOL_VERSION],
                ): vol.In(PROTOCOL_VERSIONS),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=entry.data.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
            }
        )
        return self.async_show_form(
            step_id="reconfigure", data_schema=schema, errors=errors
        )

    async def async_step_mapping(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Map detected datapoints to PureFlow features."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = self._validate_mapping(user_input)
            if not errors:
                for key in OPTIONAL_DP_KEYS:
                    if user_input.get(key) == NOT_CONFIGURED:
                        user_input[key] = None
                title = self._connection_data.pop(CONF_NAME)
                entry_data = {**self._connection_data, **user_input}
                if self.source == config_entries.SOURCE_RECONFIGURE:
                    return self.async_update_reload_and_abort(
                        self._get_reconfigure_entry(),
                        data_updates=entry_data,
                    )
                return self.async_create_entry(
                    title=title,
                    data=entry_data,
                )
            self._mapping_defaults = dict(user_input)

        choices = {
            NOT_CONFIGURED: "-",
            **{
                dp_id: f"DP {dp_id} - {value!r} ({type(value).__name__})"
                for dp_id, value in self._sorted_dps()
            },
        }
        power_default = self._mapping_default(
            CONF_POWER_DP, self._guess_power_dp()
        )
        speed_default = self._mapping_default(
            CONF_SPEED_DP, self._detected_dp("3", str)
        )
        mode_default = self._mapping_default(
            CONF_MODE_DP, self._detected_dp("3", str)
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_POWER_DP, default=power_default): vol.In(
                    {
                        key: value
                        for key, value in choices.items()
                        if key != NOT_CONFIGURED
                    }
                ),
                vol.Required(
                    CONF_SPEED_DP,
                    default=speed_default,
                ): vol.In(choices),
                vol.Optional(
                    CONF_SPEED_VALUES,
                    default=self._mapping_default(
                        CONF_SPEED_VALUES, DEFAULT_SPEED_VALUES
                    ),
                ): str,
                vol.Required(
                    CONF_MODE_DP,
                    default=mode_default,
                ): vol.In(choices),
                vol.Optional(
                    CONF_MANUAL_MODE_VALUE,
                    default=self._mapping_default(
                        CONF_MANUAL_MODE_VALUE, ""
                    ),
                ): str,
                vol.Optional(
                    CONF_AUTO_MODE_VALUE,
                    default=self._mapping_default(
                        CONF_AUTO_MODE_VALUE, "auto"
                    ),
                ): str,
                vol.Optional(
                    CONF_SLEEP_MODE_VALUE,
                    default=self._mapping_default(
                        CONF_SLEEP_MODE_VALUE, "sleep"
                    ),
                ): str,
                vol.Required(
                    CONF_PM25_DP,
                    default=self._mapping_default(
                        CONF_PM25_DP, self._detected_dp("2", int)
                    ),
                ): vol.In(choices),
                vol.Required(
                    CONF_VOC_DP,
                    default=self._mapping_default(CONF_VOC_DP),
                ): vol.In(choices),
                vol.Required(
                    CONF_AIR_QUALITY_DP,
                    default=self._mapping_default(CONF_AIR_QUALITY_DP),
                ): vol.In(choices),
                vol.Required(
                    CONF_FILTER_LIFE_DP,
                    default=self._mapping_default(
                        CONF_FILTER_LIFE_DP, self._detected_dp("5", int)
                    ),
                ): vol.In(choices),
                vol.Required(
                    CONF_IONIZER_DP,
                    default=self._mapping_default(
                        CONF_IONIZER_DP, self._detected_dp("6", bool)
                    ),
                ): vol.In(choices),
                vol.Required(
                    CONF_CHILD_LOCK_DP,
                    default=self._mapping_default(
                        CONF_CHILD_LOCK_DP, self._detected_dp("7", bool)
                    ),
                ): vol.In(choices),
                vol.Required(
                    CONF_DISPLAY_DP,
                    default=self._mapping_default(
                        CONF_DISPLAY_DP, self._detected_dp("8", bool)
                    ),
                ): vol.In(choices),
                vol.Required(
                    CONF_FILTER_RESET_DP,
                    default=self._mapping_default(
                        CONF_FILTER_RESET_DP,
                        self._detected_dp("11", bool),
                    ),
                ): vol.In(choices),
                vol.Required(
                    CONF_COUNTDOWN_DP,
                    default=self._mapping_default(
                        CONF_COUNTDOWN_DP, self._detected_dp("18", str)
                    ),
                ): vol.In(choices),
                vol.Optional(
                    CONF_COUNTDOWN_VALUES,
                    default=self._mapping_default(
                        CONF_COUNTDOWN_VALUES, DEFAULT_COUNTDOWN_VALUES
                    ),
                ): str,
            }
        )
        return self.async_show_form(
            step_id="mapping",
            data_schema=schema,
            errors=errors,
            description_placeholders={"detected_dps": format_dps(self._dps)},
        )

    def _validate_mapping(self, data: dict[str, Any]) -> dict[str, str]:
        """Validate mappings that will be used for writes."""
        errors: dict[str, str] = {}
        power_value = self._dps.get(str(data[CONF_POWER_DP]))
        if not isinstance(power_value, bool):
            errors[CONF_POWER_DP] = "power_not_boolean"

        speed_dp = data.get(CONF_SPEED_DP)
        if speed_dp != NOT_CONFIGURED:
            speed_values = parse_csv_values(data.get(CONF_SPEED_VALUES, ""))
            if len(speed_values) < 2:
                errors[CONF_SPEED_VALUES] = "speed_values_invalid"

        countdown_dp = data.get(CONF_COUNTDOWN_DP)
        if countdown_dp != NOT_CONFIGURED:
            countdown_values = parse_csv_values(
                data.get(CONF_COUNTDOWN_VALUES, "")
            )
            if len(countdown_values) < 2:
                errors[CONF_COUNTDOWN_VALUES] = "countdown_values_invalid"

        for key in (
            CONF_IONIZER_DP,
            CONF_CHILD_LOCK_DP,
            CONF_DISPLAY_DP,
            CONF_FILTER_RESET_DP,
        ):
            dp_id = data.get(key)
            if dp_id != NOT_CONFIGURED and not isinstance(
                self._dps.get(str(dp_id)), bool
            ):
                errors[key] = "switch_not_boolean"

        return errors

    def _detected_dp(self, dp_id: str, expected_type: type) -> str:
        """Return a known PureFlow15 Pro DP when its type matches."""
        value = self._dps.get(dp_id)
        if expected_type is int:
            matches = isinstance(value, int) and not isinstance(value, bool)
        else:
            matches = isinstance(value, expected_type)
        return dp_id if matches else NOT_CONFIGURED

    def _guess_power_dp(self) -> str:
        """Choose a conservative default for the required power datapoint."""
        if isinstance(self._dps.get("1"), bool):
            return "1"
        return next(
            (
                dp_id
                for dp_id, value in self._sorted_dps()
                if isinstance(value, bool)
            ),
            next(iter(self._dps)),
        )

    def _mapping_default(
        self, key: str, fallback: Any = NOT_CONFIGURED
    ) -> Any:
        """Return a valid default for new or existing mapping data."""
        value = self._mapping_defaults.get(key, fallback)
        if value is None:
            return NOT_CONFIGURED
        if key in (CONF_POWER_DP, *OPTIONAL_DP_KEYS):
            value = str(value)
            if value not in self._dps:
                return fallback
        return value

    def _sorted_dps(self) -> list[tuple[str, Any]]:
        """Return datapoints in numeric order where possible."""
        def sort_key(item: tuple[str, Any]) -> tuple[int, int | str]:
            return (
                (0, int(item[0]))
                if item[0].isdigit()
                else (1, item[0])
            )

        return sorted(self._dps.items(), key=sort_key)
