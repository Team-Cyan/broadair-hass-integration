# BROAD AIR for Home Assistant

[中文说明](README.md)

Home Assistant custom integration for BROAD / Yuanda fresh air systems.

This integration connects Home Assistant to the official BROAD AIR cloud API,
discovers fresh air units bound to your account, exposes useful sensors, and
adds basic controls for power and target fan frequency.

It has been developed against a real BROAD AIR account and an `SQ260` fresh air
unit. Other models should be treated as community-tested until their capabilities
are confirmed.

## Features

- Home Assistant UI setup flow.
- BROAD AIR cloud login using the official app signing scheme.
- Automatic recovery when the cloud invalidates an existing session token.
- Device discovery for fresh air units.
- Periodic polling with automatic post-command refresh.
- Useful sensors for temperature, CO2, PM2.5, air volume, power, running state,
  and fault state.
- Power switch.
- Target frequency number entity.
- Device-specific frequency range resolver:
  - options override
  - API status fields when available
  - known model table, including `SQ260`
  - safe fallback range
- Diagnostics with sensitive fields redacted.
- HACS custom repository metadata.
- Brand icon and logo under `custom_components/broadair/brand/`.

## Installation

### HACS custom repository

This repository is not yet listed in the default HACS store. Add it as a custom
repository:

1. Open Home Assistant.
2. Open **HACS**.
3. Go to **Integrations**.
4. Open the menu in the top-right corner.
5. Choose **Custom repositories**.
6. Add this repository URL:

   ```text
   https://github.com/Team-Cyan/broadair-hass-integration
   ```

7. Set category to **Integration**.
8. Click **Add**.
9. Search for **BROAD AIR** in HACS and install it.
10. Restart Home Assistant.
11. Go to **Settings -> Devices & services -> Add integration**.
12. Search for **BROAD AIR** and follow the setup flow.

### Manual install

1. Download or clone this repository.
2. Copy this directory:

   ```text
   custom_components/broadair
   ```

3. Into your Home Assistant config directory:

   ```text
   <home-assistant-config>/custom_components/broadair
   ```

4. Restart Home Assistant.
5. Go to **Settings -> Devices & services -> Add integration**.
6. Search for **BROAD AIR** and follow the setup flow.

For Docker-based Home Assistant installations, the config directory is usually
mounted as `/config` inside the container.

## Setup

The setup flow asks for these values:

| Field | Recommended value |
| --- | --- |
| Username or phone number | Your BROAD AIR account phone number or username |
| Password | Your BROAD AIR account password |
| API base URL | Keep `https://broadcleanair.net:8103` |
| Verify SSL certificate | Keep disabled for the default API host |
| Scan interval | Keep `60` seconds unless you need slower polling |
| Minimum frequency override | Keep `0` for automatic detection |
| Maximum frequency override | Keep `0` for automatic detection |

The official Android app currently uses `https://broadcleanair.net:8103`. The
TLS certificate served by that endpoint does not match the hostname, so SSL
verification is disabled by default for compatibility with the official API host.

The login API also has a narrow timestamp window. The integration signs login
requests with the BROAD AIR server time when available, which avoids false
authentication failures on Home Assistant hosts with small clock drift.

## Entities

Entity names depend on the device name returned by the BROAD AIR cloud.

Enabled by default:

- Indoor temperature
- Outdoor temperature
- Fresh air temperature
- Exhaust temperature
- CO2
- Outdoor PM2.5
- Realtime air volume
- Running frequency
- Realtime power
- Online
- Running
- Fault
- Power switch
- Target frequency

Disabled by default, but available for manual opt-in from Home Assistant entity
settings:

- Secondary indoor temperature
- Supply air temperature
- Indoor humidity
- Supply air humidity
- Indoor PM2.5
- Set frequency sensor
- Realtime heat recovery

These disabled entities are model-dependent, diagnostic, duplicated by a control
entity, or placeholder-like on the verified `SQ260` device.

## Services

The integration also registers service actions:

- `broadair.turn_on`
- `broadair.turn_off`
- `broadair.set_frequency`
- `broadair.refresh_realtime`

If your BROAD AIR account has exactly one fresh air unit, `device_guid` can be
omitted.

Example:

```yaml
service: broadair.set_frequency
data:
  frequency: 20
```

Control commands are serialized, so rapid UI changes do not fail with cooldown
errors. After each command, the integration refreshes cloud state immediately
and schedules a second delayed refresh.

## Frequency Range

Target frequency range is resolved per device:

1. Manual options override, when both min and max are set.
2. API status fields, if the cloud exposes a valid range.
3. Known model capabilities, currently including `SQ260` and `SQ260-C1` as
   `20-50 Hz`.
4. Default fallback `0-100 Hz` for unknown models.

If your model has a different safe range, set **Minimum frequency override** and
**Maximum frequency override** in the integration options.

## Troubleshooting

### Invalid authentication

Check username and password first. If credentials are correct, verify that the
Home Assistant host time is accurate. BROAD AIR login signatures are
time-sensitive.

### Token forced logout

The official app and Home Assistant may invalidate each other's session token
when the same account logs in from multiple places. The integration detects this
and automatically logs in again once before retrying the failed request.

### Icon does not appear

The icon and logo are included under:

```text
custom_components/broadair/brand/
```

After installing or updating, restart Home Assistant and hard-refresh the browser
or restart the mobile app to clear frontend cache.

### SSL errors

Keep **Verify SSL certificate** disabled when using the default API host. Enable
it only if you are using an endpoint with a matching certificate.

## Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pytest
ruff check .
python3 -m compileall -q custom_components tests
```

## Release Checklist

1. Update `custom_components/broadair/manifest.json`.
2. Update `pyproject.toml`.
3. Update `CHANGELOG.md`.
4. Run `ruff`, `pytest`, and `compileall`.
5. Tag the release as `vX.Y.Z`.
6. Publish a GitHub release.

## Documentation

- [Roadmap](docs/roadmap.md)
- [Design](docs/design.md)
- [API notes](docs/api-notes.md)
- [Changelog](CHANGELOG.md)
