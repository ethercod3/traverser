import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

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
    console = Console(record=True)
    table = Table(title="Traverser findings")
    table.add_column("Confidence")
    table.add_column("Status")
    table.add_column("Target")
    table.add_column("Payload")
    table.add_column("Evidence")
    table.add_column("URL")
    for finding in findings:
        table.add_row(
            finding.confidence.value,
            str(finding.status),
            finding.target,
            finding.payload,
            finding.evidence,
            finding.url,
        )
    console.print(table)
    return console.export_text(clear=False)


def write_or_print(content: str, output: Path | None) -> None:
    if output:
        output.write_text(content, encoding="utf-8")
        return
    print(content)
