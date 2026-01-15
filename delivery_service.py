import aiohttp
import asyncio
from interfaces.parsedargs import ParsedArgs
from log.logger import logger, logger_extra


class DeliveryService:
    def __init__(self, args: ParsedArgs) -> None:
        self.args = args
        self.successfull_payloads: set[str] = set()

    def _craft_payload_url(self, payload: str) -> str:
        processed_payload = f"{payload}{self.args.target}"
        return self.args.url.replace(self.args.payload_place, processed_payload)

    def __log_verbose(self, msg: str) -> None:
        if self.args.verbose:
            logger.info(msg, extra=logger_extra)

    async def _deliver_payload(self, payload: str) -> None:
        url = self._craft_payload_url(payload=payload)
        try:
            self.__log_verbose(f"[*] Sending request to the URL {url}")
            async with aiohttp.ClientSession(headers=self.args.headers) as session:
                async with session.get(url) as response:
                    if response.status in self.args.status_codes:
                        logger.info(
                            f"[green][+] Payload succeeded with HTTP status code {response.status}: {url}[/green]",
                            extra=logger_extra,
                        )
                        self.successfull_payloads.add(payload)
                    else:
                        self.__log_verbose(
                            f"[yellow][-] Request to the URL {url} returned status code of {response.status}, which is not present in the success status codes [/yellow]"
                        )
        except Exception as e:
            logger.error(
                f"[italic red][-] Error {type(e)}[/italic red] occured on request: {e}",
                extra=logger_extra,
            )

    async def _async_run(self) -> None:
        tasks: list[asyncio.Task] = []
        for idx, payload in enumerate(self.args.wordlist, start=1):
            task: asyncio.Task = asyncio.create_task(
                self._deliver_payload(payload=payload)
            )
            tasks.append(task)
            if idx % self.args.sim_requests == 0:
                await asyncio.gather(*tasks)
                tasks.clear()
        await asyncio.gather(*tasks)

    def run(self) -> None:
        asyncio.run(self._async_run())
        logger.info("Finished")
