# Software Requirements Specification (SRS)

## Current Implementation Status

This repository now includes an initial working implementation under `src/eu_weather_mcp/` with:

- A stdio JSON-RPC/MCP-style server entry point
- `get_weather_alerts`, `get_forecast`, and `ping` tools
- Open-Meteo geocoding, forecast, and warnings client logic
- EU-only location validation plus an offline fallback list of major EU cities
- Unit tests for location resolution and Open-Meteo response mapping
- A Dockerfile and `pyproject.toml` for packaging

## Quick Start

### Local development with `uv`

```bash
uv sync
uv run pytest
uv run eu-weather-mcp
```

### Activate the local virtual environment

PowerShell:

```powershell
.\activate.ps1
```

Command Prompt:

```bat
activate.bat
```

The underlying venv activation scripts also exist in `.venv/Scripts/`.

### Install with `requirements.txt`

Runtime only:

```bash
pip install -r requirements.txt
```

Runtime + dev tools:

```bash
pip install -r requirements-dev.txt
```

### Run with Python directly

```bash
python -m eu_weather_mcp
```

### Example MCP messages over stdio

Initialize:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

List tools:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

Call hourly forecast:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_forecast","arguments":{"location":"Berlin","type":"hourly"}}}
```

Call alerts:

```json
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_weather_alerts","arguments":{"location":"48.8566,2.3522"}}}
```

## Notes

- Logs are written to `stderr` so stdio protocol output on `stdout` stays valid for MCP clients.
- The repo does not include a generated `uv.lock` yet; create it with `uv lock` in an environment where `uv` is installed.

## for **EU Weather MCP Server**

**Version 1.0**  
**Date:** 2026-05-08  
**Prepared by:** [Your Name]  
**Project Type:** Model Context Protocol (MCP) Server for resume portfolio

---

## 1. Introduction

### 1.1 Purpose
This document defines the complete software requirements for the **EU Weather MCP Server** – a production‑ready MCP server that delivers weather alerts and forecasts for European locations. The server is containerized with Docker, managed with `uv` (Python package and project manager), and exposes weather data via the Model Context Protocol (MCP) for use by AI assistants and client applications.

### 1.2 Scope
The server will:
- Accept requests for **weather alerts** (e.g., warnings, watches) and **forecasts** (hourly/daily) for any European city or coordinate.
- Retrieve data from a publicly available weather API that covers the EU (Note: the US National Weather Service API is limited to US territory; therefore this project uses the **Open‑Meteo** API – a free, no‑API‑key weather service with full EU coverage).
- Implement the **MCP** transport (stdio or SSE) to communicate with MCP clients.
- Provide a clear, typed interface using JSON‑RPC over MCP.
- Run inside a Docker container for portability and easy deployment.
- Use `uv` for fast, reproducible dependency management and script execution.

### 1.3 Definitions & Acronyms
| Term | Definition |
|------|-------------|
| **MCP** | Model Context Protocol – a protocol for exposing tools and data to AI models. |
| **UV** | A fast Python package and project manager (replaces pip, poetry, etc.). |
| **NWS** | US National Weather Service – *not used because it does not cover Europe*. |
| **Open‑Meteo** | Free weather API with high‑resolution European data (https://open‑meteo.com). |
| **Alert** | A severe weather warning issued by an official European weather service (via Open‑Meteo’s alerts endpoint). |
| **Forecast** | Predictive weather parameters (temp, wind, precipitation, etc.) for a future time. |
| **MCP Client** | Any application (e.g., Claude Desktop, custom AI agent) that connects to the MCP server. |

### 1.4 References
- Model Context Protocol specification: https://modelcontextprotocol.io
- Open‑Meteo API documentation: https://open‑meteo.com/en/docs
- Docker: https://www.docker.com
- `uv` documentation: https://docs.astral.sh/uv

---

## 2. Overall Description

### 2.1 Product Perspective
The EU Weather MCP Server is a self‑contained backend service. It sits between an MCP client (like an AI assistant) and the Open‑Meteo weather API. It translates MCP tool calls into HTTP requests, processes the responses, and returns structured results. The system does not store any persistent data – it acts as a stateless proxy.

**Context diagram:**
```
[ MCP Client (e.g., Claude) ] 
        │
        │ JSON‑RPC (stdio/SSE)
        ▼
[ EU Weather MCP Server ] – Docker + uv
        │
        │ HTTPS
        ▼
