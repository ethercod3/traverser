import json
from pathlib import Path

from traverser.models import Finding


def serialize_findings(findings: list[Finding]) -> list[dict[str, object]]:
    return [
        {
            "target": finding.target,
            "payload": finding.payload,
            "url": finding.url,
            "status": finding.status,
            "confidence": finding.confidence.value,
            "evidence": finding.evidence,
        }
        for finding in findings
    ]


def render_output(findings: list[Finding], json_output: bool) -> str:
    if json_output:
        return json.dumps(serialize_findings(findings), indent=2)
    return _render_ascii_table(findings)


def write_or_print(content: str, output: Path | None) -> None:
    if output:
        output.write_text(content, encoding="utf-8")
        return
    print(content)


def _render_ascii_table(findings: list[Finding]) -> str:
    headers = ("Confidence", "Status", "Target", "Payload", "Evidence", "URL")
    rows = [
        (
            finding.confidence.value,
            str(finding.status),
            finding.target,
            finding.payload,
            finding.evidence,
            finding.url,
        )
        for finding in findings
    ]
    widths = [
        min(
            max(len(row[idx]) for row in (headers, *rows)) if rows else len(headers[idx]),
            48,
        )
        for idx in range(len(headers))
    ]
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    lines = ["Traverser findings", separator, _format_row(headers, widths), separator]
    lines.extend(_format_row(row, widths) for row in rows)
    lines.append(separator)
    return "\n".join(lines)


def _format_row(row: tuple[str, ...], widths: list[int]) -> str:
    cells = [_clip(value, width).ljust(width) for value, width in zip(row, widths, strict=True)]
    return "| " + " | ".join(cells) + " |"


def _clip(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    if width <= 3:
        return value[:width]
    return value[: width - 3] + "..."
