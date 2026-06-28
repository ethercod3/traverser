from collections.abc import Iterable

from traverser.models import Baseline, Confidence

MARKERS: dict[str, tuple[str, ...]] = {
    "passwd": ("root:x:", "daemon:x:", "/bin/"),
    "hosts": ("localhost", "127.0.0.1"),
    "win.ini": ("[fonts]", "[extensions]"),
    "boot.ini": ("[boot loader]", "[operating systems]"),
}


def markers_for_target(target: str) -> tuple[str, ...]:
    normalized = target.lower().replace("\\", "/").rstrip("/")
    name = normalized.rsplit("/", 1)[-1]
    if name in MARKERS:
        return MARKERS[name]
    return ()


def matched_markers(target: str, body: str) -> tuple[str, ...]:
    body_lower = body.lower()
    return tuple(marker for marker in markers_for_target(target) if marker.lower() in body_lower)


def classify_evidence(
    target: str,
    body: str,
    baseline: Baseline | None,
    status_success: bool,
) -> tuple[Confidence | None, str]:
    markers = matched_markers(target, body)
    if markers:
        return Confidence.MARKER_MATCH, ", ".join(markers)

    if status_success and baseline and _baseline_differs(body, baseline.body):
        return Confidence.BASELINE_DIFF_MATCH, "response differs from impossible-path baseline"

    if status_success:
        return Confidence.STATUS_ONLY, "configured success status"

    return None, ""


def _baseline_differs(body: str, baseline_body: str) -> bool:
    if not body or not baseline_body:
        return body != baseline_body
    return body.strip() != baseline_body.strip()


def is_high_confidence(confidence: Confidence) -> bool:
    return confidence in {Confidence.MARKER_MATCH, Confidence.BASELINE_DIFF_MATCH}


def best_confidence(confidences: Iterable[Confidence]) -> Confidence | None:
    order = {
        Confidence.MARKER_MATCH: 3,
        Confidence.BASELINE_DIFF_MATCH: 2,
        Confidence.STATUS_ONLY: 1,
    }
    return max(confidences, key=lambda item: order[item], default=None)