[ Open‑Meteo API ] (EU weather data)
```

### 2.2 User Characteristics
- **Primary users:** AI agents (autonomous) and developers integrating weather functions into chat‑based tools.
- **No direct human‑GUI interaction** – all access is programmatic via MCP.

### 2.3 Operational Environment
- **Host OS:** Linux, macOS, or Windows (with Docker Desktop)
- **Runtime:** Docker container (Linux based)
- **Python version:** 3.12+ (managed by `uv`)
- **Network:** Outbound HTTPS access to `api.open‑meteo.com`

### 2.4 Constraints & Assumptions
- **API limitation:** Open‑Meteo is free, but rate‑limited – the server will implement a simple retry/backoff strategy.
- **No authentication:** Open‑Meteo does not require an API key; therefore the MCP server has no built‑in auth. For a real resume project, this is acceptable, but it can be noted as “extendable”.
- **EU coverage only:** Requests for non‑EU locations will return an error (including US locations, because NWS is not used).
- **Latency:** Open‑Meteo responses average 200‑500 ms – the server will time out after 30 seconds.
- **Resilience:** The server will log errors but not crash. It will start successfully even if the external API is temporarily unreachable.

### 2.5 Design Rationale for Using Open‑Meteo Instead of NWS
The original idea mentioned “NWS API”, but the National Weather Service only covers the **United States** and its territories, not the EU. To fulfill the requirement for **EU locations**, we substitute NWS with **Open‑Meteo**, which:
- Provides free, high‑quality weather alerts and forecasts for every European country.
- Includes official weather warnings from national services (e.g., DWD, Météo‑France, Met Office).
- Has a straightforward JSON API with no API key required – ideal for a portable Docker project.

This choice makes the project both functional for EU locations and demonstrable in any environment.

---

## 3. Functional Requirements

### 3.1 MCP Tools

The server shall expose the following MCP tools:

| Tool Name | Description | Input Parameters | Output |
|-----------|-------------|------------------|--------|
| `get_weather_alerts` | Retrieve active weather warnings for an EU location. | `location` (string: city name or "lat,lon") | List of alerts with severity, description, start/end time, source. |
| `get_forecast` | Get a weather forecast (hourly or daily) for the next 7 days. | `location` (string), `type` (enum: "hourly" or "daily") | Forecast data: temperature, wind speed, precipitation probability, etc. |

### 3.2 Detailed Tool Specifications

#### 3.2.1 `get_weather_alerts`
- **Input validation:**
  - If `location` is a city name (e.g., "Berlin", "Paris"), the server must geocode it to coordinates using a local lightweight method (e.g., a bundled CSV of EU cities or call to Open‑Meteo’s geocoding API).
  - If `location` is `"lat,lon"` (e.g., `"52.52,13.40"`), parse directly.
  - Reject locations outside Europe (e.g., "New York", "Tokyo") with a clear error message.
- **API call:** `GET https://api.open-meteo.com/v1/warnings?latitude={lat}&longitude={lon}`
- **Output format (example):**
  ```json
  {
    "alerts": [
      {
        "severity": "orange",
        "event": "Heavy Rain",
        "headline": "Heavy rainfall expected in Berlin area",
        "description": "…",
        "start": "2026-05-10T12:00:00Z",
        "end": "2026-05-11T00:00:00Z",
        "source": "DWD"
      }
    ]
  }
  ```

#### 3.2.2 `get_forecast`
- **Input:** location (same resolution as above) and forecast type.
- **API call:**  
  - Hourly: `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,windspeed_10m,precipitation_probability&timezone=auto`  
  - Daily: `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto`
- **Output mapping:** Simplify the response to a human‑readable list of forecast periods.
- **Error handling:** If forecast requested for >7 days, truncate with a warning.

### 3.3 MCP Transport & Lifecycle
- **Transport:** The server must support **stdio** (default for local usage) and optionally SSE (for remote deployment). For the resume project, stdio is sufficient.
- **Initialization:** On start, the server prints an MCP `initialize` response and waits for client requests.
- **Shutdown:** Gracefully handle `SIGTERM`/`SIGINT` and close any pending HTTP connections.

### 3.4 Logging & Debugging
- Log every incoming tool call (timestamp, tool name, location) to `stdout` (JSON format).
- Log API errors and retries.
- Set log level via environment variable `LOG_LEVEL` (INFO by default).

---

## 4. Non‑Functional Requirements

### 4.1 Performance
- **Response time:** < 3 seconds for 95% of requests (including external API call and processing).
- **Throughput:** Handle at least 10 concurrent requests (limited by Open‑Meteo rate, but acceptable for a resume demo).
- **Start‑up time:** Docker container starts in < 5 seconds.

### 4.2 Reliability & Availability
- **Error recovery:** If Open‑Meteo returns 5xx or times out, the server retries up to 3 times with exponential backoff (1s, 2s, 4s). Then returns a friendly error.
- **No state loss:** Stateless server – no data persistence, so no corruption.
- **Health check:** Provide an MCP `ping` tool (optional) or respond to a simple `GET /health` on internal port 8080 (if using SSE).

