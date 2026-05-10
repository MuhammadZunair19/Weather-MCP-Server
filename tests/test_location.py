from __future__ import annotations

import httpx
import pytest

from eu_weather_mcp.config import DEFAULT_SETTINGS
from eu_weather_mcp.errors import UnsupportedLocationError
from eu_weather_mcp.location import parse_coordinates, resolve_fallback_city, resolve_location


def test_parse_coordinates_accepts_eu_values() -> None:
    coordinates = parse_coordinates("52.52,13.40")
    assert coordinates is not None
    assert coordinates.latitude == 52.52
    assert coordinates.longitude == 13.4


def test_parse_coordinates_rejects_non_eu_values() -> None:
    with pytest.raises(UnsupportedLocationError):
        parse_coordinates("40.7128,-74.0060")


def test_resolve_fallback_city_returns_major_eu_city() -> None:
    coordinates = resolve_fallback_city("Berlin")
    assert coordinates is not None
    assert coordinates.country_code == "DE"


def test_resolve_location_uses_geocoder_result() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={"results": [{"name": "Paris", "latitude": 48.8566, "longitude": 2.3522, "country_code": "FR"}]},
        )
    )
    client = httpx.Client(transport=transport)
    result = resolve_location("Paris", client, DEFAULT_SETTINGS)
    assert result.label == "Paris"
    assert result.country_code == "FR"


def test_resolve_location_rejects_non_eu_geocoder_result() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={"results": [{"name": "New York", "latitude": 40.7128, "longitude": -74.0060, "country_code": "US"}]},
        )
    )
    client = httpx.Client(transport=transport)
    with pytest.raises(UnsupportedLocationError):
        resolve_location("New York", client, DEFAULT_SETTINGS)
