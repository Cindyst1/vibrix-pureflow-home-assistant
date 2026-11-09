# Vibrix PureFlow for Home Assistant

[English](README.md) | [Nederlands](README_NL.md)

An unofficial Home Assistant custom integration for controlling a Vibrix PureFlow15 air purifier directly over the local network.

After the local key has been obtained, status updates and commands are handled locally without using the Tuya cloud. The purifier must remain reachable from Home Assistant on the same LAN.

> [!IMPORTANT]
> The PureFlow15 is a Tuya OEM device. With the original firmware, initial activation and retrieval of the local key normally require Tuya once. After setup, you can block the purifier's internet access while keeping local network traffic available.

## Features

- Local control through Home Assistant using the Tuya LAN protocol.
- Power control and fan presets: `low`, `mid`, `high`, and `turbo`.
- Automatic and sleep modes.
- PM2.5, VOC, air-quality, and remaining filter-life sensors when supported by the device.
- Ionizer, child-lock, and display switches.
- One-to-five-hour shutdown timer.
- Filter-life reset button.
- Full configuration through the Home Assistant user interface.
- Diagnostics with sensitive values such as the IP address, device ID, and local key redacted.

## Requirements

- Home Assistant 2026.7 or newer.
- A Vibrix PureFlow15 connected to the same local network as Home Assistant.
- A fixed or DHCP-reserved IP address for the purifier.
- The Tuya device ID.
- The 16-character local key.
- Tuya protocol version 3.1 through 3.5.

## Obtaining the device details

TinyTuya documents the current process for retrieving local keys through the Tuya IoT Platform: [TinyTuya setup wizard](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys).

Install TinyTuya and run its scanner and wizard:

```powershell
python -m pip install tinytuya==1.20.0
python -m tinytuya scan
python -m tinytuya wizard
```

The scan reports the purifier's IP address, device ID, and protocol version. The wizard creates `devices.json`, which contains the local key.

If the wizard returns `CERTIFICATE_VERIFY_FAILED` on Windows, install support for the Windows certificate store and retry:

```powershell
python -m pip install pip-system-certs
python -m tinytuya wizard
```

> [!WARNING]
> Never publish `devices.json`, `tinytuya.json`, or `tuya-raw.json`. These files can contain account credentials and device keys. They are excluded by this repository's `.gitignore`.

## Installation

### HACS custom repository

1. Open **HACS** in Home Assistant.
2. Open the menu in the top-right corner and select **Custom repositories**.
3. Add `https://github.com/Cindyst1/vibrix-pureflow-home-assistant`.
4. Select **Integration** as the repository type.
5. Open **Vibrix PureFlow** in HACS and select **Download**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration**.
8. Search for **Vibrix PureFlow**.

### Manual installation

1. Copy `custom_components/vibrix_pureflow` to `/config/custom_components/vibrix_pureflow` on Home Assistant.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **Vibrix PureFlow**.

## Configuration

During setup, enter:

- A name for the purifier.
- Its fixed IP address.
- The Tuya device ID.
- The 16-character local key.
- The detected Tuya protocol version.

Fully close the Tuya or Smart Life app before testing. Some devices accept only one active local connection at a time.

The integration reads the available datapoints and then asks you to map the supported functions. Only select datapoints whose purpose you know.

## Tested PureFlow15 Pro datapoints

The tested PureFlow15 Pro using protocol 3.5 reports the following datapoints:

| DP | Function | Values |
| --- | --- | --- |
| 1 | Power | `true`, `false` |
| 2 | PM2.5 | 0–999 µg/m³ |
| 3 | Mode/speed | `auto`, `sleep`, `low`, `mid`, `high`, `turbo` |
| 5 | Filter life | 0–100% |
| 6 | Ionizer | `true`, `false` |
| 7 | Child lock | `true`, `false` |
| 8 | Display | `true`, `false` |
| 11 | Filter reset | Pulse to `true` |
| 18 | Shutdown timer | `cancel`, `1h`, `2h`, `3h`, `4h`, `5h` |

This profile is filled automatically when these datapoints are detected. Datapoint numbers and values may differ between hardware or firmware versions.

## Identifying unknown datapoints

Use `tools/probe.py` to compare datapoint changes while operating one function at a time on the purifier:

```powershell
python tools/probe.py --ip 192.168.1.50 --id YOUR_DEVICE_ID --version 3.5
```

After running the TinyTuya wizard, the probe can securely read the key from `devices.json` without printing it:

```powershell
python tools/probe.py --device-file devices.json --name PureFlow15Pro
```

Record the initial state, change exactly one function on the physical control panel, and press Enter. The probe displays only the datapoints that changed.

Do not map unknown switch datapoints. An incorrect sensor mapping produces confusing readings, while an incorrect switch mapping may operate a different device function.

## Local-only operation

Once local control works reliably, you can block internet access for the purifier in your router. Keep traffic between Home Assistant and the purifier allowed on the local network, including TCP port 6668.

Reserve the purifier's IP address in your router so the integration can always find it. After a factory reset or re-pairing, the local key may change. Use **Reconfigure** on the integration to enter the new connection details.

## Troubleshooting

- **Cannot connect:** verify the IP address, device ID, local key, and protocol version.
- **Device becomes unavailable:** close the Tuya/Smart Life app and check that Home Assistant can reach the purifier on the LAN.
- **Connection stops after an IP change:** create a DHCP reservation and reconfigure the integration with the current address.
- **Authentication fails after re-pairing:** retrieve the new local key and reconfigure the integration.
- **A function operates incorrectly:** verify its datapoint using `tools/probe.py` and update the mapping.

## Tuya limitation

Running the original firmware without ever using a Tuya app or account is generally not possible. The device must first be activated, and its local key is required for encrypted LAN communication.

The only fully Tuya-free route would be compatible alternative firmware for the exact Wi-Fi module and circuit board revision. This requires hardware investigation and may damage the device or void its warranty.

## Support

Found a problem or have a different PureFlow datapoint profile? [Open an issue](https://github.com/Cindyst1/vibrix-pureflow-home-assistant/issues) and include the Home Assistant version, integration version, protocol version, and redacted diagnostics. Never include your local key.
