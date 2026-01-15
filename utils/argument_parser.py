import argparse
from interfaces.parsedargs import ParsedArgs
from utils.wordlist_reader import WordListReader
from utils.header_parser import HeaderParser


class Parser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="Argument parser module", add_help=False
        )
        self._build()

    def parse(self) -> ParsedArgs:
        namespace = self.parser.parse_args()
        return self._to_dataclass(namespace)

    def _build(self) -> None:
        self.parser.add_argument(
            "--help", action="help", help="Show this help message and exit"
        )

        self.parser.add_argument(
            "-w",
            "--wordlist",
            dest="wordlist",
            metavar="FILE",
            help="Path to wordlist file",
            default="./default.wordlist",
        )

        self.parser.add_argument(
            "-u", "--url", dest="url", metavar="URL", required=True, help="Target URL"
        )

        self.parser.add_argument(
            "-t",
            "--target",
            dest="target",
            metavar="FILE",
            required=True,
            help="Path to target file",
        )

        self.parser.add_argument(
            "-h",
            "--header",
            dest="headers",
            metavar="HEADER",
            action="append",
            default=[],
            help="HTTP header (can be specified multiple times)",
        )

        self.parser.add_argument(
            "-sr",
            "--simultaneos-requests",
            dest="sim_requests",
            metavar="MAX_SIMULTANEOS_REQUESTS",
            default=1,
            help="Maximum number of simultaneos requests",
            type=int,
        )

        self.parser.add_argument(
            "-p",
            "--place",
            dest="payload_place",
            metavar="PAYLOAD_PLACE",
            default="<>",
            help="Character sequence to replace payload with",
        )

    def _to_dataclass(self, ns: argparse.Namespace) -> ParsedArgs:
        return ParsedArgs(
            wordlist=WordListReader(ns.wordlist).read(),
            url=ns.url,
            target=ns.target.lstrip("/"),
            headers=HeaderParser(ns.headers).parse(),
            sim_requests=ns.sim_requests,
            payload_place=ns.payload_place,
        )
