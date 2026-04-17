"""Parser and tokenizer tests."""

from __future__ import annotations

import pytest

from core.ast.nodes import EquivalentNode, ImpliesNode, OrNode
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser
from utils.exceptions import ParseError, TokenizationError


@pytest.fixture()
def parser() -> ExpressionParser:
    return ExpressionParser()


def test_parser_respects_precedence(parser: ExpressionParser) -> None:
    expression = parser.parse("!a & b | c -> d ~ e")

    assert isinstance(expression, EquivalentNode)
    assert isinstance(expression.left, ImpliesNode)
    assert isinstance(expression.left.left, OrNode)
    assert expression.to_infix() == "!a & b | c -> d ~ e"


def test_parser_supports_symbol_aliases(parser: ExpressionParser) -> None:
    expression = parser.parse("\u00ac(a \u2227 b) \u2228 (c \u2194 d)")

    assert expression.to_infix() == "!(a & b) | (c ~ d)"


def test_implication_is_right_associative(parser: ExpressionParser) -> None:
    expression = parser.parse("a -> b -> c")
    evaluator = ExpressionEvaluator()

    assert evaluator.evaluate(expression, {"a": 0, "b": 1, "c": 0}) is True


def test_constants_are_supported(parser: ExpressionParser) -> None:
    expression = parser.parse("!(1 & 0)")

    assert ExpressionEvaluator().evaluate(expression, {}) is True
    assert expression.to_infix() == "!(1 & 0)"


def test_unknown_variable_raises_error(parser: ExpressionParser) -> None:
    with pytest.raises(TokenizationError):
        parser.parse("x & a")


def test_missing_parenthesis_raises_error(parser: ExpressionParser) -> None:
    with pytest.raises(ParseError):
        parser.parse("!(a | b")
