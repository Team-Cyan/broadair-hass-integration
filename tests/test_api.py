from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

SPEC = spec_from_file_location(
    "broadair_api",
    Path(__file__).parents[1] / "custom_components" / "broadair" / "api.py",
)
assert SPEC is not None
assert SPEC.loader is not None
api = module_from_spec(SPEC)
sys.modules[SPEC.name] = api
SPEC.loader.exec_module(api)


def test_build_login_signature() -> None:
    assert (
        api.build_login_signature(
            app_token="abc",
            nonce="123456",
            timestamp="1778680000",
        )
        == "30a3fb244e8834b68b9334f5738b4da8"
    )


def test_parse_wrapped_json_object() -> None:
    assert api.parse_wrapped_json('{"TEMP_INDOOR1":"27.4"}') == {"TEMP_INDOOR1": "27.4"}


def test_parse_wrapped_json_list() -> None:
    assert api.parse_wrapped_json('[{"eq_guid":"abc"}]') == [{"eq_guid": "abc"}]


def test_parse_wrapped_json_rejects_bad_json() -> None:
    with pytest.raises(api.BroadAirDataError):
        api.parse_wrapped_json("{bad")


def test_control_operation_constants() -> None:
    assert api.OPERATION_REFRESH_REALTIME == "1"
    assert api.OPERATION_TURN_OFF == "2"
    assert api.OPERATION_TURN_ON == "3"
    assert api.OPERATION_SET_FREQUENCY == "4"
