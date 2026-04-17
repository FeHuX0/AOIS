"""Tests for the command-line interface."""

from __future__ import annotations

from types import SimpleNamespace

from app.cli import (
    analyze_expression,
    configure_output_streams,
    main,
    parse_cli_arguments,
    resolve_expression,
)


def test_analyze_expression_contains_all_main_sections() -> None:
    report = analyze_expression("!(x1 & x2) | x3")
    assert "Исходная формула: !(x1 & x2) | x3" in report
    assert "Нормализованная форма: !(x1 & x2) | x3" in report
    assert "Таблица истинности:" in report
    assert "СДНФ:" in report
    assert "СКНФ:" in report
    assert "Σ(" in report
    assert "Π(" in report
    assert "Индексная форма:" in report


def test_cli_main_prints_report(capsys) -> None:
    exit_code = main(["--expr", "x1 & x2"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Таблица истинности:" in captured.out
    assert captured.err == ""


def test_cli_main_reports_domain_errors(capsys) -> None:
    exit_code = main(["--expr", "x1 ^ x2"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Ошибка:" in captured.err


def test_cli_main_reads_expression_interactively(capsys) -> None:
    exit_code = main([], input_function=lambda _: "x1 | x2")
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Исходная формула: x1 | x2" in captured.out


def test_parse_cli_arguments_and_resolve_expression() -> None:
    arguments = parse_cli_arguments([])

    resolved = resolve_expression(arguments, input_function=lambda _: "x1 & x3")

    assert resolved == "x1 & x3"


def test_configure_output_streams_reconfigures_utf8(monkeypatch) -> None:
    calls: list[str] = []

    def reconfigure(*, encoding: str) -> None:
        calls.append(encoding)

    fake_stream = SimpleNamespace(reconfigure=reconfigure)
    monkeypatch.setattr("sys.stdout", fake_stream)
    monkeypatch.setattr("sys.stderr", fake_stream)

    configure_output_streams()

    assert calls == ["utf-8", "utf-8"]
