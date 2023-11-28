"""Constants used by Nexxtmove."""
from datetime import timedelta
import json
from pathlib import Path
from typing import Final

from homeassistant.const import Platform

from .models import NexxtmoveEnvironment

PLATFORMS: Final = [Platform.SENSOR, Platform.SWITCH]

ATTRIBUTION: Final = "Data provided by Nexxtmove"

DEFAULT_NEXXTMOVE_ENVIRONMENT = NexxtmoveEnvironment(
    api_endpoint="https://nexxtmove.me/b2bev-app-service/api",
    api_key="3f3a7b768b0c689cd2487eaf9849142a",
    x_app_platform="android",
)

BASE_HEADERS = {
    "API-KEY": DEFAULT_NEXXTMOVE_ENVIRONMENT.api_key,
    "X-App-Platform": DEFAULT_NEXXTMOVE_ENVIRONMENT.x_app_platform,
    "Content-Type": "application/json; charset=utf-8",
}

UNRECORDED_ATTRIBUTES = {"charges", "events", "dates", "values"}

GRAPH_START_DATE = "20220101"

COORDINATOR_UPDATE_INTERVAL = timedelta(minutes=5)
CONNECTION_RETRY = 5
REQUEST_TIMEOUT = 20
WEBSITE = "https://nexxtmove.me/"

DEFAULT_ICON = "mdi:help-circle-outline"

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
