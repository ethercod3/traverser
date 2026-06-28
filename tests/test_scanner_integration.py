import asyncio

import pytest
from aiohttp import web

from traverser.models import ParsedArgs, PlacementMode
from traverser.scanner import DeliveryService


@pytest.fixture
async def test_server():
    app = web.Application()

    async def file_handler(request: web.Request) -> web.Response:
        filename = request.query.get("file", "")
        if "__traverser_impossible_" in filename:
            return web.Response(status=404, text="missing")
        if "etc/passwd" in filename:
            return web.Response(text="root:x:0:0:root:/root:/bin/bash")
        if "normal" in filename:
            return web.Response(text="normal page")
        return web.Response(status=404, text="not found")

    async def slow_handler(request: web.Request) -> web.Response:
        await asyncio.sleep(0.2)
        return web.Response(text="late")

    async def redirect_handler(request: web.Request) -> web.Response:
        raise web.HTTPFound("/file?file=../etc/passwd")

    app.router.add_get("/file", file_handler)
    app.router.add_get("/slow", slow_handler)
    app.router.add_get("/redirect", redirect_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    socket = site._server.sockets[0]
    host, port = socket.getsockname()[:2]
    yield f"http://{host}:{port}"
    await runner.cleanup()


def make_args(base_url: str, **overrides) -> ParsedArgs:
    values = {
        "wordlist": ["../"],
        "url": f"{base_url}/file?file=<>",
        "targets": ("/etc/passwd",),
        "headers": {},
        "sim_requests": 2,
        "payload_place": "<>",
        "status_codes": {200},
        "verbose": False,
        "timeout": 1.0,
        "retries": 0,
        "follow_redirects": True,
        "json_output": False,
        "output": None,
        "profiles": (),
        "min_depth": 1,
        "max_depth": 1,
        "placement_mode": PlacementMode.PLACEHOLDER,
        "query_param": None,
        "header_value": None,
        "stop_on_first": False,
        "max_findings": None,
    }
    values.update(overrides)
    return ParsedArgs(**values)


async def test_vulnerable_endpoint_returns_marker_finding(test_server) -> None:
    findings = await DeliveryService(make_args(test_server))._async_run()

    assert len(findings) == 1
    assert findings[0].confidence == "marker-match"


async def test_non_vulnerable_endpoint_returns_status_only(test_server) -> None:
    args = make_args(test_server, targets=("/normal",), wordlist=[""])
    findings = await DeliveryService(args)._async_run()

    assert len(findings) == 1
    assert findings[0].confidence == "status-only"


async def test_404_endpoint_has_no_findings(test_server) -> None:
    args = make_args(test_server, targets=("/missing",), wordlist=["../"])
    findings = await DeliveryService(args)._async_run()

    assert findings == []


async def test_slow_endpoint_triggers_timeout(test_server) -> None:
    args = make_args(
        test_server,
        url=f"{test_server}/slow?file=<>",
        timeout=0.01,
        targets=("/slow",),
        wordlist=["../"],
    )
    findings = await DeliveryService(args)._async_run()

    assert findings == []


async def test_redirect_follow_option(test_server) -> None:
    follow = make_args(test_server, url=f"{test_server}/redirect?file=<>", follow_redirects=True)
    no_follow = make_args(
        test_server,
        url=f"{test_server}/redirect?file=<>",
        follow_redirects=False,
    )

    follow_findings = await DeliveryService(follow)._async_run()
    no_follow_findings = await DeliveryService(no_follow)._async_run()

    assert follow_findings
    assert no_follow_findings == []
