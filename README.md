# EU Weather MCP Server

EU Weather MCP Server is a Python 3.12 project that provides European weather forecasts and alerts using the Open-Meteo API.

This project is terminal/MCP based. It does not include a web UI.

It is released as open-source software under the MIT License.

## What Works Today

- Get hourly forecasts for a European city or `lat,lon`
- Get daily forecasts for a European city or `lat,lon`
- Get active weather alerts for a European city or `lat,lon`
- Run as a local MCP server over stdio
- Build and run in Docker

## Tech Stack

- Python 3.12
- `uv`
- `httpx`
- `pytest`
- Docker

## Project Layout

```text
E:\Weather-MCP-Server
|-- src\eu_weather_mcp
|   |-- mcp_server.py
|   |-- openmeteo.py
|   |-- location.py
|   |-- service.py
|   `-- errors.py
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
- Docker installed if you want container builds

### Install runtime dependencies

```powershell
uv sync
```

### Install runtime and development dependencies

This installs test and lint tooling too.

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

## Open Source

- License: MIT
- Contributions are welcome
- Read [CONTRIBUTING.md](CONTRIBUTING.md) before sending changes
- Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Report vulnerabilities according to [SECURITY.md](SECURITY.md)

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
