# EU Weather MCP Server

EU Weather MCP Server is a Python 3.12 project that provides European weather forecasts and alerts using the Open-Meteo API.

It currently includes:

- A stdio MCP-style server
- A local Streamlit UI
- EU-only location validation
- City-name lookup with an offline fallback list
- Docker support
- `uv`-based dependency management

## What Works Today

The project can do these things right now:

- Get hourly forecasts for a European city or `lat,lon`
- Get daily forecasts for a European city or `lat,lon`
- Get active weather alerts for a European city or `lat,lon`
- Run as a local MCP server over stdio
- Run as a local Streamlit web app

## Tech Stack

- Python 3.12
- `uv`
- `httpx`
- `streamlit`
- `pytest`
- Docker

## Project Layout

```text
E:\Weather-MCP-Server
|-- src\eu_weather_mcp
|   |-- mcp_server.py
|   |-- openmeteo.py
|   |-- service.py
|   `-- streamlit_app.py
|-- tests
|-- Dockerfile
|-- pyproject.toml
|-- requirements.txt
|-- requirements-dev.txt
`-- uv.lock
```

## Setup with UV

### Prerequisites

- Python 3.12 installed
- `uv` installed
- Docker installed if you want to build containers

### Install runtime dependencies

```powershell
uv sync
```

### Install runtime and development dependencies

This is the best setup for local development because it installs `pytest` and `ruff` too.

```powershell
uv sync --extra dev
```

### Activate the virtual environment

PowerShell:

```powershell
.\activate.ps1
```

Command Prompt:

```bat
activate.bat
```

You can also use the scripts inside `.venv\Scripts\` directly.

## Run the MCP Server

With `uv`:

```powershell
uv run eu-weather-mcp
```

After activating the environment:

```powershell
eu-weather-mcp
```

Or with Python directly:

```powershell
python -m eu_weather_mcp
```

## Run the Streamlit UI

Use this command:

```powershell
uv run streamlit run src/eu_weather_mcp/streamlit_app.py
```

Or after activating the environment:

```powershell
streamlit run src/eu_weather_mcp/streamlit_app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Important UI Note

The Streamlit page does not automatically fetch weather data on load.

You need to:

1. Enter a location like `Berlin`
2. Choose `hourly` or `daily`
3. Click `Get forecast` or `Get alerts`

If you open the page and do not click a button yet, the app only shows the input controls and a small info message. That is expected with the current UI.

## Run Tests

Install dev dependencies first if needed:

```powershell
uv sync --extra dev
```

Then run:

```powershell
uv run pytest
```

## Lint the Code

```powershell
uv run ruff check .
```

## Install with Requirements Files

If you do not want to use `uv`, you can install with `pip`.

Runtime only:

```powershell
pip install -r requirements.txt
```

Runtime and dev tools:

```powershell
pip install -r requirements-dev.txt
```

## Docker

### Build the image

```powershell
docker build -t eu-weather-mcp:latest .
```

### Run the container

This runs the stdio MCP server inside Docker:

```powershell
docker run -i --rm eu-weather-mcp:latest
```

## Publish Docker Image

Docker Hub example:

```powershell
docker build -t your-dockerhub-user/eu-weather-mcp:latest .
docker push your-dockerhub-user/eu-weather-mcp:latest
```

GitHub Container Registry example:

```powershell
docker build -t ghcr.io/your-github-user/eu-weather-mcp:latest .
docker push ghcr.io/your-github-user/eu-weather-mcp:latest
```

## MCP Examples

Initialize:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

List tools:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

Get hourly forecast:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_forecast","arguments":{"location":"Berlin","type":"hourly"}}}
```

Get alerts:

```json
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_weather_alerts","arguments":{"location":"48.8566,2.3522"}}}
```

## Current Limitations

- The app is Europe-only by design
- The MCP server is stdio-first
- SSE transport is not implemented yet
- There is no persistent storage
- The Streamlit UI is a simple local interface, not a production frontend

## Notes

- Logs go to `stderr` so MCP responses on `stdout` stay clean
- `uv.lock` is included for reproducible installs
- Weather data depends on the availability of Open-Meteo
