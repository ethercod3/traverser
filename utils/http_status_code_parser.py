class HTTPStatusCodesParser:
    def __init__(self, statuses: list[str]):
        self.statuses = statuses

    def parse(self) -> set[int]:
        result = set()
        for status in self.statuses:
            if not "-" in status:
                result.add(int(status))
            else:
                a, b = status.split("-")
                a, b = int(a), int(b)
                result = result.union(set(range(a, b)))
        return result
