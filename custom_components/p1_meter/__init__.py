"""The Dongle Connect P1 Meter integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .coordinator import P1MeterCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type P1MeterConfigEntry = ConfigEntry[P1MeterCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: P1MeterConfigEntry) -> bool:
    """Set up Dongle Connect P1 Meter from a config entry."""
    coordinator = P1MeterCoordinator(hass, entry.data[CONF_HOST])
    await coordinator.async_start()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: P1MeterConfigEntry) -> bool:
    """Unload a config entry."""
    await entry.runtime_data.async_stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
