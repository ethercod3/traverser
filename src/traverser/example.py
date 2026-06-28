import asyncio
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from aiohttp import web

from traverser.cli import Parser
from traverser.logging import logger
from traverser.models import ParsedArgs
from traverser.output import render_output, write_or_print
from traverser.scanner import DeliveryService


async def _download_handler(request: web.Request) -> web.Response:
    filename = request.query.get("file", "")
    if "__traverser_impossible_" in filename:
        return web.Response(status=404, text="File not found")
    if "etc/passwd" in filename:
        return web.Response(
            text=(
                "root:x:0:0:root:/root:/bin/bash\n"
                "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
            )
        )
    if "etc/hosts" in filename:
        return web.Response(text="127.0.0.1 localhost\n")
    return web.Response(text="Public download placeholder")


async def _start_mock_server() -> tuple[web.AppRunner, str]:
    app = web.Application()
    app.router.add_get("/download", _download_handler)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    socket = site._server.sockets[0]
    host, port = socket.getsockname()[:2]
    return runner, f"http://{host}:{port}"


def _default_example_argv(base_url: str, wordlist_path: Path) -> list[str]:
    return [
        "--wordlist",
        str(wordlist_path),
        "--url",
        f"{base_url}/download?file=<>",
        "--target",
        "/etc/passwd",
        "--target",
        "/etc/hosts",
        "--header",
        "User-Agent: Traverser example",
        "--simultaneous-requests",
        "4",
        "--success-statuses",
        "200",
        "--timeout",
        "5.0",
        "--retries",
        "1",
        "--min-depth",
        "1",
        "--max-depth",
        "3",
        "--max-findings",
        "4",
    ]


def _example_args(
    base_url: str,
    wordlist_path: Path,
    argv: list[str] | None = None,
) -> ParsedArgs:
    return Parser().parse([*_default_example_argv(base_url, wordlist_path), *(argv or [])])


async def _run_example(argv: list[str] | None = None) -> None:
    runner, base_url = await _start_mock_server()
    try:
        with TemporaryDirectory(prefix="traverser-example-") as temp_dir:
            wordlist_path = Path(temp_dir) / "wordlist.txt"
            wordlist_path.write_text("../\n", encoding="utf-8")

            logger.setLevel("WARNING")
            print(f"Mock target: {base_url}/download?file=<>")
            args = _example_args(base_url, wordlist_path, argv)
            findings = await DeliveryService(args).run_async()
            write_or_print(render_output(findings, json_output=args.json_output), output=args.output)
    finally:
        await runner.cleanup()


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["--"]:
        args = args[1:]
    asyncio.run(_run_example(args))
