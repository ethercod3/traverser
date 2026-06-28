from pathlib import Path

from traverser.example import _example_args
from traverser.models import PlacementMode


def test_example_args_target_mock_download_endpoint(tmp_path: Path) -> None:
    wordlist_path = tmp_path / "wordlist.txt"
    wordlist_path.write_text("../\n", encoding="utf-8")

    args = _example_args("http://127.0.0.1:12345", wordlist_path)

    assert args.url == "http://127.0.0.1:12345/download?file=<>"
    assert args.wordlist == ["../"]
    assert args.targets == ("/etc/passwd", "/etc/hosts")
    assert args.placement_mode == PlacementMode.PLACEHOLDER
    assert args.max_findings == 4


def test_example_args_accept_user_overrides(tmp_path: Path) -> None:
    wordlist_path = tmp_path / "wordlist.txt"
    wordlist_path.write_text("../\n", encoding="utf-8")

    args = _example_args(
        "http://127.0.0.1:12345",
        wordlist_path,
        ["--max-depth", "8", "--timeout", "0.5", "--json"],
    )

    assert args.max_depth == 8
    assert args.timeout == 0.5
    assert args.json_output is True
