"""Constants for the BROAD AIR integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "broadair"

DEFAULT_BASE_URL = "https://broadcleanair.net:8103"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
DEFAULT_VERIFY_SSL = False

CONF_BASE_URL = "base_url"
CONF_FREQUENCY_MAX = "frequency_max"
CONF_FREQUENCY_MIN = "frequency_min"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_VERIFY_SSL = "verify_ssl"

PLATFORMS = ["sensor", "binary_sensor", "switch", "number"]

ATTR_DEVICE_GUID = "device_guid"
ATTR_FREQUENCY = "frequency"

SERVICE_REFRESH_REALTIME = "refresh_realtime"
SERVICE_SET_FREQUENCY = "set_frequency"
SERVICE_TURN_OFF = "turn_off"
SERVICE_TURN_ON = "turn_on"
