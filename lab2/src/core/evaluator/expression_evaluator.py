"""Expression evaluation service."""

from __future__ import annotations

from typing import Mapping

from core.ast.nodes import ExpressionNode


class ExpressionEvaluator:
    """Evaluate logical expressions against variable assignments."""

    def evaluate(self, expression: ExpressionNode, assignment: Mapping[str, bool | int]) -> bool:
        """Evaluate an AST expression."""

        normalized = {name: bool(value) for name, value in assignment.items()}
        return expression.evaluate(normalized)
