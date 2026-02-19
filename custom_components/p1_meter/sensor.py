"""Sensor platform for the Dongle Connect P1 Meter integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import P1MeterConfigEntry
from .const import DOMAIN, SENSOR_FIELDS, P1SensorFieldDescriptor
from .coordinator import P1MeterCoordinator

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = tuple(
    SensorEntityDescription(
        key=field.key,
        translation_key=field.translation_key,
        native_unit_of_measurement=field.native_unit_of_measurement,
        device_class=field.device_class,
        state_class=field.state_class,
    )
    for field in SENSOR_FIELDS
)

# Build a lookup from key to field descriptor for availability checks
_FIELD_BY_KEY: dict[str, P1SensorFieldDescriptor] = {f.key: f for f in SENSOR_FIELDS}


async def async_setup_entry(
    hass: Any,
    entry: P1MeterConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up P1 Meter sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        P1MeterSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class P1MeterSensor(CoordinatorEntity[P1MeterCoordinator], SensorEntity):
    """Representation of a P1 Meter sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: P1MeterCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._field = _FIELD_BY_KEY[description.key]
        self._attr_unique_id = f"{coordinator.host}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.serial or self.coordinator.host)},
            name="P1 Meter",
            manufacturer="Dongle Connect",
            model=self.coordinator.model,
            sw_version=self.coordinator.sw_version,
        )

    @property
    def available(self) -> bool:
        """Return True if the sensor value is available."""
        if not self.coordinator.data:
            return False
        return self._field.json_key in self.coordinator.data

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._field.json_key)
