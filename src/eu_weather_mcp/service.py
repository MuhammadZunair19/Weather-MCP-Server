from __future__ import annotations

import httpx

from eu_weather_mcp.config import DEFAULT_SETTINGS, Settings
from eu_weather_mcp.location import resolve_location
from eu_weather_mcp.openmeteo import OpenMeteoClient


class WeatherService:
    def __init__(self, settings: Settings = DEFAULT_SETTINGS, client: httpx.Client | None = None) -> None:
        self._settings = settings
        self._client = client or httpx.Client(timeout=settings.request_timeout_seconds)
        self._weather_client = OpenMeteoClient(self._client, settings)

    def close(self) -> None:
        self._client.close()

    def get_weather_alerts(self, location: str) -> dict:
        coordinates = resolve_location(location, self._client, self._settings)
        return self._weather_client.get_alerts(coordinates)

    def get_forecast(self, location: str, forecast_type: str) -> dict:
        coordinates = resolve_location(location, self._client, self._settings)
        return self._weather_client.get_forecast(coordinates, forecast_type)
