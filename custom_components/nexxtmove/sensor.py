"""Nexxtmove sensor platform."""
from __future__ import annotations

from collections.abc import Callable
import copy
from dataclasses import dataclass
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
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import NexxtmoveDataUpdateCoordinator
from .const import _LOGGER, DOMAIN
from .entity import NexxtmoveEntity
from .models import NexxtmoveItem


@dataclass
class NexxtmoveSensorDescription(SensorEntityDescription):
    """Class to describe a Nexxtmove sensor."""

    value_fn: Callable[[Any], StateType] | None = None


SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
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
    NexxtmoveSensorDescription(key="charging_point", icon="mdi:ev-plug-ccs2"),
    NexxtmoveSensorDescription(
        key="charging_events", icon="mdi:calendar-multiple-check"
    ),
    NexxtmoveSensorDescription(
        key="price", suggested_display_precision=1, icon="mdi:currency-eur"
    ),
    NexxtmoveSensorDescription(key="charges", icon="mdi:currency-eur"),
    NexxtmoveSensorDescription(
        key="euro",
        icon="mdi:currency-eur",
        suggested_display_precision=1,
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
    ),
    NexxtmoveSensorDescription(
        key="pricekwh",
        icon="mdi:currency-eur",
        device_class=SensorDeviceClass.MONETARY,
    ),
    NexxtmoveSensorDescription(key="residential_location", icon="mdi:home"),
    NexxtmoveSensorDescription(key="work_location", icon="mdi:office-building"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Nexxtmove sensors."""
    _LOGGER.debug("[sensor|async_setup_entry|async_add_entities|start]")
    coordinator: NexxtmoveDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[NexxtmoveSensor] = []

    SUPPORTED_KEYS = {
        description.key: description for description in SENSOR_DESCRIPTIONS
    }

    # _LOGGER.debug(f"[sensor|async_setup_entry|async_add_entities|SUPPORTED_KEYS] {SUPPORTED_KEYS}")

    if coordinator.data is not None:
        for item in coordinator.data:
            item = coordinator.data[item]
            if item.sensor_type == "sensor":
                if description := SUPPORTED_KEYS.get(item.type):
                    sensor_description = copy.deepcopy(description)
                    if item.native_unit_of_measurement is not None:
                        sensor_description.native_unit_of_measurement = (
                            item.native_unit_of_measurement
                        )

                    _LOGGER.debug(f"[sensor|async_setup_entry|adding] {item.name}")
                    entities.append(
                        NexxtmoveSensor(
                            coordinator=coordinator,
                            description=sensor_description,
                            item=item,
                        )
                    )
                else:
                    _LOGGER.debug(
                        f"[sensor|async_setup_entry|no support type found] {item.name}, type: {item.type}, keys: {SUPPORTED_KEYS.get(item.type)}",
                        True,
                    )

        if len(entities):
            async_add_entities(entities)


class NexxtmoveSensor(NexxtmoveEntity, SensorEntity):
    """Representation of a Nexxtmove sensor."""

    entity_description: NexxtmoveSensorDescription

    def __init__(
        self,
        coordinator: NexxtmoveDataUpdateCoordinator,
        description: EntityDescription,
        item: NexxtmoveItem,
    ) -> None:
        """Set entity ID."""
        super().__init__(coordinator, description, item)
        self.entity_id = f"sensor.{DOMAIN}_{self.item.key}"

    @property
    def native_value(self) -> str:
        """Return the status of the sensor."""
        state = self.item.state

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(state)

        return state

    @property
    def extra_state_attributes(self):
        """Return attributes for sensor."""
        if not self.coordinator.data:
            return {}
        attributes = {
            "last_nexxtmove_sync": self.last_synced,
        }
        if len(self.item.extra_attributes) > 0:
            for attr in self.item.extra_attributes:
                attributes[attr] = self.item.extra_attributes[attr]
        return attributes
