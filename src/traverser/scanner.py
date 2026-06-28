import asyncio
import ssl
from uuid import uuid4

import aiohttp

from traverser.evidence import classify_evidence, is_high_confidence
from traverser.logging import logger
from traverser.models import Baseline, Finding, ParsedArgs
from traverser.payloads import generate_payloads, normalize_target
from traverser.request_builder import build_request


class DeliveryService:
    def __init__(self, args: ParsedArgs) -> None:
        self.args = args
        self.findings: list[Finding] = []
        self._stop = asyncio.Event()

    def run(self) -> list[Finding]:
        return asyncio.run(self.run_async())

    async def run_async(self) -> list[Finding]:
        return await self._async_run()

    async def _async_run(self) -> list[Finding]:
        connector = aiohttp.TCPConnector(limit=self.args.sim_requests)
        timeout = aiohttp.ClientTimeout(total=self.args.timeout)
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.args.headers,
        ) as session:
            baselines = await self._build_baselines(session)
            semaphore = asyncio.Semaphore(self.args.sim_requests)
            payloads_by_target = generate_payloads(
                wordlist=self.args.wordlist,
                profiles=self.args.profiles,
                targets=self.args.targets,
                min_depth=self.args.min_depth,
                max_depth=self.args.max_depth,
            )
            tasks = [
                asyncio.create_task(
                    self._guarded_deliver(session, semaphore, target, payload, baselines[target])
                )
                for target, payloads in payloads_by_target.items()
                for payload in payloads
            ]
            await asyncio.gather(*tasks)
        logger.info("Finished")
        return self.findings

    async def _build_baselines(self, session: aiohttp.ClientSession) -> dict[str, Baseline]:
        baselines: dict[str, Baseline] = {}
        for target in self.args.targets:
            impossible = f"../__traverser_impossible_{uuid4().hex}__/{normalize_target(target)}"
            request = build_request(self.args, impossible)
            try:
                status, body = await self._request(session, request)
                baselines[target] = Baseline(status=status, body=body)
            except aiohttp.InvalidURL as exc:
                raise SystemExit(f"invalid URL: {exc}") from exc
            except Exception as exc:
                self._log_error(request.url, exc)
                baselines[target] = Baseline(status=None, body="")
        return baselines

    async def _guarded_deliver(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        target: str,
        payload: str,
        baseline: Baseline,
    ) -> None:
        async with semaphore:
            if self._stop.is_set():
                return
            await self._deliver_payload(session, target, payload, baseline)

    async def _deliver_payload(
        self,
        session: aiohttp.ClientSession,
        target: str,
        payload: str,
        baseline: Baseline,
    ) -> None:
        request = build_request(self.args, payload)
        if self.args.verbose:
            logger.info("[*] Sending request to %s", request.url)
        try:
            status, body = await self._request_with_retries(session, request)
        except Exception as exc:
            self._log_error(request.url, exc)
            return

        confidence, evidence = classify_evidence(
            target=target,
            body=body,
            baseline=baseline if baseline.status == status else None,
            status_success=status in self.args.status_codes,
        )
        if confidence is None:
            return

        if self.args.max_findings is not None and len(self.findings) >= self.args.max_findings:
            self._stop.set()
            return

        finding = Finding(
            target=target,
            payload=payload,
            url=request.url,
            status=status,
            confidence=confidence,
            evidence=evidence,
        )
        self.findings.append(finding)
        logger.info(
            "[green][+] %s finding with HTTP %s: %s[/green]",
            confidence.value,
            status,
            request.url,
        )
        if self._should_stop(confidence):
            self._stop.set()

    async def _request_with_retries(
        self,
        session: aiohttp.ClientSession,
        request,
    ) -> tuple[int, str]:
        last_exc: Exception | None = None
        for _ in range(self.args.retries + 1):
            try:
                return await self._request(session, request)
            except (aiohttp.ClientConnectionError, TimeoutError) as exc:
                last_exc = exc
        if last_exc:
            raise last_exc
        raise RuntimeError("request failed without an exception")

    async def _request(self, session: aiohttp.ClientSession, request) -> tuple[int, str]:
        async with session.request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            data=request.data,
            allow_redirects=self.args.follow_redirects,
        ) as response:
            body = await response.text(errors="replace")
            return response.status, body

    def _should_stop(self, confidence) -> bool:
        if self.args.stop_on_first and is_high_confidence(confidence):
            return True
        return self.args.max_findings is not None and len(self.findings) >= self.args.max_findings

    @staticmethod
    def _log_error(url: str, exc: Exception) -> None:
        if isinstance(exc, TimeoutError):
            message = "timeout"
        elif isinstance(exc, aiohttp.InvalidURL):
            message = "invalid URL"
        elif isinstance(exc, aiohttp.ClientConnectorCertificateError | ssl.SSLError):
            message = "TLS error"
        elif isinstance(exc, aiohttp.ClientConnectorDNSError):
            message = "DNS error"
        elif isinstance(exc, aiohttp.ClientConnectionResetError):
            message = "connection reset"
        elif isinstance(exc, aiohttp.ClientConnectionError):
            message = "connection error"
        else:
            message = type(exc).__name__
        logger.error("[red][-] %s on request %s: %s[/red]", message, url, exc)
