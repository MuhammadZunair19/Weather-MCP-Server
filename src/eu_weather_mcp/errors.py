from __future__ import annotations


class WeatherMcpError(Exception):
    """Base application error."""

    code = -32000

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class LocationResolutionError(WeatherMcpError):
    """Raised when a location cannot be resolved."""


class UnsupportedLocationError(WeatherMcpError):
    """Raised when a location is outside Europe."""


class WeatherApiError(WeatherMcpError):
    """Raised when the weather provider fails."""
