from traverser.evidence import classify_evidence, matched_markers
from traverser.models import Baseline, Confidence
from traverser.payloads import generate_payloads


def test_generate_payloads_combines_wordlist_profiles_and_targets() -> None:
    payloads = generate_payloads(
        wordlist=["../"],
        profiles=("linux", "encoded"),
        targets=("/etc/passwd",),
        min_depth=1,
        max_depth=2,
    )

    assert payloads["/etc/passwd"] == [
        "../etc/passwd",
        "../../etc/passwd",
        "..%2fetc/passwd",
        "..%2f..%2fetc/passwd",
    ]


def test_marker_matching_for_passwd() -> None:
    assert matched_markers("/etc/passwd", "root:x:0:0:root:/root:/bin/bash") == (
        "root:x:",
        "/bin/",
    )


def test_classify_marker_match_beats_status_only() -> None:
    confidence, evidence = classify_evidence(
        target="/etc/passwd",
        body="daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
        baseline=Baseline(status=404, body="missing"),
        status_success=True,
    )

    assert confidence == Confidence.MARKER_MATCH
    assert "daemon:x:" in evidence


def test_classify_baseline_diff() -> None:
    confidence, evidence = classify_evidence(
        target="/unknown/file",
        body="secret data",
        baseline=Baseline(status=200, body="normal page"),
        status_success=True,
    )

    assert confidence == Confidence.BASELINE_DIFF_MATCH
    assert "baseline" in evidence


def test_classify_status_only() -> None:
    confidence, evidence = classify_evidence(
        target="/unknown/file",
        body="normal page",
        baseline=Baseline(status=200, body="normal page"),
        status_success=True,
    )

    assert confidence == Confidence.STATUS_ONLY
    assert evidence == "configured success status"
