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

    def to_dict(self) -> dict:
        """Serialize to dict for storage."""
        return {
            "name": self.name,
            "key": self.key,
            "type": self.type,
            "sensor_type": self.sensor_type,
            "state": self.state,
            "device_key": self.device_key,
            "device_name": self.device_name,
            "device_model": self.device_model,
            "data": self.data,
            "extra_attributes": self.extra_attributes,
            "native_unit_of_measurement": self.native_unit_of_measurement,
        }

    @classmethod
    def from_dict(cls, data: dict) -> NexxtmoveItem:
        """Deserialize from dict."""
        return cls(
            name=data.get("name", ""),
            key=data.get("key", ""),
            type=data.get("type", ""),
            sensor_type=data.get("sensor_type", ""),
            state=data.get("state", ""),
            device_key=data.get("device_key", ""),
            device_name=data.get("device_name", ""),
            device_model=data.get("device_model", ""),
            data=data.get("data", {}),
            extra_attributes=data.get("extra_attributes", {}),
            native_unit_of_measurement=data.get("native_unit_of_measurement"),
        )
