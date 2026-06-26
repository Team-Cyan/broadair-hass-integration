"""State helpers for BROAD AIR coordinator data."""

from __future__ import annotations

from typing import Any


def merge_status_snapshot(
    current: dict[str, Any] | None,
    update: dict[str, Any],
) -> dict[str, Any]:
    """Merge a partial realtime status update into the current status snapshot."""

    merged = dict(current or {})
    merged.update(update)
    return merged
