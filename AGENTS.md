# AGENTS.md

This file is the repository entrypoint for coding agents.

Keep this file short. Treat it as a table of contents, not the full knowledge base.

## Read Order

For most tasks, read in this order:

1. `docs/ai/project-overview.md`
2. `docs/roadmap.md`
3. The smallest relevant design or API note under `docs/`
4. A matching Home Assistant integration file only after the docs refresh

Do not start by reading every custom component file.

## Repository Model

- `AGENTS.md`: thin agent entrypoint
- `.agents/`: repo-local agent assets and reusable prompts
- `docs/ai/`: reusable AI knowledge base
- `docs/roadmap.md`: current project state and next work
- `docs/`: durable design, API, and operations notes
- `custom_components/broadair/`: Home Assistant integration implementation

## Working Rules

- Keep AI-facing docs in English.
- Reply to the human user in their preferred language.
- Prefer small, well-bounded sessions.
- Keep `.agents/` thin; keep durable knowledge in `docs/`.
- Update the most relevant doc when integration behavior or safe verification guidance changes.

## Safety

- Keep credentials, cookies, tokens, and real device identifiers out of committed docs.
- Prefer read-only cloud/API inspection unless the user explicitly asks for control behavior.
- Treat Home Assistant service/entity changes as user-facing behavior and verify with tests or supervised live review.

## Useful Docs

- `docs/README.md`
- `docs/ai/project-overview.md`
- `.agents/README.md`
- `docs/roadmap.md`
- `docs/design.md`
- `docs/api-notes.md`
