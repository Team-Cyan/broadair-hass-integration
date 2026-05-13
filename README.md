# BROAD AIR for Home Assistant

Custom Home Assistant integration for BROAD / Yuanda fresh air systems using the official BROAD AIR cloud API.

## Phase 1 status

Implemented:

- UI config flow with username and password.
- Cloud login using the official app signing scheme.
- Device list discovery for fresh air units.
- Periodic status polling.
- Sensors for common fresh air status values such as indoor/outdoor temperature, CO2, PM2.5, frequency, realtime air volume, humidity, and power/heat recovery metrics.
- Binary sensors for online state, running state, and fault presence.

Not implemented yet:

- Device control entities or services. The official app exposes power and frequency commands, but those are intentionally deferred to phase 2.

## Install

Copy `custom_components/broadair` into your Home Assistant `custom_components` directory, restart Home Assistant, then add the integration from **Settings -> Devices & services -> Add integration -> BROAD AIR**.

The official Android app currently uses `https://broadcleanair.net:8103`. Its TLS certificate does not match that host, so this integration exposes a setup option to disable SSL verification for this API host. Keep the default unless your environment requires stricter handling.

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
