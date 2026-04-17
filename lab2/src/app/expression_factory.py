"""Factories for building logical expression AST nodes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.ast_nodes import And, Expression, Not, Or, Variable


class ExpressionFactory(Protocol):
    """Factory protocol used by the parser to create AST nodes."""

    def create_variable(self, name: str) -> Expression:
        """Create a variable node."""

    def create_not(self, operand: Expression) -> Expression:
        """Create a negation node."""

    def create_and(self, left: Expression, right: Expression) -> Expression:
        """Create a conjunction node."""

    def create_or(self, left: Expression, right: Expression) -> Expression:
        """Create a disjunction node."""


@dataclass(frozen=True, slots=True)
class DefaultExpressionFactory:
    """Default AST factory used in production code."""

    def create_variable(self, name: str) -> Expression:
        """Create a variable node."""

        return Variable(name)

    def create_not(self, operand: Expression) -> Expression:
        """Create a negation node."""

        return Not(operand)

    def create_and(self, left: Expression, right: Expression) -> Expression:
        """Create a conjunction node."""

        return And(left, right)

    def create_or(self, left: Expression, right: Expression) -> Expression:
        """Create a disjunction node."""

        return Or(left, right)
