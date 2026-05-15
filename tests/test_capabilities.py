from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SPEC = spec_from_file_location(
    "broadair_capabilities",
    Path(__file__).parents[1]
    / "custom_components"
    / "broadair"
    / "capabilities.py",
)
assert SPEC is not None
assert SPEC.loader is not None
capabilities = module_from_spec(SPEC)
sys.modules[SPEC.name] = capabilities
SPEC.loader.exec_module(capabilities)


def test_frequency_range_prefers_options_override() -> None:
    frequency_range = capabilities.resolve_frequency_range(
        device={"product_model": "SQ260"},
        status={"FREQUENCY_MIN": "10", "FREQUENCY_MAX": "80"},
        override_min=30,
        override_max=45,
    )

    assert frequency_range == capabilities.FrequencyRange(30, 45, "options")


def test_frequency_range_uses_api_status_when_available() -> None:
    frequency_range = capabilities.resolve_frequency_range(
        device={"product_model": "SQ260"},
        status={"FREQUENCY_MIN": "10", "FREQUENCY_MAX": "80"},
    )

    assert frequency_range == capabilities.FrequencyRange(10, 80, "api")


def test_frequency_range_uses_known_model_table() -> None:
    frequency_range = capabilities.resolve_frequency_range(
        device={"product_model": "SQ260"},
    )

    assert frequency_range == capabilities.FrequencyRange(20, 50, "model:SQ260")


def test_frequency_range_falls_back_for_unknown_model() -> None:
    frequency_range = capabilities.resolve_frequency_range(
        device={"product_model": "unknown"},
    )

    assert frequency_range == capabilities.FrequencyRange(0, 100, "default")


def test_frequency_range_ignores_invalid_override() -> None:
    frequency_range = capabilities.resolve_frequency_range(
        device={"product_model": "SQ260"},
        override_min=70,
        override_max=20,
    )

    assert frequency_range == capabilities.FrequencyRange(20, 50, "model:SQ260")
