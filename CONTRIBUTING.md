# Contributing

Thanks for contributing to EU Weather MCP Server.

## Development Setup

1. Install dependencies:

```powershell
uv sync --extra dev
```

2. Activate the environment if you want shell-local commands:

```powershell
.\activate.ps1
```

3. Run tests:

```powershell
uv run pytest
```

4. Run lint checks:

```powershell
uv run ruff check .
```

## Coding Guidelines

- Use Python 3.12 features intentionally
- Keep type hints on public functions
- Prefer small focused changes
- Preserve the terminal/MCP-first design
- Add or update tests when behavior changes

## Pull Requests

- Keep pull requests focused
- Include a short summary of the change
- Mention any user-facing behavior changes
- Mention test coverage or gaps in the PR description

## Reporting Issues

When reporting a bug, include:

- What you ran
- What you expected
- What happened instead
- Relevant logs or error output
- Your OS and Python version
