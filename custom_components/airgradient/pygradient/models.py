from typing import Dict, List, Optional

from pydantic import BaseModel, StrictFloat, StrictInt, StrictStr, validator


class AG(BaseModel):
    """WiFi RSSI and loop count."""

    wifi: StrictInt
    boot: StrictInt


class PMTH(BaseModel):
    """Particulate matter, temperature, and humidity readings."""

    pm01: StrictInt
    pm02: StrictInt
    pm10: StrictInt
    pm003_count: StrictInt
    atmp: StrictInt | StrictFloat
    rhum: StrictInt | StrictFloat


class SensorReading(AG, PMTH):
    """Common sensor readings."""

    rco2: StrictInt
    tvoc_index: StrictInt
    nox_index: StrictInt

    channels: Optional[List[PMTH]] = None

    @validator("channels", pre=True)
    def init_channels(cls, obj: Dict[str, Dict[str, int | float]]) -> List[PMTH]:
        """Parse individual channels supplied by the Outdoor Monitor with dual PM sensors."""
        return [PMTH.model_validate(obj["1"]), PMTH.model_validate(obj["2"])]


class SensorData(BaseModel):
    """Data from an AirGradient sensor."""

    id: StrictStr
    ip: Optional[StrictStr]
    readings: SensorReading
