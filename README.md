# Traverser - python script for finding path traversal vulnerabilities

## Example usage

```bash
python traverser.py -u "https://localhost:8000/image?filename={INSERT_PAYLOAD}" -t etc/passwd -p "{INSERT_PAYLOAD}" -sr 5
```

## Arguments

### -w or --wordlist
Not required. Filepath to the wordlist. Default: ./default.wordlist

### -u or --url
Required. URL to attack

### -t or --target
Required. Target filepath

### -h or --header
Not required. Additional HTTP header. You can add multiple headers ad follows

```
-h "Header-A: A" -h "Header-B: B"
```

### -sr or --simultaneos-requests
Not required. Maximum number of simultaneos requests. Default: 1

### -p or --place
Not required. Character sequence to replace payload with. Default: <>

## Installation

The script was written on `Python 3.13.1`

1. Clone the repo
2. Go to the downloaded directory
3. Run `python -m venv .venv`
4. Activate the virtual env: `.venv/scripts/activate` on Windows or `source .venv/bin/activate` on Linux
5. Now you can run the script