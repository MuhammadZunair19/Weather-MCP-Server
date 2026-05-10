from __future__ import annotations

import httpx

from eu_weather_mcp.config import DEFAULT_SETTINGS
from eu_weather_mcp.models import Coordinates
from eu_weather_mcp.openmeteo import OpenMeteoClient


def test_get_hourly_forecast_maps_response() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "hourly": {
                    "time": ["2026-05-10T00:00"],
                    "temperature_2m": [18.5],
                    "wind_speed_10m": [12.0],
                    "precipitation_probability": [30],
                }
            },
        )
    )
    client = OpenMeteoClient(httpx.Client(transport=transport), DEFAULT_SETTINGS)
    result = client.get_forecast(Coordinates(52.52, 13.405, "Berlin"), "hourly")
    assert result["type"] == "hourly"
    assert result["periods"][0]["temperature_c"] == 18.5


def test_get_alerts_normalizes_response() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "warnings": [
                    {
                        "severity": "severe",
                        "event": "Heavy Rain",
                        "headline": "Heavy rainfall expected",
                        "description": "Rain likely.",
                        "onset": "2026-05-10T12:00:00Z",
                        "expires": "2026-05-10T18:00:00Z",
                        "sender_name": "DWD",
                    }
                ]
            },
        )
    )
    client = OpenMeteoClient(httpx.Client(transport=transport), DEFAULT_SETTINGS)
    result = client.get_alerts(Coordinates(52.52, 13.405, "Berlin"))
    assert result["alerts"][0]["severity"] == "orange"
    assert result["alerts"][0]["source"] == "DWD"
