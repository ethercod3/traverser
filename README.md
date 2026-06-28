# Traverser

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Category-Security%20Tool-red)
![Web](https://img.shields.io/badge/Target-Web%20Applications-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

Traverser is a Python-based utility for detecting **Path Traversal** vulnerabilities in web applications.  
It automates payload injection and request handling to help identify improper file path validation.

## Features

- Evidence-based Path Traversal vulnerability detection
- Custom wordlist support and built-in payload profiles
- Steady concurrent HTTP requests with session reuse
- Flexible payload placement in URLs, query params, headers, path segments, and POST bodies
- JSON or human-readable output

## Requirements

- Python **3.13** or newer

## Installation

```bash
git clone https://github.com/ethercod3/traverser.git
cd traverser
python -m venv .venv
```

### Activate the virtual environment

**Windows**
```bash
.venv\Scripts\activate
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

### Example

```bash
traverser \
  -u "https://localhost:8000/image?filename={INSERT_PAYLOAD}" \
  -t /etc/passwd \
  -p "{INSERT_PAYLOAD}" \
  --simultaneous-requests 5 \
  --profile linux
```

## Command-line Arguments

| Short | Long | Required | Description | Default |
|------|------|----------|-------------|---------|
| `-u` | `--url` | Yes | Target URL | — |
| `-t` | `--target` | Yes* | Target file path on the server. Can be repeated | — |
| — | `--target-file` | No | File with one target path per line | — |
| `-w` | `--wordlist` | No | Path to payload wordlist | `./default.wordlist` |
| `-h` | `--header` | No | Additional HTTP header(s) | — |
| `-sr` | `--simultaneous-requests` | No | Maximum number of concurrent requests | `1` |
| `-p` | `--place` | No | Payload placeholder string | `<>` |
| `-ss` | `--success-statuses` | No | Successfull HTTP statuses | `200-400` |
| — | `--timeout` | No | Total request timeout in seconds | `10.0` |
| — | `--retries` | No | Retries for transient connection failures | `0` |
| — | `--follow-redirects` / `--no-follow-redirects` | No | Enable or disable redirect following | follow |
| — | `--profile` | No | Built-in payload profile: `linux`, `windows`, `encoded`, `double-encoded`, `mixed-separator` | — |
| — | `--min-depth` / `--max-depth` | No | Traversal depth range for generated payloads | `1` / `6` |
| — | `--query-param` | No | Place payload in a query parameter | — |
| — | `--path-segment` | No | Place payload as a URL path segment | — |
| — | `--header-value` | No | Place payload in the named header | — |
| — | `--post-body` | No | Send payload as a POST body | — |
| — | `--json` | No | Emit JSON findings | `False` |
| — | `--output` | No | Write findings to a file | — |
| — | `--stop-on-first` | No | Stop after first high-confidence finding | `False` |
| — | `--max-findings` | No | Stop after N findings | — |
| `-v` | `--verbose` | No | Display verbose info | `False` |

*At least one `--target` or `--target-file` entry is required.

### Multiple headers example

```bash
-h "Authorization: Bearer TOKEN" \
-h "X-Custom-Header: value"
```

### Multiple ranges of the successfull HTTP statuses example

```bash
-ss "200-202" \
-ss "302"
```

Second number of the range is excluded. Result status codes will be `(200, 201, 302)`.

### Development checks

```bash
python -m pytest
python -m ruff check .
```

### Demo target

Run a local mock target and print a sample scan report:

```bash
uv run example
```
