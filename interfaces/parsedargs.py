from dataclasses import dataclass


@dataclass
class ParsedArgs:
    wordlist: str
    url: str
    target: str
    headers: list[str]
    sim_requests: int
    payload_place: str
