from __future__ import annotations

import time
from typing import Any

import httpx

from eu_weather_mcp.config import Settings
from eu_weather_mcp.errors import WeatherApiError
from eu_weather_mcp.models import Coordinates


class OpenMeteoClient:
    def __init__(self, client: httpx.Client, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    def get_alerts(self, coordinates: Coordinates) -> dict[str, Any]:
        payload = self._request_json(
            self._settings.warnings_base_url,
            {"latitude": coordinates.latitude, "longitude": coordinates.longitude},
        )
        alerts = payload.get("warnings") or payload.get("alerts") or []
        normalized = []
        for item in alerts:
            normalized.append(
                {
                    "severity": _normalize_severity(item.get("severity") or item.get("level")),
                    "event": item.get("event") or item.get("type") or "Weather alert",
                    "headline": item.get("headline") or item.get("title") or "Active weather alert",
                    "description": item.get("description") or item.get("instruction") or "",
                    "start": item.get("onset") or item.get("start"),
                    "end": item.get("expires") or item.get("end"),
                    "source": item.get("sender_name") or item.get("source") or "Open-Meteo",
                }
            )
        return {"location": coordinates.label, "alerts": normalized}

    def get_forecast(self, coordinates: Coordinates, forecast_type: str) -> dict[str, Any]:
        if forecast_type == "hourly":
            return self._get_hourly_forecast(coordinates)
        if forecast_type == "daily":
            return self._get_daily_forecast(coordinates)
        raise WeatherApiError(f"Unsupported forecast type: '{forecast_type}'")

    def _get_hourly_forecast(self, coordinates: Coordinates) -> dict[str, Any]:
        payload = self._request_json(
            self._settings.forecast_base_url,
            {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude,
                "hourly": "temperature_2m,wind_speed_10m,precipitation_probability",
                "forecast_days": 7,
                "timezone": "auto",
            },
        )
        hourly = payload.get("hourly") or {}
        times = hourly.get("time") or []
        temperatures = hourly.get("temperature_2m") or []
        wind_speeds = hourly.get("wind_speed_10m") or []
        precipitation_probabilities = hourly.get("precipitation_probability") or []
        periods = []
        for index, forecast_time in enumerate(times):
            periods.append(
                {
                    "time": forecast_time,
                    "temperature_c": _value_at(temperatures, index),
                    "wind_speed_kmh": _value_at(wind_speeds, index),
                    "precipitation_probability_percent": _value_at(precipitation_probabilities, index),
                }
            )
        return {"location": coordinates.label, "type": "hourly", "periods": periods}

    def _get_daily_forecast(self, coordinates: Coordinates) -> dict[str, Any]:
        payload = self._request_json(
            self._settings.forecast_base_url,
            {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude,
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "forecast_days": 7,
                "timezone": "auto",
            },
        )
        daily = payload.get("daily") or {}
        dates = daily.get("time") or []
        highs = daily.get("temperature_2m_max") or []
        lows = daily.get("temperature_2m_min") or []
        weather_codes = daily.get("weather_code") or daily.get("weathercode") or []
        periods = []
        for index, forecast_date in enumerate(dates):
            periods.append(
                {
                    "date": forecast_date,
                    "temperature_max_c": _value_at(highs, index),
                    "temperature_min_c": _value_at(lows, index),
                    "weather_code": _value_at(weather_codes, index),
                }
            )
        return {"location": coordinates.label, "type": "daily", "periods": periods}

    def _request_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self._settings.max_retries):
            try:
                response = self._client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                if attempt + 1 >= self._settings.max_retries:
                    break
                time.sleep(self._settings.backoff_seconds[min(attempt, len(self._settings.backoff_seconds) - 1)])

        raise WeatherApiError("Weather provider request failed after retries") from last_error


def _normalize_severity(severity: str | int | None) -> str:
    if severity is None:
        return "unknown"
    if isinstance(severity, int):
        return {1: "yellow", 2: "orange", 3: "red"}.get(severity, str(severity))
    value = str(severity).strip().lower()
    aliases = {"moderate": "yellow", "severe": "orange", "extreme": "red"}
    return aliases.get(value, value)


def _value_at(values: list[Any], index: int) -> Any:
    return values[index] if index < len(values) else None
