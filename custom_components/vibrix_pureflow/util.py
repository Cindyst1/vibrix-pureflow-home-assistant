"""Value helpers for the Vibrix PureFlow integration."""

from __future__ import annotations

import json
from typing import Any


def parse_scalar(value: str) -> Any:
    """Convert a user-entered scalar while preserving ordinary strings."""
    stripped = value.strip()
    if not stripped:
        return ""

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped

    if isinstance(parsed, (str, int, float, bool)) or parsed is None:
        return parsed
    return stripped


def parse_csv_values(value: str) -> list[Any]:
    """Parse comma-separated Tuya values in their original scalar types."""
    return [
        parse_scalar(item)
        for item in value.split(",")
        if item.strip()
    ]


def format_dps(dps: dict[str, Any]) -> str:
    """Format detected datapoints for the config flow."""
    if not dps:
        return "Geen datapoints ontvangen."

    def sort_key(item: tuple[str, Any]) -> tuple[int, int | str]:
        dp_id = item[0]
        return (0, int(dp_id)) if dp_id.isdigit() else (1, dp_id)

    return "\n".join(
        f"- DP `{dp_id}` = `{value!r}` ({type(value).__name__})"
        for dp_id, value in sorted(dps.items(), key=sort_key)
    )
