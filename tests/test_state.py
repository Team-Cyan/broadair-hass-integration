from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SPEC = spec_from_file_location(
    "broadair_state",
    Path(__file__).parents[1] / "custom_components" / "broadair" / "state.py",
)
assert SPEC is not None
assert SPEC.loader is not None
state = module_from_spec(SPEC)
sys.modules[SPEC.name] = state
SPEC.loader.exec_module(state)


def test_merge_status_snapshot_preserves_fields_missing_from_realtime_update() -> None:
    assert state.merge_status_snapshot(
        {"TEMP_INDOOR1": "27.5", "CO2_CONCENTRATION": "450"},
        {"RT_VOLUME": "130", "POWER_USED_RT": "0.03"},
    ) == {
        "TEMP_INDOOR1": "27.5",
        "CO2_CONCENTRATION": "450",
        "RT_VOLUME": "130",
        "POWER_USED_RT": "0.03",
    }


def test_merge_status_snapshot_replaces_fields_present_in_realtime_update() -> None:
    assert state.merge_status_snapshot(
        {"RT_VOLUME": "0", "POWER_USED_RT": "0"},
        {"RT_VOLUME": "130"},
    ) == {"RT_VOLUME": "130", "POWER_USED_RT": "0"}
