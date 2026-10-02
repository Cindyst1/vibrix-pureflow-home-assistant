"""Interactively compare local Tuya datapoint snapshots."""

from __future__ import annotations

import argparse
import json
from getpass import getpass
from pathlib import Path
from typing import Any

import tinytuya


def read_status(device: tinytuya.Device) -> dict[str, Any]:
    """Read a normalized datapoint snapshot or exit with a useful error."""
    response = device.status()
    if not isinstance(response, dict) or not isinstance(response.get("dps"), dict):
        raise RuntimeError(f"Ongeldig antwoord: {response!r}")
    return {str(key): value for key, value in response["dps"].items()}


def print_snapshot(snapshot: dict[str, Any]) -> None:
    """Print datapoints in numeric order."""
    for dp_id in sorted(
        snapshot,
        key=lambda value: (0, int(value)) if value.isdigit() else (1, value),
    ):
        value = snapshot[dp_id]
        print(f"DP {dp_id:>3}: {value!r} ({type(value).__name__})")


def load_device(
    path: Path, name: str
) -> tuple[str, str, str, str]:
    """Load one device from a TinyTuya devices file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    devices = data.get("devices", []) if isinstance(data, dict) else data
    matches = [
        device
        for device in devices
        if str(device.get("name", "")).casefold() == name.casefold()
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Verwacht precies één apparaat met naam {name!r}, "
            f"maar vond er {len(matches)}."
        )
    device = matches[0]
    return (
        str(device["ip"]),
        str(device["id"]),
        str(device["key"]),
        str(device.get("version", "3.3")),
    )


def main() -> None:
    """Run the interactive datapoint probe."""
    parser = argparse.ArgumentParser(
        description="Vergelijk datapoints van een Vibrix PureFlow15 via het LAN."
    )
    parser.add_argument("--ip", help="IP-adres van de luchtreiniger")
    parser.add_argument("--id", help="Tuya device-ID")
    parser.add_argument(
        "--version", default="3.3", choices=("3.1", "3.2", "3.3", "3.4", "3.5")
    )
    parser.add_argument(
        "--device-file",
        type=Path,
        help="TinyTuya devices.json; voorkomt dat de lokale sleutel wordt getoond",
    )
    parser.add_argument(
        "--name",
        default="PureFlow15Pro",
        help="Exacte apparaatnaam in devices.json",
    )
    args = parser.parse_args()
    if args.device_file:
        ip_address, device_id, local_key, version = load_device(
            args.device_file, args.name
        )
    else:
        if not args.ip or not args.id:
            parser.error("gebruik --device-file, of geef zowel --ip als --id op")
        ip_address = args.ip
        device_id = args.id
        local_key = getpass("Lokale sleutel (16 tekens): ")
        version = args.version

    device = tinytuya.Device(
        dev_id=device_id,
        address=ip_address,
        local_key=local_key,
        version=float(version),
        connection_timeout=5,
        connection_retry_limit=1,
        connection_retry_delay=1,
    )
    try:
        previous = read_status(device)
        print("\nBeginsituatie:")
        print_snapshot(previous)

        while True:
            answer = input(
                "\nWijzig precies één functie op het apparaat en druk Enter "
                "(of typ q om te stoppen): "
            )
            if answer.strip().lower() == "q":
                break
            current = read_status(device)
            changed = {
                dp_id: value
                for dp_id, value in current.items()
                if previous.get(dp_id) != value
            }
            removed = set(previous) - set(current)
            if not changed and not removed:
                print("Geen gewijzigde datapoints gevonden.")
            else:
                for dp_id, value in changed.items():
                    print(
                        f"DP {dp_id}: {previous.get(dp_id)!r} -> {value!r} "
                        f"({type(value).__name__})"
                    )
                for dp_id in removed:
                    print(f"DP {dp_id}: niet meer gerapporteerd")
            previous = current
    finally:
        device.close()


if __name__ == "__main__":
    main()
