# Changelog

## 0.2.2 - 2026-05-15

- Resolve target frequency ranges per device from options, API status fields,
  known model capabilities, or a default fallback.
- Add options for manual frequency range overrides when the cloud API does not
  expose min/max metadata.

## 0.2.1 - 2026-05-15

- Reauthenticate and retry once when the BROAD AIR cloud invalidates a session
  token.
- Remove the realtime refresh button; polling and post-command refreshes now
  keep state current automatically.
- Serialize rapid control commands instead of raising a cooldown error.
- Resolve target frequency ranges from options, API status fields when
  available, known model capabilities, or a conservative default.
- Filter placeholder temperature values and scale the outdoor PM2.5 field.
- Treat impossible 0% humidity readings as unknown and report online when
  coordinator status polling succeeds.

## 0.2.0 - 2026-05-15

- Add Home Assistant UI controls for power, target frequency, and realtime refresh.
- Add diagnostics with sensitive fields redacted.
- Add reauthentication flow for expired or changed BROAD AIR credentials.
- Document HACS custom repository installation.
- Add CI checks for linting, tests, and Python bytecode compilation.

## 0.1.0

- Add initial BROAD AIR cloud login, device discovery, polling sensors, binary
  sensors, and service-level control actions.
