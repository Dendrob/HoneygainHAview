"""Data update coordinator for Honeygain."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import HoneygainApi
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HoneygainDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch Honeygain data on a shared schedule."""

    def __init__(self, hass: HomeAssistant, api: HoneygainApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Retrieve all API datasets in the executor."""
        try:
            return await self.hass.async_add_executor_job(self.api.fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Honeygain: {err}") from err
