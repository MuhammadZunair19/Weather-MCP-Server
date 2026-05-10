from __future__ import annotations

from typing import Any

import streamlit as st

from eu_weather_mcp.errors import WeatherMcpError
from eu_weather_mcp.service import WeatherService


def main() -> None:
    st.set_page_config(
        page_title="EU Weather UI",
        page_icon="🌦️",
        layout="wide",
    )

    st.title("EU Weather MCP UI")
    st.caption("Explore European weather forecasts and alerts using the same service layer as the MCP server.")

    with st.sidebar:
        st.header("Request")
        location = st.text_input(
            "Location",
            value="Berlin",
            help="Enter a European city like Berlin or coordinates like 52.52,13.40.",
        )
        forecast_type = st.radio(
            "Forecast type",
            options=["hourly", "daily"],
            horizontal=True,
        )
        load_forecast = st.button("Get forecast", type="primary", use_container_width=True)
        load_alerts = st.button("Get alerts", use_container_width=True)

        st.markdown("Examples: `Berlin`, `Paris`, `52.52,13.40`")

    st.markdown(
        """
        <style>
        .stMetric {
            border: 1px solid rgba(120, 120, 120, 0.2);
            border-radius: 16px;
            padding: 0.75rem;
            background: rgba(250, 250, 250, 0.7);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not load_forecast and not load_alerts:
        st.info("Choose a location and load a forecast or active weather alerts.")
        return

    service = WeatherService()
    try:
        if load_forecast:
            forecast = service.get_forecast(location, forecast_type)
            _render_forecast(forecast)
        if load_alerts:
            alerts = service.get_weather_alerts(location)
            _render_alerts(alerts)
    except WeatherMcpError as exc:
        st.error(exc.message)
    finally:
        service.close()


def _render_forecast(forecast: dict[str, Any]) -> None:
    st.subheader(f"{forecast['location']} forecast")
    periods = forecast.get("periods") or []

    if not periods:
        st.warning("No forecast periods were returned.")
        return

    if forecast.get("type") == "hourly":
        _render_hourly_forecast(periods)
        return

    _render_daily_forecast(periods)


def _render_hourly_forecast(periods: list[dict[str, Any]]) -> None:
    preview = periods[:24]
    cols = st.columns(3)
    cols[0].metric("Hours shown", str(len(preview)))
    cols[1].metric("Warmest", _format_temperature(max((p.get("temperature_c") for p in preview), default=None)))
    cols[2].metric(
        "Highest rain chance",
        _format_percent(max((p.get("precipitation_probability_percent") for p in preview), default=None)),
    )

    st.dataframe(
        preview,
        use_container_width=True,
        hide_index=True,
    )

    chart_rows = []
    for period in preview:
        chart_rows.append(
            {
                "time": period.get("time"),
                "temperature_c": period.get("temperature_c"),
                "wind_speed_kmh": period.get("wind_speed_kmh"),
                "precipitation_probability_percent": period.get("precipitation_probability_percent"),
            }
        )

    st.line_chart(chart_rows, x="time", y=["temperature_c", "wind_speed_kmh"])
    st.bar_chart(chart_rows, x="time", y="precipitation_probability_percent")


def _render_daily_forecast(periods: list[dict[str, Any]]) -> None:
    cols = st.columns(3)
    cols[0].metric("Days shown", str(len(periods)))
    cols[1].metric("Warmest high", _format_temperature(max((p.get("temperature_max_c") for p in periods), default=None)))
    cols[2].metric("Coolest low", _format_temperature(min((p.get("temperature_min_c") for p in periods), default=None)))

    st.dataframe(
        periods,
        use_container_width=True,
        hide_index=True,
    )

    chart_rows = []
    for period in periods:
        chart_rows.append(
            {
                "date": period.get("date"),
                "temperature_max_c": period.get("temperature_max_c"),
                "temperature_min_c": period.get("temperature_min_c"),
            }
        )

    st.line_chart(chart_rows, x="date", y=["temperature_max_c", "temperature_min_c"])


def _render_alerts(alert_payload: dict[str, Any]) -> None:
    st.subheader(f"{alert_payload['location']} alerts")
    alerts = alert_payload.get("alerts") or []

    if not alerts:
        st.success("No active alerts were returned for this location.")
        return

    for alert in alerts:
        severity = str(alert.get("severity", "unknown")).upper()
        headline = alert.get("headline") or "Weather alert"
        with st.expander(f"{severity}: {headline}", expanded=True):
            st.write(f"**Event:** {alert.get('event') or 'Unknown'}")
            st.write(f"**Source:** {alert.get('source') or 'Unknown'}")
            st.write(f"**Start:** {alert.get('start') or 'Unknown'}")
            st.write(f"**End:** {alert.get('end') or 'Unknown'}")
            description = alert.get("description") or "No description available."
            st.write(description)


def _format_temperature(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f} C"


def _format_percent(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{value}%"
