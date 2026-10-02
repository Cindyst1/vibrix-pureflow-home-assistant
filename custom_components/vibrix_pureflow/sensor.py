"""Sensor platform for the Vibrix PureFlow integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfDensity, UnitOfRatio
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VibrixConfigEntry
from .const import (
    CONF_AIR_QUALITY_DP,
    CONF_FILTER_LIFE_DP,
    CONF_PM25_DP,
    CONF_VOC_DP,
)
from .entity import VibrixEntity


@dataclass(frozen=True, kw_only=True)
class VibrixSensorDescription(SensorEntityDescription):
    """Describe a PureFlow sensor."""

    dp_config_key: str


SENSORS = (
    VibrixSensorDescription(
        key="pm25",
        translation_key="pm25",
        dp_config_key=CONF_PM25_DP,
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=UnitOfDensity.MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    VibrixSensorDescription(
        key="voc",
        translation_key="voc",
        dp_config_key=CONF_VOC_DP,
        native_unit_of_measurement=UnitOfRatio.PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:molecule",
    ),
    VibrixSensorDescription(
        key="air_quality",
        translation_key="air_quality",
        dp_config_key=CONF_AIR_QUALITY_DP,
        icon="mdi:air-filter",
    ),
    VibrixSensorDescription(
        key="filter_life",
        translation_key="filter_life",
        dp_config_key=CONF_FILTER_LIFE_DP,
        native_unit_of_measurement=UnitOfRatio.PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VibrixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up configured PureFlow sensors."""
    async_add_entities(
        VibrixPureFlowSensor(entry, description)
        for description in SENSORS
        if entry.data.get(description.dp_config_key)
    )


class VibrixPureFlowSensor(VibrixEntity, SensorEntity):
    """Representation of a PureFlow sensor datapoint."""

    entity_description: VibrixSensorDescription

    def __init__(
        self,
        entry: VibrixConfigEntry,
        description: VibrixSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the raw local datapoint value."""
        return self.dp_value(self.entity_description.dp_config_key)
