import asyncio
import logging
from typing import Awaitable, Callable, Set, TypeAlias

from aiohttp import web
from pydantic import ValidationError

from .models import SensorData

logger = logging.getLogger(__name__)

Callback: TypeAlias = Callable[[SensorData], None]
AsyncCallback: TypeAlias = Callable[[SensorData], Awaitable[None]]


class SensorAPI(object):
    def __init__(self) -> None:
        self.callbacks: Set[Callback] = set()
        self.async_callbacks: Set[AsyncCallback] = set()
        self.app = web.Application()
        self.app.add_routes(
            [web.post("/sensors/airgradient:{sensor_id:[a-f0-9]{12}}/measures", self.process_sensor_reading)]
        )
        self.runner = web.AppRunner(self.app)

    def register_callback(self, f: Callback) -> None:
        """Register a callback."""
        self.callbacks.add(f)

    def register_async_callback(self, f: AsyncCallback) -> None:
        """Register an async callback."""
        self.async_callbacks.add(f)

    def unregister_callback(self, f: Callback) -> None:
        """Unregister a callback."""
        self.callbacks.discard(f)

    def unregister_async_callback(self, f: AsyncCallback) -> None:
        """Unregister an async callback."""
        self.async_callbacks.discard(f)

    def serve(self, host: str = "0.0.0.0", port: int = 8088) -> None:
        """Serve the HTTP endpoint."""
        web.run_app(self.app, host=host, port=port)

    async def async_serve(self, host: str = "0.0.0.0", port: int = 8088) -> None:
        """Serve the HTTP endpoint async."""
        await self.runner.setup()
        site = web.TCPSite(self.runner, host, port)
        await site.start()

    async def async_teardown(self) -> None:
        """Stop serving the endpoint."""
        await self.runner.cleanup()

    async def process_sensor_reading(self, request: web.Request) -> web.Response:
        """Process readings posted by the sensor."""
        sensor_id = request.match_info["sensor_id"]

        try:
            readings = await request.json()
            sensor_data = SensorData(id=sensor_id, readings=readings, ip=request.remote)
            logger.info("Data received from %s", sensor_id)
        except ValidationError:
            logger.error("Bad request from %s: %s", sensor_id, await request.text())
            return web.Response(status=400)

        # Call the callbacks upon receiving sensor data
        if self.async_callbacks:
            await asyncio.gather(*(cb(sensor_data) for cb in self.async_callbacks))

        for cb in self.callbacks:
            cb(sensor_data)

        return web.Response()
