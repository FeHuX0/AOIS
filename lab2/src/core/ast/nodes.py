"""AST node definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping

from utils.exceptions import EvaluationError

Assignment = Mapping[str, bool]


class ExpressionNode(ABC):
    """Base class for every AST node."""

    precedence = 0

    @abstractmethod
    def evaluate(self, assignment: Assignment) -> bool:
        """Evaluate the expression."""

    @abstractmethod
    def variables(self) -> frozenset[str]:
        """Return variable names used by the expression."""

    @abstractmethod
    def to_infix(self, parent_precedence: int = 0) -> str:
        """Render the expression in infix notation."""

    def __str__(self) -> str:
        return self.to_infix()


@dataclass(frozen=True, slots=True)
class ConstantNode(ExpressionNode):
    """Boolean constant."""

    value: bool
    precedence = 6

    def evaluate(self, assignment: Assignment) -> bool:
        return self.value

    def variables(self) -> frozenset[str]:
        return frozenset()

    def to_infix(self, parent_precedence: int = 0) -> str:
        return "1" if self.value else "0"


@dataclass(frozen=True, slots=True)
class VariableNode(ExpressionNode):
    """Boolean variable."""

    name: str
    precedence = 6

    def evaluate(self, assignment: Assignment) -> bool:
        if self.name not in assignment:
            raise EvaluationError(f"Missing value for variable '{self.name}'")
        return bool(assignment[self.name])

    def variables(self) -> frozenset[str]:
        return frozenset({self.name})

    def to_infix(self, parent_precedence: int = 0) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class NotNode(ExpressionNode):
    """Logical negation."""

    operand: ExpressionNode
    precedence = 5

    def evaluate(self, assignment: Assignment) -> bool:
        return not self.operand.evaluate(assignment)

    def variables(self) -> frozenset[str]:
        return self.operand.variables()

    def to_infix(self, parent_precedence: int = 0) -> str:
        rendered = f"!{self.operand.to_infix(self.precedence)}"
        if self.precedence < parent_precedence:
            return f"({rendered})"
        return rendered


class BinaryNode(ExpressionNode):
    """Shared behavior for binary operations."""

    symbol = "?"
    precedence = 0
    right_associative = False
    associative = False

    def __init__(self, left: ExpressionNode, right: ExpressionNode) -> None:
        self.left = left
        self.right = right

    def variables(self) -> frozenset[str]:
        return self.left.variables() | self.right.variables()

    def to_infix(self, parent_precedence: int = 0) -> str:
        left_precedence = self.precedence + 1 if self.right_associative else self.precedence
        right_precedence = self.precedence if self.right_associative or self.associative else self.precedence + 1
        rendered = (
            f"{self.left.to_infix(left_precedence)} "
            f"{self.symbol} "
            f"{self.right.to_infix(right_precedence)}"
        )
        if self.precedence < parent_precedence:
            return f"({rendered})"
        return rendered

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.left!r}, {self.right!r})"


class AndNode(BinaryNode):
    """Logical conjunction."""

    symbol = "&"
    precedence = 4
    associative = True

    def evaluate(self, assignment: Assignment) -> bool:
        return self.left.evaluate(assignment) and self.right.evaluate(assignment)


class OrNode(BinaryNode):
    """Logical disjunction."""

    symbol = "|"
    precedence = 3
    associative = True

    def evaluate(self, assignment: Assignment) -> bool:
        return self.left.evaluate(assignment) or self.right.evaluate(assignment)


class ImpliesNode(BinaryNode):
    """Logical implication."""

    symbol = "->"
    precedence = 2
    right_associative = True

    def evaluate(self, assignment: Assignment) -> bool:
        return (not self.left.evaluate(assignment)) or self.right.evaluate(assignment)


class EquivalentNode(BinaryNode):
    """Logical equivalence."""

    symbol = "~"
    precedence = 1
    associative = True

    def evaluate(self, assignment: Assignment) -> bool:
        return self.left.evaluate(assignment) == self.right.evaluate(assignment)
