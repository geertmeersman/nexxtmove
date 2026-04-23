"""Diagnostics support for Nexxtmove."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


# ------------------------
# Helpers
# ------------------------
def _redact(data: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive fields."""
    if not isinstance(data, dict):
        return data

    redacted = {}
    for key, value in data.items():
        if key.lower() in ("password", "token", "auth", "authorization"):
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = _redact(value)
        else:
            redacted[key] = value

    return redacted


# ------------------------
# Main diagnostics
# ------------------------
async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    if not coordinator:
        return {"error": "No coordinator found"}

    client = coordinator.client

    return {
        "config_entry": {
            "entry_id": entry.entry_id,
            "domain": entry.domain,
            "title": entry.title,
            "data": _redact(dict(entry.data)),
            "options": _redact(dict(entry.options)),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update_success_time": str(coordinator.last_success_time),
            "update_interval": str(coordinator.update_interval),
        },
        "client": {
            "environment": str(getattr(client.environment, "api_endpoint", None)),
            "has_token": client.token is not None,
            "profile": _redact(client.profile),
        },
        "data": _serialize_data(coordinator.data),
    }


# ------------------------
# Data serializer
# ------------------------
def _serialize_data(data: Any) -> Any:
    """Convert coordinator data into JSON-serializable structure."""
    if not data:
        return {}

    result = {}

    for key, item in data.items():
        try:
            result[key] = {
                "name": item.name,
                "type": item.type,
                "state": item.state,
                "device_key": item.device_key,
                "device_name": item.device_name,
                "device_model": item.device_model,
                "extra_attributes": item.extra_attributes,
            }
        except Exception as err:
            result[key] = {"error": str(err)}

    return result
