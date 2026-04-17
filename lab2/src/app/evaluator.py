"""Expression evaluation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, TypeAlias

from app.ast_nodes import Expression

Bit: TypeAlias = Literal[0, 1]
BitTuple: TypeAlias = tuple[Bit, Bit, Bit]
VARIABLE_NAMES = ("x1", "x2", "x3")


def build_assignment(bits: BitTuple) -> dict[str, bool]:
    """Build a variable assignment mapping from a tuple of bits."""

    return {name: bool(value) for name, value in zip(VARIABLE_NAMES, bits, strict=True)}


def evaluate_expression(expression: Expression, variables: Mapping[str, int | bool]) -> int:
    """Evaluate an expression and return the result as 0 or 1."""

    normalized_variables = {name: bool(value) for name, value in variables.items()}
    return int(expression.evaluate(normalized_variables))
