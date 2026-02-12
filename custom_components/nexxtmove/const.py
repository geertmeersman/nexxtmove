"""Constants used by Nexxtmove."""

from datetime import timedelta
import json
from pathlib import Path
from typing import Final

from homeassistant.const import Platform

from .models import NexxtmoveEnvironment

PLATFORMS: Final = [Platform.SENSOR, Platform.SWITCH]

ATTRIBUTION: Final = "Data provided by Nexxtmove"

manifestfile = Path(__file__).parent / "manifest.json"
with open(manifestfile) as json_file:
    manifest_data = json.load(json_file)

DOMAIN = manifest_data.get("domain")
NAME = manifest_data.get("name")
VERSION = manifest_data.get("version")
ISSUEURL = manifest_data.get("issue_tracker")
STARTUP = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""


DEFAULT_NEXXTMOVE_ENVIRONMENT = NexxtmoveEnvironment(
    api_endpoint="https://nexxtmove.me/b2bev-app-service/api",
    api_key="41c71886-9afd-43dc-9492-e1e99f082569",
    x_app_platform="android",
)

BASE_HEADERS = {
    "API-KEY": DEFAULT_NEXXTMOVE_ENVIRONMENT.api_key,
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": f"Home Assistant Integration Nexxtmove {VERSION}",
}

UNRECORDED_ATTRIBUTES = {"charges", "events", "dates", "values"}

COORDINATOR_UPDATE_INTERVAL = timedelta(minutes=120)
CONNECTION_RETRY = 1
REQUEST_TIMEOUT = 20
MAX_ROWS = 50
WEBSITE = "https://nexxtmove.me/"

DEFAULT_ICON = "mdi:help-circle-outline"
