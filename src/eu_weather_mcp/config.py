from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    forecast_base_url: str = "https://api.open-meteo.com/v1/forecast"
    warnings_base_url: str = "https://api.open-meteo.com/v1/warnings"
    geocoding_base_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    request_timeout_seconds: float = 30.0
    max_retries: int = 3
    backoff_seconds: tuple[float, ...] = (1.0, 2.0, 4.0)


DEFAULT_SETTINGS = Settings()
