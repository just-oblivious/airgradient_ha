"""AirGradient HTTP Sensor integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .coordinator import AirGradientHTTPCoordinator

DOMAIN = "airgradient"

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the AirGradient coordinator."""

    ag_coordinator = AirGradientHTTPCoordinator(hass, DOMAIN)
    await ag_coordinator.begin("0.0.0.0", entry.data[CONF_PORT])

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = ag_coordinator

    # Setup the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Tear down the AirGradient coordinator."""

    ag_coordinator = hass.data[DOMAIN][entry.entry_id]
    await ag_coordinator.teardown()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
