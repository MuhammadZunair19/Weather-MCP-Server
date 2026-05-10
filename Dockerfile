FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv sync --no-dev

FROM python:3.12-slim-bookworm
RUN useradd --create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src ./src
COPY README.md pyproject.toml ./
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
CMD ["eu-weather-mcp"]
