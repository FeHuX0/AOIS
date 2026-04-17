"""Truth table generation."""

from __future__ import annotations

from itertools import product

from core.ast.nodes import ExpressionNode
from core.evaluator.expression_evaluator import ExpressionEvaluator
from models.truth_table import TruthTable, TruthTableRow
from utils import ALLOWED_VARIABLES, ValidationError, bit_tuple_to_int


class TruthTableGenerator:
    """Generate truth tables for boolean expressions."""

    def __init__(self, evaluator: ExpressionEvaluator | None = None) -> None:
        self._evaluator = evaluator or ExpressionEvaluator()

    def generate(self, expression: ExpressionNode) -> TruthTable:
        """Generate the truth table in canonical order."""

        variables = tuple(variable for variable in ALLOWED_VARIABLES if variable in expression.variables())
        if len(variables) > len(ALLOWED_VARIABLES):
            raise ValidationError("At most five variables are supported")

        if not variables:
            result = int(self._evaluator.evaluate(expression, {}))
            return TruthTable(variables=(), rows=(TruthTableRow(index=0, inputs=(), result=result),))

        rows: list[TruthTableRow] = []
        for bits in product((0, 1), repeat=len(variables)):
            assignment = {name: bool(value) for name, value in zip(variables, bits, strict=True)}
            result = int(self._evaluator.evaluate(expression, assignment))
            rows.append(TruthTableRow(index=bit_tuple_to_int(bits), inputs=bits, result=result))
        return TruthTable(variables=variables, rows=tuple(rows))