### 4.3 Security
- **No secrets:** Because Open‑Meteo requires no API key, no environment secrets are needed. This simplifies deployment.
- **Input sanitisation:** All location strings are validated to prevent command injection or path traversal (already safe because we use parameterised HTTP calls).
- **Docker non‑root:** The container runs as a non‑root user (e.g., `appuser`).

### 4.4 Maintainability & Code Quality
- **Language & style:** Python 3.12, type hints for all functions, `ruff` linting + formatting.
- **Testing:** Unit tests for location parsing, error formatting, and mock API responses. Use `pytest`.
- **Documentation:** `README.md` with build and run instructions (Docker + uv). Also MCP tool examples.
- **Dependency pinning:** All dependencies locked via `uv.lock` for reproducible builds.

### 4.5 Deployment & Build
- **Dockerfile:** Multi‑stage, using `ghcr.io/astral-sh/uv:latest` as builder, then slim Python runtime.
- **`uv` commands:** `uv sync`, `uv run` to start the server.
- **Container registry ready:** Can be pushed to Docker Hub or GitHub Container Registry.

### 4.6 Portability
- The server must run identically on Linux x86_64, ARM64 (Apple Silicon), and Windows WSL2.
- All external dependencies are Python packages fetched via `uv` – no system libraries required.

---

## 5. External Interface Requirements

### 5.1 User Interfaces
None – machine‑to‑machine only.

### 5.2 Hardware Interfaces
None.

### 5.3 Software Interfaces

| Interface | Description | Protocol | Data Format |
|-----------|-------------|----------|--------------|
| MCP Client → Server | Incoming tool requests | JSON‑RPC over stdio (or SSE) | MCP‑spec JSON |
| Server → Open‑Meteo API | Retrieve weather data | HTTPS | JSON |
| Server → stdout | Logs and MCP protocol messages (when stdio transport is used, the client reads them) | Plain text | JSON lines / human text |

### 5.4 Communication Interfaces
- **Outbound:** Only standard HTTP/1.1 or HTTP/2 to `api.open-meteo.com` (TCP port 443).
- **Inbound (stdio):** Standard input/output of the container process – used by Docker/MCP client.

---

## 6. System Features (Detailed)

### Feature 6.1: Location Geocoding
Because the MCP server must accept city names, we implement a lightweight geocoding fallback:
1. Try Open‑Meteo’s geocoding API: `https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1`
2. If no result or network error, fall back to an internal mapping of ~50 major EU cities (bundled as JSON). This guarantees offline demo capability.
3. Return error if location still unresolved.

### Feature 6.2: Alert Filtering & Formatting
Open‑Meteo returns alerts for a radius around the given point. The server will:
- Filter alerts that are actually relevant to the location (already done by API).
- Transform the raw warning codes into human‑readable severity levels (green/yellow/orange/red).
- Combine multiple alerts for the same area into a concise list.

### Feature 6.3: MCP Tool Registration
On start, the server announces the two tools using MCP’s `tools/list` response. Example response:
```json
{
  "tools": [
    {
      "name": "get_weather_alerts",
      "description": "Get active weather warnings for an EU location",
      "inputSchema": {...}
    },
    ...
  ]
}
```

### Feature 6.4: Error Handling & User Feedback
All errors returned by the MCP server follow a consistent format:
```json
{
  "error": {
    "code": -32000,
    "message": "Location not found in Europe: 'New York'"
  }
}
```
HTTP errors from Open‑Meteo are translated into MCP‑friendly messages with suggestions.

---

## 7. Build & Deployment Specification

### 7.1 `uv` Integration
- `pyproject.toml` defines:
  - Project metadata, Python version, dependencies (`httpx`, `pydantic`, `mcp`, etc.)
  - Script entry point: `[project.scripts]` or `uv run mcp-server`
- **Dependencies:**
  ```toml
  dependencies = [
      "mcp>=0.1.0",
      "httpx>=0.27.0",
      "pydantic>=2.0",
  ]
  ```
- **Dev dependencies:** `pytest`, `ruff`, `mypy`.

### 7.2 Docker Build
- **Dockerfile** (optimised):
  ```dockerfile
  FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
  WORKDIR /app
  COPY pyproject.toml uv.lock ./
  RUN uv sync --frozen --no-dev

  FROM python:3.12-slim-bookworm
  WORKDIR /app
  COPY --from=builder /app/.venv /app/.venv
  COPY src/ ./src/
  ENV PATH="/app/.venv/bin:$PATH"
  EXPOSE 8080  # optional for SSE
  CMD ["python", "-m", "src.mcp_server"]
  ```

- **Build command:** `docker build -t eu-weather-mcp:latest .`
- **Run command:** `docker run -i --rm eu-weather-mcp:latest`  (for stdio, interactively)

