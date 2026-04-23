"""Base Nexxtmove entity."""

from __future__ import annotations

import logging

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NexxtmoveDataUpdateCoordinator
from .const import ATTRIBUTION, DOMAIN, NAME, UNRECORDED_ATTRIBUTES, VERSION, WEBSITE
from .models import NexxtmoveItem

_LOGGER = logging.getLogger(__name__)


class NexxtmoveEntity(CoordinatorEntity[NexxtmoveDataUpdateCoordinator]):
    """Base Nexxtmove entity."""

    _attr_attribution = ATTRIBUTION
    _unrecorded_attributes = frozenset(UNRECORDED_ATTRIBUTES)

    def __init__(
        self,
        coordinator: NexxtmoveDataUpdateCoordinator,
        description: EntityDescription,
        item: NexxtmoveItem,
    ) -> None:
        """Initialize Nexxtmove entity."""
        super().__init__(coordinator)

        self.entity_description = description
        self._key = item.key
        self.client = coordinator.client

        # Device info (static, based on initial item)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(item.device_key))},
            name=f"{NAME} {item.device_name}",
            manufacturer=NAME,
            configuration_url=WEBSITE,
            entry_type=DeviceEntryType.SERVICE,
            model=item.device_model,
            sw_version=VERSION,
        )

        self._attr_unique_id = f"{DOMAIN}_{item.key}"
        self._attr_name = f"{item.name}".capitalize()

        _LOGGER.debug(f"[init] {self._key}")

    # ------------------------
    # Dynamic data access
    # ------------------------
    @property
    def item(self) -> NexxtmoveItem | None:
        """Return current item from coordinator."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._key)

    # ------------------------
    # Availability
    # ------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.item is not None

    # ------------------------
    # Common attributes
    # ------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Return common extra attributes."""
        item = self.item
        if item is None:
            return {}

        attributes = {
            "last_synced": getattr(self.coordinator, "last_success_time", None),
        }

        if item.extra_attributes:
            attributes.update(item.extra_attributes)

        return attributes

    # ------------------------
    # Manual update (not used)
    # ------------------------
    async def async_update(self) -> None:
        """Update the entity (unused, handled by coordinator)."""
        return
