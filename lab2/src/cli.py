"""Command-line interface for the logic lab."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from typing import TextIO

from boolean_algebra.analyzer import BooleanFunctionAnalyzer
from utils.exceptions import LogicLabError
from utils.reporting import format_report

PromptFunction = Callable[[str], str]


def configure_stdio_streams() -> None:
    """Switch standard streams to UTF-8 when supported."""

    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(description="Boolean algebra laboratory work")
    parser.add_argument(
        "--expr",
        required=False,
        help="Logical expression to analyze. If omitted, the CLI reads from stdin or prompts interactively.",
    )
    return parser


def resolve_expression(
    expression_argument: str | None,
    input_function: PromptFunction = input,
    stdin: TextIO | None = None,
) -> str:
    """Resolve the expression from CLI arguments, piped stdin or prompt."""

    if expression_argument is not None:
        return expression_argument.strip()

    input_stream = stdin or sys.stdin
    isatty = getattr(input_stream, "isatty", None)
    if callable(isatty) and not isatty():
        try:
            piped_expression = input_stream.read().strip()
        except OSError:
            piped_expression = ""
        if piped_expression:
            return piped_expression

    return input_function("> ").strip()


def main(argv: Sequence[str] | None = None, input_function: PromptFunction = input) -> int:
    """CLI entry point."""

    configure_stdio_streams()
    parser = build_argument_parser()
    namespace = parser.parse_args(argv)
    expression = resolve_expression(namespace.expr, input_function=input_function)

    try:
        analyzer = BooleanFunctionAnalyzer()
        report = format_report(analyzer.analyze(expression))
    except LogicLabError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
