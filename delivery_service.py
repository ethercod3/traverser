import aiohttp
import asyncio
from rich import print as rprint
from interfaces.parsedargs import ParsedArgs


class DeliveryService:
    def __init__(self, args: ParsedArgs) -> None:
        self.args = args

    def _craft_payload_url(self, payload: str) -> str:
        processed_payload = f"{payload * 20}{self.args.target}"
        return f"{self.args.url}".replace(self.args.payload_place, processed_payload)

    async def _deliver_payload(self, payload: str) -> None:
        url = self._craft_payload_url(payload=payload)
        try:
            async with aiohttp.ClientSession(headers=self.args.headers) as session:
                async with session.get(url) as response:
                    if response.status in range(200, 400):
                        rprint(
                            f"[green][+] PAYLOAD SUCCESSFULL WITH STATUS CODE {response.status}: {url}[/green]"
                        )
        except Exception as e:
            rprint(
                f"[italic red][-] Error {type(e)}[/italic red] occured on request: {e}"
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
