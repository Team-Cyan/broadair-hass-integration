# Roadmap

## Phase 1: Read-only integration

- Create a standard Home Assistant custom integration repo.
- Add thin `AGENTS.md`, `.agents/`, and `docs/` routing for future agent sessions. **Done.**
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

- Implement client methods for `SetFreshAir`. **Done.**
- Add service actions. **Done.**
  - `broadair.turn_on`
  - `broadair.turn_off`
  - `broadair.set_frequency`
  - `broadair.refresh_realtime`
- Verify command effects against actual device state. **Pending supervised live review.**
- Add switch/number/button entities after service-level behavior is proven. **Done.**
- Add cooldowns and command result refreshes. **Done.**

## Phase 3: Polish and distribution

- Add HACS metadata and release packaging. **Done for custom repository install; pending official HACS default listing.**
- Add diagnostics with sensitive fields redacted. **Done.**
- Add reauth flow for expired credentials. **Done.**
- Add translations for entity names and config errors. **Done.**
- Expand tests with Home Assistant config flow coverage.
