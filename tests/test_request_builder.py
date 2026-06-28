from traverser.models import ParsedArgs, PlacementMode
from traverser.request_builder import build_request


def make_args(**overrides) -> ParsedArgs:
    values = {
        "wordlist": ["../"],
        "url": "https://example.test/base?x=1&file=<>",
        "targets": ("/etc/passwd",),
        "headers": {"User-Agent": "Traverser"},
        "sim_requests": 1,
        "payload_place": "<>",
        "status_codes": {200},
        "verbose": False,
        "timeout": 10.0,
        "retries": 0,
        "follow_redirects": True,
        "json_output": False,
        "output": None,
        "profiles": (),
        "min_depth": 1,
        "max_depth": 6,
        "placement_mode": PlacementMode.PLACEHOLDER,
        "query_param": None,
        "header_value": None,
        "stop_on_first": False,
        "max_findings": None,
    }
    values.update(overrides)
    return ParsedArgs(**values)


def test_placeholder_request() -> None:
    request = build_request(make_args(), "../etc/passwd")

    assert request.method == "GET"
    assert request.url == "https://example.test/base?x=1&file=../etc/passwd"


def test_query_param_request() -> None:
    request = build_request(
        make_args(
            url="https://example.test/base?x=1",
            placement_mode=PlacementMode.QUERY_PARAM,
            query_param="file",
        ),
        "../etc/passwd",
    )

    assert request.url == "https://example.test/base?x=1&file=..%2Fetc%2Fpasswd"


def test_path_segment_request() -> None:
    request = build_request(
        make_args(url="https://example.test/base", placement_mode=PlacementMode.PATH_SEGMENT),
        "../etc/passwd",
    )

    assert request.url == "https://example.test/base/..%2Fetc%2Fpasswd"


def test_header_value_request() -> None:
    request = build_request(
        make_args(placement_mode=PlacementMode.HEADER_VALUE, header_value="X-File"),
        "../etc/passwd",
    )

    assert request.headers["X-File"] == "../etc/passwd"


def test_post_body_request() -> None:
    request = build_request(make_args(placement_mode=PlacementMode.POST_BODY), "../etc/passwd")

    assert request.method == "POST"
    assert request.data == "../etc/passwd"
    assert request.headers["Content-Type"] == "text/plain"
