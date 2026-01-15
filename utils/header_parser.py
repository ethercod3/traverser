from rich import print as rprint


class HeaderParser:
    def __init__(self, headers: list[str]):
        self.headers = headers

    def _parse_arg(self, arg: str) -> tuple[str, str]:
        key, value = arg.split(":")
        key, value = key.strip(), value.strip()
        return key, value

    def parse(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for header in self.headers:
            try:
                key, value = self._parse_arg(header)
                result[key] = value
            except ValueError:
                rprint(
                    f"[yellow][-] The header '{header}' is not valid HTTP header and will be not added to the requests[/yellow]"
                )
        return result
