"""Client wrapper for the pyHoneygain library."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyHoneygain import HoneyGain

from .const import API_METHODS


class HoneygainApiError(Exception):
    """Raised when Honeygain rejects authentication or API data."""


class HoneygainApi:
    """Authenticated Honeygain API client."""

    def __init__(self, email: str, password: str) -> None:
        self._client = HoneyGain()
        if not self._client.login(email, password):
            raise HoneygainApiError("Honeygain authentication failed")

    def fetch_data(self) -> dict[str, Any]:
        """Fetch all read-only data exposed by pyHoneygain."""
        result: dict[str, Any] = {}
        for key, method_name in API_METHODS.items():
            method: Callable[[], Any] = getattr(self._client, method_name)
            data = method()
            if data is False:
                raise HoneygainApiError(f"Honeygain returned an error for {key}")
            result[key] = data
        return result
