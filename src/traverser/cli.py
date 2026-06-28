import argparse
from pathlib import Path

from traverser.models import ParsedArgs, PlacementMode
from traverser.output import render_output, write_or_print
from traverser.parsers import HeaderParser, HTTPStatusCodesParser, WordListReader
from traverser.payloads import PROFILE_CHOICES
from traverser.scanner import DeliveryService


class Parser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description="Path traversal scanner", add_help=False)
        self._build()

    def parse(self, argv: list[str] | None = None) -> ParsedArgs:
        namespace = self.parser.parse_args(argv)
        return self._to_dataclass(namespace)

    def _build(self) -> None:
        self.parser.add_argument("--help", action="help", help="Show this help message and exit")
        self.parser.add_argument("-w", "--wordlist", default="./default.wordlist", metavar="FILE")
        self.parser.add_argument("-u", "--url", required=True, metavar="URL")
        self.parser.add_argument("-t", "--target", action="append", default=[], metavar="FILE")
        self.parser.add_argument("--target-file", metavar="FILE")
        self.parser.add_argument(
            "-h",
            "--header",
            dest="headers",
            action="append",
            default=[],
            metavar="HEADER",
        )
        self.parser.add_argument(
            "-sr",
            "--simultaneous-requests",
            dest="sim_requests",
            metavar="MAX",
            default=1,
            type=int,
            help="Maximum number of concurrent requests",
        )
        self.parser.add_argument(
            "--simultaneos-requests",
            dest="sim_requests",
            metavar="MAX",
            type=int,
            help=argparse.SUPPRESS,
        )
        self.parser.add_argument(
            "-p",
            "--place",
            dest="payload_place",
            default="<>",
            metavar="TEXT",
        )
        self.parser.add_argument(
            "-ss",
            "--success-statuses",
            dest="success_statuses",
            default=[],
            action="append",
            metavar="STATUS",
        )
        self.parser.add_argument("-v", "--verbose", action="store_true")
        self.parser.add_argument("--timeout", type=float, default=10.0)
        self.parser.add_argument("--retries", type=int, default=0)
        self.parser.add_argument(
            "--follow-redirects",
            dest="follow_redirects",
            action="store_true",
            default=True,
        )
        self.parser.add_argument(
            "--no-follow-redirects",
            dest="follow_redirects",
            action="store_false",
        )
        self.parser.add_argument("--json", dest="json_output", action="store_true")
        self.parser.add_argument("--output", type=Path)
        self.parser.add_argument("--profile", choices=PROFILE_CHOICES, action="append", default=[])
        self.parser.add_argument("--min-depth", type=int, default=1)
        self.parser.add_argument("--max-depth", type=int, default=6)
        self.parser.add_argument("--query-param", metavar="NAME")
        self.parser.add_argument("--path-segment", action="store_true")
        self.parser.add_argument("--header-value", metavar="HEADER")
        self.parser.add_argument("--post-body", action="store_true")
        self.parser.add_argument("--stop-on-first", action="store_true")
        self.parser.add_argument("--max-findings", type=int)

    def _to_dataclass(self, ns: argparse.Namespace) -> ParsedArgs:
        try:
            targets = self._targets(ns)
            headers = HeaderParser(ns.headers).parse()
            status_codes = HTTPStatusCodesParser(ns.success_statuses or ["200-400"]).parse()
            wordlist = WordListReader(ns.wordlist).read()
        except (OSError, ValueError) as exc:
            self.parser.error(str(exc))

        self._validate(ns, targets)
        return ParsedArgs(
            wordlist=wordlist,
            url=ns.url,
            targets=tuple(targets),
            headers=headers,
            sim_requests=ns.sim_requests,
            payload_place=ns.payload_place,
            status_codes=status_codes,
            verbose=ns.verbose,
            timeout=ns.timeout,
            retries=ns.retries,
            follow_redirects=ns.follow_redirects,
            json_output=ns.json_output,
            output=ns.output,
            profiles=tuple(ns.profile),
            min_depth=ns.min_depth,
            max_depth=ns.max_depth,
            placement_mode=self._placement_mode(ns),
            query_param=ns.query_param,
            header_value=ns.header_value,
            stop_on_first=ns.stop_on_first,
            max_findings=ns.max_findings,
        )

    def _validate(self, ns: argparse.Namespace, targets: list[str]) -> None:
        if not targets:
            self.parser.error("at least one --target or --target-file entry is required")
        if ns.sim_requests <= 0:
            self.parser.error("--simultaneous-requests must be greater than 0")
        if ns.timeout <= 0:
            self.parser.error("--timeout must be greater than 0")
        if ns.retries < 0:
            self.parser.error("--retries must be 0 or greater")
        if ns.min_depth < 0 or ns.max_depth < 0:
            self.parser.error("--min-depth and --max-depth must be 0 or greater")
        if ns.min_depth > ns.max_depth:
            self.parser.error("--min-depth must be less than or equal to --max-depth")
        if ns.max_findings is not None and ns.max_findings <= 0:
            self.parser.error("--max-findings must be greater than 0")
        placement_modes = sum(
            bool(item) for item in (ns.query_param, ns.path_segment, ns.header_value, ns.post_body)
        )
        if placement_modes > 1:
            self.parser.error("choose only one placement helper")
        if placement_modes == 0 and ns.payload_place not in ns.url:
            self.parser.error("URL must contain the payload placeholder")

    def _targets(self, ns: argparse.Namespace) -> list[str]:
        targets = list(ns.target)
        if ns.target_file:
            target_file = Path(ns.target_file)
            targets.extend(
                line.strip()
                for line in target_file.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        return list(dict.fromkeys(targets))

    @staticmethod
    def _placement_mode(ns: argparse.Namespace) -> PlacementMode:
        if ns.query_param:
            return PlacementMode.QUERY_PARAM
        if ns.path_segment:
            return PlacementMode.PATH_SEGMENT
        if ns.header_value:
            return PlacementMode.HEADER_VALUE
        if ns.post_body:
            return PlacementMode.POST_BODY
        return PlacementMode.PLACEHOLDER


def main(argv: list[str] | None = None) -> None:
    args = Parser().parse(argv)
    findings = DeliveryService(args=args).run()
    write_or_print(render_output(findings, args.json_output), args.output)
