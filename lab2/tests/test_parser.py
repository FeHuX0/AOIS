"""Tests for the parser."""

from __future__ import annotations

import pytest

from app.evaluator import evaluate_expression
from app.exceptions import MissingParenthesisError, TrailingTokensError, UnexpectedTokenError
from app.parser import parse_expression


def test_parser_respects_operator_precedence() -> None:
    expression = parse_expression("!x1 | x2 & x3")
    assert str(expression) == "!x1 | x2 & x3"
    assert evaluate_expression(expression, {"x1": 0, "x2": 0, "x3": 0}) == 1


def test_parser_normalizes_alternative_not_and_or_symbols() -> None:
    expression = parse_expression("~(x1 + x2) * x3")
    assert str(expression) == "!(x1 | x2) & x3"


def test_parser_keeps_nested_negations() -> None:
    expression = parse_expression("!!x1")
    assert str(expression) == "!!x1"


def test_parser_reports_missing_parenthesis() -> None:
    with pytest.raises(MissingParenthesisError):
        parse_expression("!(x1 | x2")


def test_parser_reports_invalid_operator_order() -> None:
    with pytest.raises(UnexpectedTokenError):
        parse_expression("x1 | | x2")


def test_parser_reports_trailing_tokens() -> None:
    with pytest.raises(TrailingTokensError):
        parse_expression("x1 x2")
