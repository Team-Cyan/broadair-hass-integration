# Agent Assets

This folder contains repo-local assets for coding agents.

Keep durable project knowledge in `docs/`. Use `.agents/` only for thin agent-facing assets such as local templates, reusable prompts, or routing helpers that are useful inside this repository.

## Boundaries

- Do not turn `.agents/` into a second knowledge base.
- Do not store secrets, local credentials, run logs, or scratch notes here.
- Keep project state, module knowledge, specs, plans, and operations notes under `docs/`.
