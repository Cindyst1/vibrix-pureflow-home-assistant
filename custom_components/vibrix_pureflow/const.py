"""Constants for the Vibrix PureFlow integration."""

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "vibrix_pureflow"

CONF_PROTOCOL_VERSION: Final = "protocol_version"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_LOCAL_KEY: Final = "local_key"

CONF_POWER_DP: Final = "power_dp"
CONF_SPEED_DP: Final = "speed_dp"
CONF_SPEED_VALUES: Final = "speed_values"
CONF_MODE_DP: Final = "mode_dp"
CONF_MANUAL_MODE_VALUE: Final = "manual_mode_value"
CONF_AUTO_MODE_VALUE: Final = "auto_mode_value"
CONF_SLEEP_MODE_VALUE: Final = "sleep_mode_value"
CONF_PM25_DP: Final = "pm25_dp"
CONF_VOC_DP: Final = "voc_dp"
CONF_AIR_QUALITY_DP: Final = "air_quality_dp"
CONF_FILTER_LIFE_DP: Final = "filter_life_dp"
CONF_FILTER_RESET_DP: Final = "filter_reset_dp"
CONF_IONIZER_DP: Final = "ionizer_dp"
CONF_CHILD_LOCK_DP: Final = "child_lock_dp"
CONF_DISPLAY_DP: Final = "display_dp"
CONF_COUNTDOWN_DP: Final = "countdown_dp"
CONF_COUNTDOWN_VALUES: Final = "countdown_values"

OPTIONAL_DP_KEYS: Final = (
    CONF_SPEED_DP,
    CONF_MODE_DP,
    CONF_PM25_DP,
    CONF_VOC_DP,
    CONF_AIR_QUALITY_DP,
    CONF_FILTER_LIFE_DP,
    CONF_FILTER_RESET_DP,
    CONF_IONIZER_DP,
    CONF_CHILD_LOCK_DP,
    CONF_DISPLAY_DP,
    CONF_COUNTDOWN_DP,
)

PROTOCOL_VERSIONS: Final = ("3.1", "3.2", "3.3", "3.4", "3.5")
DEFAULT_PROTOCOL_VERSION: Final = "3.5"
DEFAULT_SCAN_INTERVAL: Final = 15
DEFAULT_SPEED_VALUES: Final = "low,mid,high,turbo"
DEFAULT_COUNTDOWN_VALUES: Final = "cancel,1h,2h,3h,4h,5h"
NOT_CONFIGURED: Final = "__none__"

PLATFORMS: Final = (
    Platform.BUTTON,
    Platform.FAN,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
)
