# Traverser

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Category-Security%20Tool-red)
![Web](https://img.shields.io/badge/Target-Web%20Applications-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

Traverser is a Python-based utility for detecting **Path Traversal** vulnerabilities in web applications.  
It automates payload injection and request handling to help identify improper file path validation.

## Features

- Automated Path Traversal vulnerability detection
- Custom wordlist support
- Concurrent HTTP requests
- Flexible payload placement
- Support for custom HTTP headers

## Requirements

- Python **3.13.1** or newer

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

## Usage

### Example

```bash
python traverser.py \
  -u "https://localhost:8000/image?filename={INSERT_PAYLOAD}" \
  -t /etc/passwd \
  -p "{INSERT_PAYLOAD}" \
  -sr 5
```

## Command-line Arguments

| Short | Long | Required | Description | Default |
|------|------|----------|-------------|---------|
| `-u` | `--url` | Yes | Target URL | — |
| `-t` | `--target` | Yes | Target file path on the server | — |
| `-w` | `--wordlist` | No | Path to payload wordlist | `./default.wordlist` |
| `-h` | `--header` | No | Additional HTTP header(s) | — |
| `-sr` | `--simultaneous-requests` | No | Maximum number of concurrent requests | `1` |
| `-p` | `--place` | No | Payload placeholder string | `<>` |
| `-ss` | `--success-statuses` | No | Successfull HTTP statuses | `200-400` | 
| `-v` | `--verbose` | No | Display verbose info | `False` |

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

Second number of the range is excluded. Result status codes will be `(200, 201, 302)`