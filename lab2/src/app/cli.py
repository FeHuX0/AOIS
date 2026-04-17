"""Command-line interface for the logic algebra laboratory work."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

from app.analysis import analyze_expression as build_analysis_result
from app.exceptions import LogicLabError
from app.formatter import format_report

PromptFunction = Callable[[str], str]


@dataclass(frozen=True, slots=True)
class CliArguments:
    """Parsed CLI arguments."""

    expression: str | None


def analyze_expression(expression_text: str) -> str:
    """Parse, evaluate and format the full report for the given expression."""

    return format_report(build_analysis_result(expression_text))


def configure_output_streams() -> None:
    """Switch stdout and stderr to UTF-8 when the current streams support it."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description="Analyze a logical expression over variables x1, x2, x3.",
    )
    parser.add_argument(
        "--expr",
        required=False,
        help="Logical expression to analyze. If omitted, the CLI will ask for it interactively.",
    )
    return parser


def parse_cli_arguments(argv: Sequence[str] | None = None) -> CliArguments:
    """Parse raw CLI arguments into a typed structure."""

    parser = build_argument_parser()
    namespace = parser.parse_args(argv)
    return CliArguments(expression=namespace.expr)


def prompt_for_expression(input_function: PromptFunction = input) -> str:
    """Request a logical expression from the user."""

    return input_function("Введите логическую формулу: ").strip()


def resolve_expression(
    arguments: CliArguments,
    input_function: PromptFunction = input,
) -> str:
    """Resolve the expression from CLI arguments or interactive input."""

    if arguments.expression is not None:
        return arguments.expression
    return prompt_for_expression(input_function)


def main(
    argv: Sequence[str] | None = None,
    input_function: PromptFunction = input,
) -> int:
    """CLI entry point."""

    configure_output_streams()
    arguments = parse_cli_arguments(argv)

    try:
        report = analyze_expression(resolve_expression(arguments, input_function))
    except LogicLabError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
