# Roadmap

## Phase 1: Read-only integration

- Create a standard Home Assistant custom integration repo.
- Reverse engineer enough of the official API to authenticate and read fresh air status.
- Add UI setup with connection validation.
- Discover fresh air devices from the cloud account.
- Expose useful read-only entities:
  - temperatures
  - humidity
  - CO2
  - PM2.5
  - realtime air volume
  - current and target frequency
  - online, running, and fault state
- Add unit tests for API signing and payload parsing.
- Document API notes and known limitations.

## Phase 2: Safe control

- Implement client methods for `SetFreshAir`.
- Add service actions:
  - `broadair.turn_on`
  - `broadair.turn_off`
  - `broadair.set_frequency`
  - `broadair.refresh_realtime`
- Verify command effects against actual device state.
- Add switch/number entities after service-level behavior is proven.
- Add cooldowns and command result refreshes.

## Phase 3: Polish and distribution

- Add HACS metadata and release packaging.
- Add diagnostics with sensitive fields redacted.
- Add reauth flow for expired credentials.
- Add translations for entity names and config errors.
- Expand tests with Home Assistant config flow coverage.
