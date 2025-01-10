"""Models used by Nexxtmove."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


class NexxtmoveConfigEntryData(TypedDict):
    """Config entry for the Nexxtmove integration."""

    username: str | None
    password: str | None


@dataclass
class NexxtmoveEnvironment:
    """Class to describe a Nexxtmove environment."""

    api_endpoint: str
    api_key: str
    x_app_platform: str


@dataclass
class NexxtmoveItem:
    """Nexxtmove item model."""

    name: str = ""
    key: str = ""
    type: str = ""
    sensor_type: str = ""
    state: str = ""
    device_key: str = ""
    device_name: str = ""
    device_model: str = ""
    data: dict = field(default_factory=dict)
    extra_attributes: dict = field(default_factory=dict)
    native_unit_of_measurement: str = None
