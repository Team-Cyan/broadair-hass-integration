"""Device capability helpers for BROAD AIR."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

DEFAULT_FREQUENCY_RANGE = (0, 100)
MODEL_FREQUENCY_RANGES: dict[str, tuple[int, int]] = {
    "SQ260": (20, 50),
    "SQ260-C1": (20, 50),
}
FREQUENCY_MIN_KEYS = (
    "FREQUENCY_MIN",
    "FREQ_MIN",
    "MIN_FREQUENCY",
    "MIN_FREQ",
)
FREQUENCY_MAX_KEYS = (
    "FREQUENCY_MAX",
    "FREQ_MAX",
    "MAX_FREQUENCY",
    "MAX_FREQ",
)


@dataclass(slots=True, frozen=True)
class FrequencyRange:
    """Resolved target frequency range."""

    minimum: int
    maximum: int
    source: str


def resolve_frequency_range(
    *,
    device: Mapping[str, Any],
    status: Mapping[str, Any] | None = None,
    override_min: int | None = None,
    override_max: int | None = None,
) -> FrequencyRange:
    """Resolve the target frequency range for a device."""

    override = _valid_range(override_min, override_max)
    if override is not None:
        return FrequencyRange(*override, source="options")

    api_range = _range_from_status(status or {})
    if api_range is not None:
        return FrequencyRange(*api_range, source="api")

    model = str(device.get("product_model") or "").strip().upper()
    model_range = MODEL_FREQUENCY_RANGES.get(model)
    if model_range is not None:
        return FrequencyRange(*model_range, source=f"model:{model}")

    return FrequencyRange(*DEFAULT_FREQUENCY_RANGE, source="default")


def _range_from_status(status: Mapping[str, Any]) -> tuple[int, int] | None:
    minimum = _first_int(status, FREQUENCY_MIN_KEYS)
    maximum = _first_int(status, FREQUENCY_MAX_KEYS)
    return _valid_range(minimum, maximum)


def _first_int(status: Mapping[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = status.get(key)
        if value in (None, ""):
            continue
        try:
            return int(float(value))
        except (TypeError, ValueError):
            continue
    return None


def _valid_range(
    minimum: int | None,
    maximum: int | None,
) -> tuple[int, int] | None:
    if minimum is None or maximum is None:
        return None
    if minimum <= 0 and maximum <= 0:
        return None
    if minimum < 0 or maximum <= minimum:
        return None
    return minimum, maximum
