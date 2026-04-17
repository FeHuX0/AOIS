"""Tests for the AST factory integration."""

from __future__ import annotations

from app.ast_nodes import Expression
from app.expression_factory import DefaultExpressionFactory
from app.parser import parse_expression


class RecordingFactory:
    """Factory that records method calls made by the parser."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.factory = DefaultExpressionFactory()

    def create_variable(self, name: str) -> Expression:
        self.calls.append(f"var:{name}")
        return self.factory.create_variable(name)

    def create_not(self, operand: Expression) -> Expression:
        self.calls.append("not")
        return self.factory.create_not(operand)

    def create_and(self, left: Expression, right: Expression) -> Expression:
        self.calls.append("and")
        return self.factory.create_and(left, right)

    def create_or(self, left: Expression, right: Expression) -> Expression:
        self.calls.append("or")
        return self.factory.create_or(left, right)


def test_parser_builds_ast_through_factory() -> None:
    factory = RecordingFactory()

    expression = parse_expression("!(x1 & x2) | x3", factory=factory)

    assert str(expression) == "!(x1 & x2) | x3"
    assert factory.calls == ["var:x1", "var:x2", "and", "not", "var:x3", "or"]
