"""AST node definitions for logical expressions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping

from app.exceptions import EvaluationError


class Expression(ABC):
    """Abstract base class for all AST nodes."""

    precedence = 0

    @abstractmethod
    def evaluate(self, variables: Mapping[str, bool]) -> bool:
        """Evaluate the expression for the provided variable values."""

    @abstractmethod
    def to_string(self, parent_precedence: int = 0) -> str:
        """Render the expression in normalized textual form."""

    def __str__(self) -> str:
        return self.to_string()


@dataclass(frozen=True, slots=True)
class Variable(Expression):
    """A boolean variable."""

    name: str
    precedence = 4

    def evaluate(self, variables: Mapping[str, bool]) -> bool:
        """Return the value of the variable from the provided mapping."""

        if self.name not in variables:
            raise EvaluationError(f"Value for variable '{self.name}' is not provided")
        return bool(variables[self.name])

    def to_string(self, parent_precedence: int = 0) -> str:
        """Render the variable name."""

        return self.name


@dataclass(frozen=True, slots=True)
class Not(Expression):
    """Unary negation."""

    operand: Expression
    precedence = 3

    def evaluate(self, variables: Mapping[str, bool]) -> bool:
        """Evaluate the negated operand."""

        return not self.operand.evaluate(variables)

    def to_string(self, parent_precedence: int = 0) -> str:
        """Render the negation with parentheses when required."""

        expression = f"!{self.operand.to_string(self.precedence)}"
        if self.precedence < parent_precedence:
            return f"({expression})"
        return expression


@dataclass(frozen=True, slots=True)
class And(Expression):
    """Binary conjunction."""

    left: Expression
    right: Expression
    precedence = 2

    def evaluate(self, variables: Mapping[str, bool]) -> bool:
        """Evaluate the conjunction."""

        return self.left.evaluate(variables) and self.right.evaluate(variables)

    def to_string(self, parent_precedence: int = 0) -> str:
        """Render the conjunction with precedence-aware parentheses."""

        expression = (
            f"{self.left.to_string(self.precedence)} & "
            f"{self.right.to_string(self.precedence)}"
        )
        if self.precedence < parent_precedence:
            return f"({expression})"
        return expression


@dataclass(frozen=True, slots=True)
class Or(Expression):
    """Binary disjunction."""

    left: Expression
    right: Expression
    precedence = 1

    def evaluate(self, variables: Mapping[str, bool]) -> bool:
        """Evaluate the disjunction."""

        return self.left.evaluate(variables) or self.right.evaluate(variables)

    def to_string(self, parent_precedence: int = 0) -> str:
        """Render the disjunction with precedence-aware parentheses."""

        expression = (
            f"{self.left.to_string(self.precedence)} | "
            f"{self.right.to_string(self.precedence)}"
        )
        if self.precedence < parent_precedence:
            return f"({expression})"
        return expression
