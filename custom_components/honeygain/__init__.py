"""Honeygain Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed
from requests.exceptions import RequestException

from .api import HoneygainApi, HoneygainApiError
from .const import DOMAIN
from .coordinator import HoneygainDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Honeygain from a config entry."""
    try:
        api = await hass.async_add_executor_job(
            HoneygainApi,
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
        )
    except (HoneygainApiError, RequestException, KeyError, ValueError) as err:
        raise ConfigEntryNotReady("Unable to authenticate with Honeygain") from err

    coordinator = HoneygainDataUpdateCoordinator(hass, api)
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        raise ConfigEntryNotReady("Unable to retrieve Honeygain data") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Honeygain config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
