from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Confidence(StrEnum):
    STATUS_ONLY = "status-only"
    MARKER_MATCH = "marker-match"
    BASELINE_DIFF_MATCH = "baseline-diff-match"


class PlacementMode(StrEnum):
    PLACEHOLDER = "placeholder"
    QUERY_PARAM = "query-param"
    PATH_SEGMENT = "path-segment"
    HEADER_VALUE = "header-value"
    POST_BODY = "post-body"


@dataclass(frozen=True)
class ParsedArgs:
    wordlist: list[str]
    url: str
    targets: tuple[str, ...]
    headers: dict[str, str]
    sim_requests: int
    payload_place: str
    status_codes: set[int]
    verbose: bool
    timeout: float
    retries: int
    follow_redirects: bool
    json_output: bool
    output: Path | None
    profiles: tuple[str, ...]
    min_depth: int
    max_depth: int
    placement_mode: PlacementMode
    query_param: str | None
    header_value: str | None
    stop_on_first: bool
    max_findings: int | None


@dataclass(frozen=True)
class Baseline:
    status: int | None
    body: str


@dataclass(frozen=True)
class Finding:
    target: str
    payload: str
    url: str
    status: int
    confidence: Confidence
    evidence: str
