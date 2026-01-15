from pathlib import Path


class WordListReader:
    def __init__(self, filepath: str) -> None:
        if not Path(filepath).exists():
            raise Exception(f"[-] File not found: {filepath}")
        self.filepath = filepath

    def read(self) -> list[str]:
        with open(self.filepath, "r") as f:
            return [s.strip() for s in f.readlines()]
