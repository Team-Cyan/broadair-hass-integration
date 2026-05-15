# Project Overview

## What This Project Is

- A Home Assistant custom integration for BROAD / Yuanda fresh air systems.
- A cloud-API integration that discovers devices, polls state, and exposes fresh-air sensors.
- A cautious control surface with service actions plus direct UI entities for
  power and target frequency.

## What It Is Not

- Not a broad Home Assistant platform repo.
- Not a local-only device protocol implementation.
- Not a place to commit cloud credentials, tokens, cookies, or real private device identifiers.

## Core Runtime Surfaces

- Home Assistant integration: `custom_components/broadair/`
- API client: `custom_components/broadair/api.py`
- Setup/config flow: `custom_components/broadair/config_flow.py`
- Entity platforms: files under `custom_components/broadair/`
- API notes: `docs/api-notes.md`
- Roadmap: `docs/roadmap.md`

## Current Architecture

- The config flow authenticates against the official cloud API.
- The coordinator polls device state and refreshes entities.
- Sensor and binary sensor platforms expose read-only fresh-air state.
- Services provide the safe control layer for turn on, turn off, frequency updates, and explicit refresh.
- Switch and number platforms expose direct Home Assistant UI controls backed by
  the same coordinator command methods.
- The realtime refresh command remains a service-level action; normal operation
  uses polling plus post-command refreshes instead of a manual button entity.

## Documentation Strategy

- root `AGENTS.md` for entry routing
- `.agents/` for repo-local agent assets
- `docs/ai/` for reusable agent knowledge
- `docs/roadmap.md` for current state
- `docs/design.md` and `docs/api-notes.md` for durable integration context
