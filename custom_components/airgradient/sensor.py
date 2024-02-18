"""AirGradient Sensor platform."""
from __future__ import annotations

from datetime import datetime, timedelta

from .pygradient.models import SensorData

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    EntityCategory,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import AirGradientHTTPCoordinator

SENSORS: dict[str, SensorEntityDescription] = {
    "atmp": SensorEntityDescription(
        key="atmp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        translation_key="atmp"
    ),
    "rhum": SensorEntityDescription(
        key="rhum",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        translation_key="rhum"
    ),
    "rco2": SensorEntityDescription(
        key="rco2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        translation_key="rco2"
    ),
    "tvoc_index": SensorEntityDescription(
        key="tvoc_index",
        device_class=SensorDeviceClass.AQI,
        translation_key="tvoc_index"
    ),
    "nox_index": SensorEntityDescription(
        key="nox_index",
        device_class=SensorDeviceClass.AQI,
        translation_key="nox_index"
    ),
    "wifi": SensorEntityDescription(
        key="wifi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTIC,
        translation_key="wifi"
    ),
    "pm01": SensorEntityDescription(
        key="pm01",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM1,
        translation_key="pm01",
    ),
    "pm02": SensorEntityDescription(
        key="pm02",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        translation_key="pm02",
    ),
    "pm10": SensorEntityDescription(
        key="pm10",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM10,
        translation_key="pm10",
    ),
    "pm003_count": SensorEntityDescription(
        key="pm003_count",
        device_class=SensorDeviceClass.AQI,
        translation_key="pm003_count"
    ),
}


class AirGradientSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an AirGradient Sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AirGradientHTTPCoordinator,
        sensor_data: SensorData,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{sensor_data.id}_{entity_description.key}"
        self._id = sensor_data.id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, sensor_data.id)},
            name=f"AirGradient {sensor_data.id}",
            model="Air Quality Monitor",
            manufacturer="AirGradient",
            serial_number=sensor_data.id
        )

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        if self.coordinator.data and self._id in self.coordinator.data:
            value = getattr(self.coordinator.data[self._id].readings, self.entity_description.key)
            if isinstance(value, (str, int, float)):
                return value
        return None

    @property
    def available(self) -> bool:
        """Return availability based on the last_seen date of the sensor."""
        if last_seen := self.coordinator.last_seen.get(self._id):
            return bool((datetime.now() - last_seen) < timedelta(minutes=5))
        return False


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Register a callback for newly-discovered sensors with the coordinator."""
    ag_coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async def new_sensor_callback(sensor_data: SensorData) -> None:
        """Create entities for sensor readings."""
        entities = []
        for reading, value in sensor_data.readings:
            if value is not None:
                if entity_description := SENSORS.get(reading):
                    entities.append(AirGradientSensorEntity(ag_coordinator, sensor_data, entity_description))
        async_add_entities(entities)

    ag_coordinator.register_callback(new_sensor_callback)
