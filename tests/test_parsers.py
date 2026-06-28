import pytest

from traverser.parsers import HeaderParser, HTTPStatusCodesParser, WordListReader


def test_header_parser_allows_colons_in_values() -> None:
    assert HeaderParser(["Authorization: Bearer a:b:c"]).parse() == {
        "Authorization": "Bearer a:b:c"
    }


def test_header_parser_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="header name"):
        HeaderParser([": value"]).parse()


def test_status_parser_handles_ranges_and_single_values() -> None:
    assert HTTPStatusCodesParser(["200-203", "302"]).parse() == {200, 201, 202, 302}


@pytest.mark.parametrize("status", ["99", "600", "abc", "300-200"])
def test_status_parser_rejects_invalid_values(status: str) -> None:
    with pytest.raises(ValueError):
        HTTPStatusCodesParser([status]).parse()


def test_wordlist_reader_skips_blank_lines(tmp_path) -> None:
    wordlist = tmp_path / "payloads.txt"
    wordlist.write_text("../\n\n..\\\n", encoding="utf-8")

    assert WordListReader(str(wordlist)).read() == ["../", "..\\"]
