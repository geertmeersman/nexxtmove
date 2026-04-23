"""Nexxtmove sensor platform."""

from __future__ import annotations

from collections.abc import Callable
import copy
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import NexxtmoveDataUpdateCoordinator
from .const import DOMAIN
from .entity import NexxtmoveEntity
from .models import NexxtmoveItem

_LOGGER = logging.getLogger(__name__)


# ------------------------
# Sensor descriptions
# ------------------------
@dataclass
class NexxtmoveSensorDescription(SensorEntityDescription):
    """Describe a Nexxtmove sensor."""

    value_fn: Callable[[Any], StateType] | None = None


SENSOR_DESCRIPTIONS: list[NexxtmoveSensorDescription] = [
    NexxtmoveSensorDescription(key="company", icon="mdi:account-group"),
    NexxtmoveSensorDescription(key="charging_device_pin", icon="mdi:lock-question"),
    NexxtmoveSensorDescription(key="profile", icon="mdi:face-man"),
    NexxtmoveSensorDescription(
        key="consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:gauge",
        suggested_display_precision=1,
    ),
    NexxtmoveSensorDescription(
        key="consumptionTotal",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
        icon="mdi:gauge",
    ),
    NexxtmoveSensorDescription(
        key="totalEnergyWh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=1,
        icon="mdi:gauge",
    ),
    NexxtmoveSensorDescription(key="counter", icon="mdi:counter"),
    NexxtmoveSensorDescription(key="charging_device", icon="mdi:ev-station"),
    NexxtmoveSensorDescription(key="charging_point", icon="mdi:ev-plug-type1"),
    NexxtmoveSensorDescription(
        key="charging_events", icon="mdi:calendar-multiple-check"
    ),
    NexxtmoveSensorDescription(
        key="price", suggested_display_precision=2, icon="mdi:currency-eur"
    ),
    NexxtmoveSensorDescription(key="charges", icon="mdi:currency-eur"),
    NexxtmoveSensorDescription(
        key="euro",
        icon="mdi:currency-eur",
        suggested_display_precision=2,
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
    ),
    NexxtmoveSensorDescription(
        key="pricekwh",
        icon="mdi:currency-eur",
        suggested_display_precision=2,
        device_class=SensorDeviceClass.MONETARY,
    ),
    NexxtmoveSensorDescription(key="residential_location", icon="mdi:home"),
    NexxtmoveSensorDescription(key="work_location", icon="mdi:office-building"),
]

SUPPORTED_KEYS = {desc.key: desc for desc in SENSOR_DESCRIPTIONS}


# ------------------------
# Setup
# ------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nexxtmove sensors."""
    _LOGGER.debug("[sensor|setup] start")

    coordinator: NexxtmoveDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    known_keys: set[str] = set()

    def _process_coordinator_update():
        """Add new entities when coordinator updates."""
        if not coordinator.data:
            return

        new_entities: list[NexxtmoveSensor] = []

        for item in coordinator.data.values():
            if item.sensor_type != "sensor":
                continue

            if item.key in known_keys:
                continue

            description = SUPPORTED_KEYS.get(item.type)
            if not description:
                _LOGGER.debug(f"[sensor] unsupported type: {item.type} ({item.name})")
                continue

            sensor_description = copy.deepcopy(description)

            if item.native_unit_of_measurement is not None:
                sensor_description.native_unit_of_measurement = (
                    item.native_unit_of_measurement
                )

            _LOGGER.debug(f"[sensor] adding entity: {item.name}")

            new_entities.append(
                NexxtmoveSensor(
                    coordinator=coordinator,
                    description=sensor_description,
                    item=item,
                )
            )

            known_keys.add(item.key)

        if new_entities:
            async_add_entities(new_entities)

    # 🔥 Initial population (if data already exists)
    _process_coordinator_update()

    # 🔥 Listen for future updates
    coordinator.async_add_listener(_process_coordinator_update)


# ------------------------
# Entity
# ------------------------
class NexxtmoveSensor(NexxtmoveEntity, SensorEntity):
    """Representation of a Nexxtmove sensor."""

    entity_description: NexxtmoveSensorDescription

    def __init__(
        self,
        coordinator: NexxtmoveDataUpdateCoordinator,
        description: NexxtmoveSensorDescription,
        item: NexxtmoveItem,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, description, item)
        self.entity_id = f"sensor.{DOMAIN}_{item.key}"

    @property
    def native_value(self):
        """Return sensor value."""
        item = self.item
        if item is None:
            return None

        state = item.state

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(state)

        return state
