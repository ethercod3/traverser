from dataclasses import dataclass
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from traverser.models import ParsedArgs, PlacementMode


@dataclass(frozen=True)
class BuiltRequest:
    method: str
    url: str
    headers: dict[str, str]
    data: str | None


def build_request(args: ParsedArgs, payload: str) -> BuiltRequest:
    headers = dict(args.headers)
    if args.placement_mode == PlacementMode.PLACEHOLDER:
        return BuiltRequest("GET", args.url.replace(args.payload_place, payload), headers, None)

    if args.placement_mode == PlacementMode.QUERY_PARAM:
        return BuiltRequest(
            "GET",
            _with_query(args.url, args.query_param or "file", payload),
            headers,
            None,
        )

    if args.placement_mode == PlacementMode.PATH_SEGMENT:
        return BuiltRequest("GET", _with_path_segment(args.url, payload), headers, None)

    if args.placement_mode == PlacementMode.HEADER_VALUE:
        headers[args.header_value or "X-Traverser-Payload"] = payload
        return BuiltRequest("GET", args.url, headers, None)

    if args.placement_mode == PlacementMode.POST_BODY:
        headers.setdefault("Content-Type", "text/plain")
        return BuiltRequest("POST", args.url, headers, payload)

    raise ValueError(f"unsupported placement mode: {args.placement_mode}")


def _with_query(url: str, name: str, value: str) -> str:
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    query.append((name, value))
    return urlunsplit(parts._replace(query=urlencode(query)))


def _with_path_segment(url: str, payload: str) -> str:
    parts = urlsplit(url)
    path = parts.path.rstrip("/") + "/" + quote(payload, safe="")
    return urlunsplit(parts._replace(path=path))
