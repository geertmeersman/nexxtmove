"""Nexxtmove switch platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import NexxtmoveDataUpdateCoordinator
from .const import DOMAIN
from .entity import NexxtmoveEntity
from .models import NexxtmoveItem

_LOGGER = logging.getLogger(__name__)


@dataclass
class NexxtmoveSwitchDescription(SwitchEntityDescription):
    """Class to describe a Nexxtmove switch."""

    value_fn: Callable[[Any], StateType] | None = None


SENSOR_DESCRIPTIONS: list[SwitchEntityDescription] = [
    NexxtmoveSwitchDescription(key="charging_device", icon="mdi:ev-station"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Nexxtmove switches."""
    _LOGGER.debug("[switch|async_setup_entry|async_add_entities|start]")
    coordinator: NexxtmoveDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[NexxtmoveSwitch] = []

    SUPPORTED_KEYS = {
        description.key: description for description in SENSOR_DESCRIPTIONS
    }

    # _LOGGER.debug(f"[switch|async_setup_entry|async_add_entities|SUPPORTED_KEYS] {SUPPORTED_KEYS}")

    if coordinator.data is not None:
        for item in coordinator.data:
            item = coordinator.data[item]
            if item.sensor_type == "switch":
                if description := SUPPORTED_KEYS.get(item.type):
                    switch_description = NexxtmoveSwitchDescription(
                        key=str(item.key),
                        name=item.name,
                        icon=description.icon,
                    )

                    _LOGGER.debug(f"[switch|async_setup_entry|adding] {item.name}")
                    entities.append(
                        NexxtmoveSwitch(
                            coordinator=coordinator,
                            description=switch_description,
                            item=item,
                        )
                    )
                else:
                    _LOGGER.debug(
                        f"[switch|async_setup_entry|no support type found] {item.name}, type: {item.type}, keys: {SUPPORTED_KEYS.get(item.type)}",
                        True,
                    )

        if len(entities):
            async_add_entities(entities)


class NexxtmoveSwitch(NexxtmoveEntity, SwitchEntity):
    """Representation of a Nexxtmove switch."""

    entity_description: NexxtmoveSwitchDescription

    def __init__(
        self,
        coordinator: NexxtmoveDataUpdateCoordinator,
        description: EntityDescription,
        item: NexxtmoveItem,
    ) -> None:
        """Set entity ID."""
        super().__init__(coordinator, description, item)
        self.entity_id = f"switch.{DOMAIN}_{self.item.key}"

    @property
    def native_value(self) -> str:
        """Return the status of the switch."""
        state = self.item.state

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(state)

        return state

    @property
    def extra_state_attributes(self):
        """Return attributes for switch."""
        if not self.coordinator.data:
            return {}
        attributes = {
            "last_nexxtmove_sync": self.last_synced,
        }
        if len(self.item.extra_attributes) > 0:
            for attr in self.item.extra_attributes:
                attributes[attr] = self.item.extra_attributes[attr]
        return attributes

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        state = self.item.state

        return state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        _LOGGER.debug(f"Turning {self.item.name} on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        _LOGGER.debug(f"Turning {self.item.name} off")
