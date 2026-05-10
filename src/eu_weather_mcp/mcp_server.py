from __future__ import annotations

import json
import logging
import os
import signal
import sys
from typing import Any

from eu_weather_mcp.errors import WeatherMcpError
from eu_weather_mcp.service import WeatherService

LOGGER = logging.getLogger("eu_weather_mcp")


class StdioMcpServer:
    def __init__(self, service: WeatherService) -> None:
        self._service = service
        self._running = True

    def stop(self, *_args: object) -> None:
        self._running = False

    def serve(self) -> int:
        while self._running:
            raw_line = sys.stdin.readline()
            if raw_line == "":
                break
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            try:
                request = json.loads(raw_line)
                response = self._handle_request(request)
            except json.JSONDecodeError:
                response = self._error_response(None, -32700, "Invalid JSON")
            except WeatherMcpError as exc:
                response = self._error_response(None, exc.code, exc.message)
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("Unhandled server error")
                response = self._error_response(None, -32603, f"Internal error: {exc}")

            if response is not None:
                self._write_message(response)

        self._service.close()
        return 0

    def _handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params") or {}

        if method == "notifications/initialized":
            return None
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "serverInfo": {"name": "eu-weather-mcp-server", "version": "0.1.0"},
                    "capabilities": {"tools": {}},
                },
            }
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"status": "ok"}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": _tool_definitions()}}
        if method == "tools/call":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": self._handle_tool_call(params),
            }

        return self._error_response(request_id, -32601, f"Method not found: {method}")

    def _handle_tool_call(self, params: dict[str, Any]) -> dict[str, Any]:
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        LOGGER.info(
            json.dumps(
                {
                    "event": "tool_call",
                    "tool": tool_name,
                    "location": arguments.get("location"),
                }
            )
        )

        if tool_name == "get_weather_alerts":
            payload = self._service.get_weather_alerts(str(arguments.get("location", "")))
        elif tool_name == "get_forecast":
            payload = self._service.get_forecast(
                str(arguments.get("location", "")),
                str(arguments.get("type", "hourly")),
            )
        elif tool_name == "ping":
            payload = {"status": "ok"}
        else:
            raise WeatherMcpError(f"Unknown tool: '{tool_name}'")

        return {
            "content": [{"type": "text", "text": _format_pretty_json(payload)}],
            "structuredContent": payload,
            "isError": False,
        }

    def _write_message(self, message: dict[str, Any]) -> None:
        if sys.stdout.isatty():
            output = json.dumps(message, ensure_ascii=True, indent=2)
        else:
            output = json.dumps(message, ensure_ascii=True)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()

    def _error_response(self, request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "get_weather_alerts",
            "description": "Get active weather warnings for an EU location",
            "inputSchema": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        },
        {
            "name": "get_forecast",
            "description": "Get a weather forecast for an EU location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "type": {"type": "string", "enum": ["hourly", "daily"]},
                },
                "required": ["location", "type"],
            },
        },
        {
            "name": "ping",
            "description": "Check whether the server is healthy",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def _format_pretty_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    _configure_logging()
    service = WeatherService()
    server = StdioMcpServer(service)
    signal.signal(signal.SIGINT, server.stop)
    signal.signal(signal.SIGTERM, server.stop)
    return server.serve()


def _configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, stream=sys.stderr, format="%(message)s")


if __name__ == "__main__":
    raise SystemExit(main())
