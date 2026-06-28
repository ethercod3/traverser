import pytest

from traverser.cli import Parser
from traverser.models import PlacementMode


def parse_args(tmp_path, *args: str):
    wordlist = tmp_path / "wordlist.txt"
    wordlist.write_text("../\n", encoding="utf-8")
    return Parser().parse(["--wordlist", str(wordlist), *args])


def test_cli_accepts_correct_and_typo_concurrency_aliases(tmp_path) -> None:
    args = parse_args(tmp_path, "-u", "https://example.test/?f=<>", "-t", "/etc/passwd", "-sr", "3")
    typo_args = parse_args(
        tmp_path,
        "-u",
        "https://example.test/?f=<>",
        "-t",
        "/etc/passwd",
        "--simultaneos-requests",
        "4",
    )

    assert args.sim_requests == 3
    assert typo_args.sim_requests == 4


def test_cli_rejects_missing_placeholder(tmp_path) -> None:
    with pytest.raises(SystemExit):
        parse_args(tmp_path, "-u", "https://example.test/", "-t", "/etc/passwd")


def test_cli_allows_query_param_without_placeholder(tmp_path) -> None:
    args = parse_args(
        tmp_path,
        "-u",
        "https://example.test/",
        "-t",
        "/etc/passwd",
        "--query-param",
        "file",
    )

    assert args.placement_mode == PlacementMode.QUERY_PARAM
    assert args.query_param == "file"


def test_cli_reads_target_file(tmp_path) -> None:
    target_file = tmp_path / "targets.txt"
    target_file.write_text("/etc/passwd\n/etc/hosts\n", encoding="utf-8")
    args = parse_args(
        tmp_path,
        "-u",
        "https://example.test/?f=<>",
        "--target-file",
        str(target_file),
    )

    assert args.targets == ("/etc/passwd", "/etc/hosts")
