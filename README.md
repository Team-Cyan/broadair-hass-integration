# BROAD AIR for Home Assistant

Custom Home Assistant integration for BROAD / Yuanda fresh air systems using the official BROAD AIR cloud API.

The repository includes `custom_components/broadair/brand/icon.png` and
`brand/logo.png` based on the official BROAD AIR app icon for Home Assistant
and HACS presentation.

## Status

Implemented:

- UI config flow with username and password.
- Options flow for API URL, SSL verification, and scan interval.
- Reauthentication flow for expired or changed credentials.
- Cloud login using the official app signing scheme.
- Device list discovery for fresh air units.
- Periodic status polling, plus an automatic delayed refresh after commands.
- Sensors for common fresh air status values such as indoor/outdoor temperature, CO2, PM2.5, frequency, realtime air volume, humidity, and power/heat recovery metrics.
- Binary sensors for online state, running state, and fault presence.
- UI controls:
  - power switch
  - target frequency number
- Explicit services:
  - `broadair.turn_on`
  - `broadair.turn_off`
  - `broadair.set_frequency`
  - `broadair.refresh_realtime`
- Diagnostics with sensitive fields redacted.

Not implemented yet:

- Official HACS default repository listing. Install through HACS as a custom repository for now.
- Broad live-device control matrix. Basic login and status reads are verified; control commands should still be reviewed on the actual unit before heavy automation.

## Install

### HACS custom repository

1. Open HACS.
2. Go to **Integrations**.
3. Open the menu and choose **Custom repositories**.
4. Add `https://github.com/Team-Cyan/broadair-hass-integration`.
5. Select category **Integration**.
6. Install **BROAD AIR**.
7. Restart Home Assistant.
8. Add the integration from **Settings -> Devices & services -> Add integration -> BROAD AIR**.

### Manual install

Copy `custom_components/broadair` into your Home Assistant `custom_components`
directory, restart Home Assistant, then add the integration from
**Settings -> Devices & services -> Add integration -> BROAD AIR**.

## Setup values

- **Username or phone number**: your BROAD AIR account, usually the phone number used by the official app.
- **Password**: your BROAD AIR account password.
- **API base URL**: keep the default `https://broadcleanair.net:8103`.
- **Verify SSL certificate**: keep disabled for the default host because the official endpoint currently serves a certificate that does not match `broadcleanair.net`.
- **Scan interval**: default `60` seconds. The allowed range is 30 to 3600 seconds.
- **Minimum/maximum frequency override**: keep both values at `0` for automatic
  detection. The integration checks API status fields first, then known model
  ranges such as `SQ260`, then falls back to a broad default.

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
- Power switch
- Target frequency

Some rarely useful or model-dependent sensors are disabled by default, but can
be manually enabled from Home Assistant entity settings:

- Secondary indoor temperature
- Supply air temperature
- Indoor humidity
- Supply air humidity
- Indoor PM2.5
- Set frequency sensor
- Realtime heat recovery

## Services

Service calls accept an optional `device_guid`. If your account has exactly one fresh air unit, you can omit it.

```yaml
service: broadair.set_frequency
data:
  frequency: 20
```

The integration waits for the command call to complete, serializes rapid
commands instead of failing with a cooldown error, and refreshes cloud state
after each command. It does not assume optimistic success.

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pytest
ruff check .
```

## Release checklist

1. Update `custom_components/broadair/manifest.json`.
2. Update `pyproject.toml`.
3. Move the matching `CHANGELOG.md` section out of `Unreleased`.
4. Run `ruff`, `pytest`, and `compileall`.
5. Tag the release as `vX.Y.Z` and publish a GitHub release.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).
