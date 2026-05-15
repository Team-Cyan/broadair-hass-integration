# Design

## Goal

Provide a standard Home Assistant custom integration for BROAD / Yuanda fresh air units. Phase 1 is read-only and proves the full path from Home Assistant setup to real cloud state entities. Phase 2 adds safe control once the command semantics are reviewed against real hardware behavior.

## Architecture

The integration has four layers:

- `BroadAirApiClient`: async cloud API wrapper, signing, login, token refresh, device list, and status fetch.
- `BroadAirCoordinator`: Home Assistant `DataUpdateCoordinator` that owns the authenticated client and refreshes all devices on a polling interval.
- Entity platforms: sensors and binary sensors read the latest coordinator data from memory only.
- Config flow: validates credentials before saving an entry, with options for API base URL, SSL verification, and scan interval.

## Data Flow

1. User enters credentials in the UI config flow.
2. The flow logs in and fetches the fresh air device list.
3. Home Assistant stores only the username and password in the config entry.
4. On setup, the coordinator logs in, discovers devices, and polls status.
5. Entities expose parsed values from the coordinator cache.

## Security

The repository contains no account credentials. Runtime credentials live in the Home Assistant config entry storage. The official API host used by the Android app currently has a certificate mismatch; SSL verification is configurable so the user can choose between compatibility and strict validation.

## Error Handling

The client raises typed exceptions for authentication failures, API errors, malformed wrapped JSON, and connection failures. The coordinator marks entities unavailable on update failure. Config flow errors are mapped to user-facing error keys.

## Phase 2 Control Design

Control should be added in small steps:

1. Add explicit service actions for power on, power off, refresh realtime data, and set frequency. Done in phase 2.
2. Add a switch entity only after service actions are verified.
3. Add a number/select entity for frequency or mode only after the command value range is confirmed on real hardware.
4. Add command cooldown and optimistic-state avoidance. Every command should trigger a refresh and trust the cloud response instead of assuming success. Done for service actions.
5. Keep potentially complex automatic tuning commands behind services until their tuple format is fully documented.
