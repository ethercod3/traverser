# Traverser Improvement Plan

This file captures the improvement backlog for the path traversal scanner so the work can continue in a later session.

## Current State

- Small Python CLI entrypoint: `traverser.py`.
- Main request logic lives in `delivery_service.py`.
- CLI parsing and value parsing live under `utils/`.
- Detection currently treats selected HTTP status codes as success.
- Requests are concurrent in batches, but each payload creates its own `aiohttp.ClientSession`.
- Project uses `requirements.txt` with pinned direct and transitive dependencies.

## Highest Priority

1. Improve finding quality with response evidence.
   - Do not treat HTTP status alone as proof.
   - Read response body for known file markers.
   - Suggested markers:
     - `/etc/passwd`: `root:x:`, `daemon:x:`, `/bin/`
     - `/etc/hosts`: `localhost`, `127.0.0.1`
     - Windows `win.ini`: `[fonts]`, `[extensions]`
     - Windows `boot.ini`: `[boot loader]`, `[operating systems]`
   - Add baseline comparison using a random impossible target path.
   - Report confidence: status-only, marker match, baseline-diff match.

2. Reuse one HTTP session.
   - Create one `aiohttp.ClientSession` for the whole run.
   - Use `aiohttp.TCPConnector(limit=args.sim_requests)`.
   - Pass the session into each request task.
   - This should reduce overhead and improve connection reuse.

3. Replace batch concurrency with steady concurrency.
   - Current batching waits for each batch to fully finish before starting the next batch.
   - Use `asyncio.Semaphore` or a worker queue.
   - Keep up to `--simultaneous-requests` in flight until the wordlist is done.

4. Add network controls.
   - `--timeout` for total request timeout.
   - `--retries` for transient failures.
   - `--follow-redirects` / `--no-follow-redirects`.
   - Clear error handling for timeout, DNS, TLS, connection reset, and invalid URL.

## Correctness Fixes

1. Fix CLI spelling while keeping compatibility.
   - Current code accepts `--simultaneos-requests`.
   - README documents `--simultaneous-requests`.
   - Add correct spelling as the primary option.
   - Keep typo alias hidden or documented as deprecated.

2. Validate CLI arguments.
   - Fail early if the URL does not contain the payload placeholder.
   - Require `sim_requests > 0`.
   - Validate HTTP status codes are between `100` and `599`.
   - Validate status ranges are ascending and parse cleanly.
   - Return argparse errors instead of raw exceptions.

3. Fix header parsing.
   - Current parser uses `split(":")`.
   - Use `split(":", 1)` so values can contain colons.
   - Reject empty header names.

4. Fix type annotations.
   - `ParsedArgs.wordlist` should be `list[str]`, not `str`.
   - `ParsedArgs.headers` should be `dict[str, str]`, not `list[str]`.
   - Consider making the dataclass frozen.

5. Fix lint issue.
   - `not "-" in status` should be `"-" not in status`.

## Product Features

1. Output formats.
   - Human table output by default.
   - `--json` for automation.
   - `--output FILE` to write findings.

2. Better payload generation.
   - Keep wordlist support.
   - Add built-in payload profiles:
     - linux
     - windows
     - encoded
     - double-encoded
     - mixed-separator
   - Generate traversal depth from `--min-depth` / `--max-depth`.

3. Multiple targets.
   - Allow multiple `--target` values.
   - Or support a target file list.
   - Map each target to expected evidence markers.

4. Request placement modes.
   - Current placeholder replacement is flexible and should stay.
   - Add optional helpers for common placements:
     - query parameter
     - path segment
     - header value
     - POST body

5. Stop conditions.
   - `--stop-on-first` to exit after first high-confidence finding.
   - `--max-findings` to limit output.

## Testing Plan

1. Unit tests.
   - `HeaderParser`
   - `HTTPStatusCodesParser`
   - `WordListReader`
   - URL payload crafting
   - evidence matching

2. Integration tests.
   - Use a small local aiohttp server.
   - Cases:
     - vulnerable endpoint returns fake `/etc/passwd`
     - non-vulnerable endpoint returns normal 200
     - endpoint returns 404
     - slow endpoint triggers timeout
     - redirect endpoint follows or rejects based on option

3. Tooling.
   - Add `pyproject.toml`.
   - Configure `ruff`.
   - Add `pytest`.
   - Add a simple CI workflow later if the repo will be maintained on GitHub.

## Packaging Plan

1. Replace dependency management.
   - Move from raw `requirements.txt` to `pyproject.toml`.
   - Keep only direct runtime dependencies:
     - `aiohttp`
     - `rich`
   - Put dev tools under optional dependencies:
     - `ruff`
     - `pytest`

2. Add console entrypoint.
   - Installable command: `traverser`.
   - Keep `python traverser.py` working during transition if useful.

3. Version and metadata.
   - Add license file if missing.
   - Add package metadata.
   - Add supported Python version based on actual needs, likely lower than Python 3.13 if no 3.13-only feature is used.

## Suggested First PR

Scope: make scanner faster and less noisy without changing the public shape too much.

1. Fix types and parser bugs.
2. Add correct `--simultaneous-requests` alias.
3. Reuse one `aiohttp.ClientSession`.
4. Replace batch concurrency with semaphore concurrency.
5. Add `--timeout`.
6. Add body evidence markers for common targets.
7. Add focused tests for parsers and evidence detection.

Expected result: fewer false positives, faster scans, and a cleaner base for later features.
