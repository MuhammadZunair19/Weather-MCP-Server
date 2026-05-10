from __future__ import annotations

import re

import httpx

from eu_weather_mcp.config import Settings
from eu_weather_mcp.errors import LocationResolutionError, UnsupportedLocationError, WeatherApiError
from eu_weather_mcp.models import Coordinates, FALLBACK_CITIES

COORDINATE_PATTERN = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")
EU_COUNTRY_CODES = {
    "AL", "AD", "AT", "BA", "BE", "BG", "BY", "CH", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
    "FO", "FR", "GB", "GE", "GI", "GR", "HR", "HU", "IE", "IS", "IT", "LI", "LT", "LU", "LV",
    "MC", "MD", "ME", "MK", "MT", "NL", "NO", "PL", "PT", "RO", "RS", "SE", "SI", "SK", "SM",
    "TR", "UA", "VA", "XK",
}


def parse_coordinates(location: str) -> Coordinates | None:
    match = COORDINATE_PATTERN.match(location)
    if not match:
        return None

    latitude = float(match.group(1))
    longitude = float(match.group(2))

    if not _coordinates_look_european(latitude, longitude):
        raise UnsupportedLocationError(f"Location is outside Europe: '{location}'")

    return Coordinates(latitude=latitude, longitude=longitude, label=location.strip())


def resolve_fallback_city(location: str) -> Coordinates | None:
    key = location.strip().casefold()
    city = FALLBACK_CITIES.get(key)
    if city is None:
        return None
    latitude, longitude, country_code = city
    return Coordinates(
        latitude=latitude,
        longitude=longitude,
        label=location.strip(),
        country_code=country_code,
    )


def resolve_location(location: str, client: httpx.Client, settings: Settings) -> Coordinates:
    coordinate_result = parse_coordinates(location)
    if coordinate_result is not None:
        return coordinate_result

    geocoded = geocode_location(location, client, settings)
    if geocoded is not None:
        return geocoded

    fallback = resolve_fallback_city(location)
    if fallback is not None:
        return fallback

    raise LocationResolutionError(f"Location not found in Europe: '{location}'")


def geocode_location(location: str, client: httpx.Client, settings: Settings) -> Coordinates | None:
    try:
        response = client.get(
            settings.geocoding_base_url,
            params={"name": location, "count": 1, "language": "en", "format": "json"},
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        if isinstance(exc, httpx.RequestError):
            return None
        _raise_weather_error(exc)

    payload = response.json()
    results = payload.get("results") or []
    if not results:
        return None

    result = results[0]
    country_code = (result.get("country_code") or "").upper()
    latitude = result.get("latitude")
    longitude = result.get("longitude")
    name = result.get("name") or location.strip()

    if latitude is None or longitude is None:
        return None

    if country_code and country_code not in EU_COUNTRY_CODES:
        raise UnsupportedLocationError(f"Location not found in Europe: '{location}'")

    if not _coordinates_look_european(float(latitude), float(longitude)):
        raise UnsupportedLocationError(f"Location is outside Europe: '{location}'")

    return Coordinates(
        latitude=float(latitude),
        longitude=float(longitude),
        label=name,
        country_code=country_code or None,
    )


def _coordinates_look_european(latitude: float, longitude: float) -> bool:
    return 27.0 <= latitude <= 72.5 and -31.5 <= longitude <= 45.0


def _raise_weather_error(exc: httpx.HTTPError) -> None:
    raise WeatherApiError("Weather provider returned an unexpected geocoding response") from exc
