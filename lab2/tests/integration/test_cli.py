"""CLI integration tests."""

from __future__ import annotations

from io import StringIO

import cli
from cli import main, resolve_expression


def test_cli_prints_full_report(capsys) -> None:
    exit_code = main(["--expr", "!(!a -> !b) | c"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Truth table:" in captured.out
    assert "Zhegalkin polynomial:" in captured.out
    assert "Calculation-tabular method (DNF):" in captured.out
    assert "Karnaugh map:" in captured.out
    assert captured.err == ""


def test_cli_reports_errors(capsys) -> None:
    exit_code = main(["--expr", "a ^ b"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Error:" in captured.err


def test_cli_reads_expression_interactively(capsys) -> None:
    exit_code = main([], input_function=lambda _: "a | b")
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Expression: a | b" in captured.out


def test_cli_resolves_expression_from_stdin(monkeypatch) -> None:
    class FakeStdin(StringIO):
        def isatty(self) -> bool:
            return False

    monkeypatch.setattr(cli.sys, "stdin", FakeStdin("\u00aca \u2228 b"))

    assert resolve_expression(None) == "\u00aca \u2228 b"


def test_cli_accepts_symbolic_input_via_stdin(monkeypatch, capsys) -> None:
    class FakeStdin(StringIO):
        def isatty(self) -> bool:
            return False

    monkeypatch.setattr(cli.sys, "stdin", FakeStdin("\u00aca \u2228 b"))

    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Normalized: !a | b" in captured.out
