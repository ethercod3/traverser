from traverser.example import _example_args
from traverser.models import PlacementMode


def test_example_args_target_mock_download_endpoint() -> None:
    args = _example_args("http://127.0.0.1:12345")

    assert args.url == "http://127.0.0.1:12345/download?file=<>"
    assert args.targets == ("/etc/passwd", "/etc/hosts")
    assert args.placement_mode == PlacementMode.PLACEHOLDER
    assert args.max_findings == 4
