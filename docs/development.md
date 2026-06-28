# Development

## Install

```bash
uv sync --extra dev --extra docs
```

## Run Checks

```bash
uv run ruff check .
uv run pytest -p no:seleniumbase
uv run mkdocs build --strict
```

## Demo

```bash
uv run example
```

The demo starts a local aiohttp mock target, scans it, prints a report, and shuts the server down.

## Documentation

Serve the Material for MkDocs site locally:

```bash
uv run mkdocs serve
```

Build the static site:

```bash
uv run mkdocs build --strict
```
