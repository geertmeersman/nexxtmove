"""Nexxtmove switch platform."""

from __future__ import annotations

from collections.abc import Callable
import copy
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import NexxtmoveDataUpdateCoordinator
from .const import DOMAIN
from .entity import NexxtmoveEntity
from .models import NexxtmoveItem

_LOGGER = logging.getLogger(__name__)


# ------------------------
# Switch descriptions
# ------------------------
@dataclass
class NexxtmoveSwitchDescription(SwitchEntityDescription):
    """Describe a Nexxtmove switch."""

    value_fn: Callable[[Any], StateType] | None = None


SWITCH_DESCRIPTIONS: list[NexxtmoveSwitchDescription] = [
    NexxtmoveSwitchDescription(key="charging_device", icon="mdi:ev-station"),
]

SUPPORTED_KEYS = {desc.key: desc for desc in SWITCH_DESCRIPTIONS}


# ------------------------
# Setup
# ------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nexxtmove switches."""
    _LOGGER.debug("[switch|setup] start")

    coordinator: NexxtmoveDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_keys: set[str] = set()

    def _process_coordinator_update():
        """Add new switch entities when coordinator updates."""
        if not coordinator.data:
            return

        new_entities: list[NexxtmoveSwitch] = []

        for item in coordinator.data.values():
            if item.sensor_type != "switch":
                continue

            if item.key in known_keys:
                continue

            description = SUPPORTED_KEYS.get(item.type)
            if not description:
                _LOGGER.debug(f"[switch] unsupported type: {item.type} ({item.name})")
                continue

            switch_description = copy.deepcopy(description)

            _LOGGER.debug(f"[switch] adding entity: {item.name}")

            new_entities.append(
                NexxtmoveSwitch(
                    coordinator=coordinator,
                    description=switch_description,
                    item=item,
                )
            )

            known_keys.add(item.key)

        if new_entities:
            async_add_entities(new_entities)

    # 🔥 Initial population
    _process_coordinator_update()

    # 🔥 Listen for updates
    coordinator.async_add_listener(_process_coordinator_update)


# ------------------------
# Entity
# ------------------------
class NexxtmoveSwitch(NexxtmoveEntity, SwitchEntity):
    """Representation of a Nexxtmove switch."""

    entity_description: NexxtmoveSwitchDescription

    def __init__(
        self,
        coordinator: NexxtmoveDataUpdateCoordinator,
        description: NexxtmoveSwitchDescription,
        item: NexxtmoveItem,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator, description, item)
        self.entity_id = f"switch.{DOMAIN}_{item.key}"

    @property
    def is_on(self) -> bool | None:
        """Return True if switch is on."""
        item = self.item
        if item is None:
            return None

        state = item.state

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(state)

        return bool(state)

    @property
    def extra_state_attributes(self):
        """Return attributes for switch."""
        item = self.item
        if item is None:
            return {}

        attributes = {
            "last_synced": getattr(self.coordinator, "last_success", None),
        }

        if item.extra_attributes:
            attributes.update(item.extra_attributes)

        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        item = self.item
        if item is None:
            return

        _LOGGER.debug(f"Turning {item.name} on")

        # TODO: call API here
        # await self.hass.async_add_executor_job(self.coordinator.client.turn_on, item)

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        item = self.item
        if item is None:
            return

        _LOGGER.debug(f"Turning {item.name} off")

        # TODO: call API here
        # await self.hass.async_add_executor_job(self.coordinator.client.turn_off, item)

        await self.coordinator.async_request_refresh()
