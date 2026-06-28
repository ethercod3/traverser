import asyncio

from aiohttp import web

from traverser.logging import logger
from traverser.models import ParsedArgs, PlacementMode
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


def _example_args(base_url: str) -> ParsedArgs:
    return ParsedArgs(
        wordlist=["../"],
        url=f"{base_url}/download?file=<>",
        targets=("/etc/passwd", "/etc/hosts"),
        headers={"User-Agent": "Traverser example"},
        sim_requests=4,
        payload_place="<>",
        status_codes={200},
        verbose=False,
        timeout=5.0,
        retries=1,
        follow_redirects=True,
        json_output=False,
        output=None,
        profiles=(),
        min_depth=1,
        max_depth=3,
        placement_mode=PlacementMode.PLACEHOLDER,
        query_param=None,
        header_value=None,
        stop_on_first=False,
        max_findings=4,
    )


async def _run_example() -> None:
    runner, base_url = await _start_mock_server()
    try:
        logger.setLevel("WARNING")
        print(f"Mock target: {base_url}/download?file=<>")
        findings = await DeliveryService(_example_args(base_url)).run_async()
        write_or_print(render_output(findings, json_output=False), output=None)
    finally:
        await runner.cleanup()


def main() -> None:
    asyncio.run(_run_example())
