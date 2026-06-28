from pathlib import Path


class HeaderParser:
    def __init__(self, headers: list[str]):
        self.headers = headers

    def _parse_arg(self, arg: str) -> tuple[str, str]:
        key, value = arg.split(":", 1)
        key, value = key.strip(), value.strip()
        if not key:
            raise ValueError("header name cannot be empty")
        return key, value

    def parse(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for header in self.headers:
            key, value = self._parse_arg(header)
            result[key] = value
        return result


class HTTPStatusCodesParser:
    def __init__(self, statuses: list[str]):
        self.statuses = statuses

    def parse(self) -> set[int]:
        result: set[int] = set()
        for status in self.statuses:
            if "-" not in status:
                result.add(self._parse_status(status))
                continue

            start_raw, end_raw = status.split("-", 1)
            start = self._parse_status(start_raw)
            end = self._parse_status(end_raw)
            if start >= end:
                raise ValueError(f"status range must ascend: {status}")
            result.update(range(start, end))
        return result

    @staticmethod
    def _parse_status(raw: str) -> int:
        try:
            status = int(raw)
        except ValueError as exc:
            raise ValueError(f"invalid HTTP status code: {raw}") from exc
        if status < 100 or status > 599:
            raise ValueError(f"HTTP status code out of range: {status}")
        return status


class WordListReader:
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"wordlist file not found: {filepath}")

    def read(self) -> list[str]:
        return [
            line.strip()
            for line in self.filepath.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
