# Traverser

Traverser is an evidence-based path traversal scanner for web applications.

It injects traversal payloads into a target request, checks response bodies for known file
markers, compares responses with an impossible-path baseline, and reports confidence for each
finding.

## Features

- Shared `aiohttp` session with steady concurrency.
- Evidence markers for Linux and Windows file targets.
- Baseline comparison to reduce false positives.
- Wordlist payloads and built-in payload profiles.
- Placeholder, query parameter, path segment, header, and POST body placement modes.
- Human-readable or JSON output.
- Local demo command with a mock vulnerable target.

## Quick Start

```bash
uv run traverser \
  --url "https://example.test/download?file=<>" \
  --target /etc/passwd \
  --simultaneous-requests 5 \
  --profile linux
```

Run the local demo:

```bash
uv run example
```
