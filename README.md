# BROAD AIR for Home Assistant

Custom Home Assistant integration for BROAD / Yuanda fresh air systems using the official BROAD AIR cloud API.

The repository includes `custom_components/broadair/icon.png` and `logo.png`
based on the official BROAD AIR app icon for Home Assistant and HACS
presentation.

## Phase 1 status

Implemented:

- UI config flow with username and password.
- Cloud login using the official app signing scheme.
- Device list discovery for fresh air units.
- Periodic status polling.
- Sensors for common fresh air status values such as indoor/outdoor temperature, CO2, PM2.5, frequency, realtime air volume, humidity, and power/heat recovery metrics.
- Binary sensors for online state, running state, and fault presence.
- Explicit services for safe phase 2 control:
  - `broadair.turn_on`
  - `broadair.turn_off`
  - `broadair.set_frequency`
  - `broadair.refresh_realtime`

Not implemented yet:

- Switch and number entities for direct UI control. Services come first so command behavior can be reviewed before optimistic entity controls are added.

## Install

Copy `custom_components/broadair` into your Home Assistant `custom_components` directory, restart Home Assistant, then add the integration from **Settings -> Devices & services -> Add integration -> BROAD AIR**.

The official Android app currently uses `https://broadcleanair.net:8103`. Its TLS certificate does not match that host, so this integration exposes a setup option to disable SSL verification for this API host. Keep the default unless your environment requires stricter handling.

The official API has a narrow login timestamp window. The integration signs login requests with the API server time when available, which avoids false authentication failures on Home Assistant hosts with small clock drift.

## Supported entities

Entity names depend on the device name reported by the cloud. The integration currently exposes:

- Indoor temperature
- Secondary indoor temperature
- Outdoor temperature
- Fresh air temperature
- Exhaust temperature
- Supply air temperature
- Indoor humidity
- Supply air humidity
- CO2 concentration
- Outdoor PM2.5
- Indoor PM2.5
- Realtime air volume
- Running frequency
- Set frequency
- Realtime power
- Realtime heat recovery
- Online
- Fresh air running
- Fault present

## Services

Service calls accept an optional `device_guid`. If your account has exactly one fresh air unit, you can omit it.

```yaml
service: broadair.set_frequency
data:
  frequency: 20
```

The integration waits for the command call to complete, applies a short command cooldown, and refreshes cloud state after each command. It does not assume optimistic success.

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pytest
ruff check .
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).
