"""Sensors for Honeygain API datasets."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSOR_NAMES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Honeygain dataset sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        HoneygainDataSensor(coordinator, entry, key, name)
        for key, name in SENSOR_NAMES.items()
    ]
    obsolete_prefixes = tuple(
        f"{entry.entry_id}_{key}_" for key in SENSOR_NAMES
    )
    registry = er.async_get(hass)
    for registered_entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if (
            registered_entity.domain == "sensor"
            and registered_entity.unique_id.startswith(obsolete_prefixes)
        ):
            registry.async_remove(registered_entity.entity_id)
    async_add_entities(entities)


def _summary_metrics(data: Any) -> list[tuple[str, int | float]]:
    """Return a short list of likely financial or usage metrics."""
    totals: dict[tuple[str, ...], int | float] = {}
    ignored_parts = {
        "date",
        "time",
        "timestamp",
        "id",
        "uuid",
        "user",
        "status",
        "type",
        "name",
        "email",
        "address",
        "wallet",
        "hash",
        "token",
    }
    metric_terms = (
        "balance",
        "earning",
        "credit",
        "amount",
        "revenue",
        "winning",
        "traffic",
        "bytes",
        "shared",
    )

    def collect(value: Any, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                collect(child, (*path, str(key).casefold().replace("-", "_")))
        elif isinstance(value, list):
            for child in value:
                collect(child, path)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            metric_path = tuple(
                part for part in path if part not in {"data", "result", "response", "items"}
            )
            if not metric_path or any(
                part in ignored_parts or part.endswith("_id") for part in metric_path
            ):
                return
            if any(term in "_".join(metric_path) for term in metric_terms):
                totals[metric_path] = totals.get(metric_path, 0) + value

    collect(data)

    def score(path: tuple[str, ...]) -> int:
        label = "_".join(path)
        if "balance" in label:
            return 100
        if "total" in label and ("earning" in label or "credit" in label):
            return 95
        if "earning" in label:
            return 90
        if "credit" in label:
            return 85
        if "amount" in label or "revenue" in label:
            return 80
        if "winning" in label:
            return 75
        return 50

    ranked = sorted(totals.items(), key=lambda item: (-score(item[0]), item[0]))
    return [
        (" ".join(part.replace("_", " ") for part in path), value)
        for path, value in ranked[:4]
    ]


def _count_records(data: Any) -> int:
    """Count records in a list response, including nested API envelopes."""
    count = _find_list_length(data)
    if count is not None:
        return count
    return len(data) if isinstance(data, dict) else 0


def _find_list_length(data: Any) -> int | None:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for child in data.values():
            count = _find_list_length(child)
            if count is not None:
                return count
    return None


def _find_scalar(data: Any, names: set[str]) -> str | int | float | bool | None:
    """Find the first scalar matching one of the requested API field names."""
    if isinstance(data, dict):
        for key, value in data.items():
            normalized_key = str(key).casefold().replace("-", "_")
            if normalized_key in names and isinstance(value, (str, int, float, bool)):
                return value
            found = _find_scalar(value, names)
            if found is not None:
                return found
    elif isinstance(data, list):
        for value in data:
            found = _find_scalar(value, names)
            if found is not None:
                return found
    return None


class HoneygainDataSensor(CoordinatorEntity, SensorEntity):
    """Expose one complete Honeygain API response as a sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, Any]],
        entry: ConfigEntry,
        key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Honeygain",
            manufacturer="Honeygain",
        )

    @property
    def native_value(self) -> str | int | float | None:
        """Return a compact summary instead of an availability placeholder."""
        data = self.coordinator.data[self._key]
        metrics = _summary_metrics(data)
        if metrics:
            return metrics[0][1]
        if self._key in {"devices", "payouts", "notifications"}:
            return _count_records(data)
        if self._key == "account":
            account_name = _find_scalar(data, {"username", "display_name", "nickname"})
            return str(account_name) if account_name is not None else "connected"
        if self._key == "jumptask_wallet":
            enabled = _find_scalar(data, {"jt_toggle", "enabled", "is_enabled"})
            if isinstance(enabled, bool):
                return "configured" if enabled else "not configured"
            return "configured" if data else "not configured"
        if self._key == "honeypot":
            status = _find_scalar(data, {"status", "opened", "is_opened", "is_active"})
            if isinstance(status, bool):
                return "open" if status else "closed"
            if isinstance(status, (str, int, float)):
                return status
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the raw response and a limited set of useful metrics."""
        data = self.coordinator.data[self._key]
        attributes: dict[str, Any] = {"data": data}
        if metrics := _summary_metrics(data):
            attributes["summary"] = dict(metrics)
        return attributes
