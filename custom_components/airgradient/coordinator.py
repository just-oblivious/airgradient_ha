"""AirGradient Coordinator."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
import logging

from pygradient import SensorAPI, SensorData

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class AirGradientHTTPCoordinator(DataUpdateCoordinator):
    """Coordinator responsible for discovering sensors and updating entities."""

    def __init__(self, hass: HomeAssistant, name: str) -> None:
        """Initialize the HTTP API."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=None,
            update_method=None,
        )

        self._api = SensorAPI()
        self._api.register_async_callback(self.readings_callback)
        self._platform_callbacks: set[Callable[[SensorData], Awaitable[None]]] = set()

        # Record sensor state
        self._sensor_data: dict[str, SensorData] = {}
        self.last_seen: dict[str, datetime] = {}

    def register_callback(self, f: Callable[[SensorData], Awaitable[None]]) -> None:
        """Register a new device callback."""
        self._platform_callbacks.add(f)

    async def begin(self, host: str, port: int) -> None:
        """Start serving the AirGradient device API."""
        await self._api.async_serve(host, port)

    async def teardown(self) -> None:
        """Stop serving the AirGradient device API."""
        await self._api.async_teardown()

    async def readings_callback(self, sensor_data: SensorData) -> None:
        """Inform platforms of updated readings and newly discovered devices."""
        self.last_seen[sensor_data.id] = datetime.now()

        # Inform platforms that a new device was discovered
        if sensor_data.id not in self._sensor_data:
            if self._platform_callbacks:
                await asyncio.gather(*(f(sensor_data) for f in self._platform_callbacks))

        # Inform all entities that new data has arrived
        self._sensor_data[sensor_data.id] = sensor_data
        self.async_set_updated_data(self._sensor_data)
