# Usage

## Scan a Placeholder URL

```bash
uv run traverser \
  --url "https://example.test/download?file=<>" \
  --target /etc/passwd \
  --wordlist default.wordlist
```

The `--place` value defaults to `<>`.

## Multiple Targets

```bash
uv run traverser \
  --url "https://example.test/download?file=<>" \
  --target /etc/passwd \
  --target /etc/hosts
```

Targets may also come from a file:

```bash
uv run traverser \
  --url "https://example.test/download?file=<>" \
  --target-file targets.txt
```

## Payload Profiles

```bash
uv run traverser \
  --url "https://example.test/download?file=<>" \
  --target /etc/passwd \
  --profile linux \
  --profile encoded \
  --min-depth 1 \
  --max-depth 6
```

Available profiles:

- `linux`
- `windows`
- `encoded`
- `double-encoded`
- `mixed-separator`

## Placement Modes

Placeholder replacement is the default and most flexible mode. Traverser also supports helpers:

```bash
uv run traverser --url "https://example.test/download" --target /etc/passwd --query-param file
uv run traverser --url "https://example.test/files" --target /etc/passwd --path-segment
uv run traverser --url "https://example.test/download" --target /etc/passwd --header-value X-File
uv run traverser --url "https://example.test/download" --target /etc/passwd --post-body
```

## Network Controls

```bash
uv run traverser \
  --url "https://example.test/download?file=<>" \
  --target /etc/passwd \
  --timeout 5 \
  --retries 2 \
  --no-follow-redirects
```

## Output

Default output is an ASCII report. JSON output is available for automation:

```bash
uv run traverser \
  --url "https://example.test/download?file=<>" \
  --target /etc/passwd \
  --json \
  --output findings.json
```
