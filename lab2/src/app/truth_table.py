"""Truth table generation for expressions over x1, x2, x3."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from app.ast_nodes import Expression
from app.evaluator import BitTuple, build_assignment, evaluate_expression


@dataclass(frozen=True, slots=True)
class TruthTableRow:
    """One row of a truth table."""

    index: int
    bits: BitTuple
    result: int

    @property
    def assignment(self) -> dict[str, bool]:
        """Return the row as a boolean assignment mapping."""

        return build_assignment(self.bits)


@dataclass(frozen=True, slots=True)
class TruthTable:
    """Truth table for a logical expression."""

    rows: tuple[TruthTableRow, ...]

    def indices_for_value(self, value: int) -> tuple[int, ...]:
        """Return row indices for the requested function value."""

        return tuple(row.index for row in self.rows if row.result == value)

    def result_vector(self) -> tuple[int, ...]:
        """Return the function values ordered by set index 0..7."""

        return tuple(row.result for row in self.rows)

    def minterm_indices(self) -> tuple[int, ...]:
        """Return the indices of rows where the function equals one."""

        return self.indices_for_value(1)

    def maxterm_indices(self) -> tuple[int, ...]:
        """Return the indices of rows where the function equals zero."""

        return self.indices_for_value(0)


def bits_to_index(bits: BitTuple) -> int:
    """Convert a variable tuple x1x2x3 to its canonical row index."""

    x1, x2, x3 = bits
    return x1 * 4 + x2 * 2 + x3


def build_truth_table(expression: Expression) -> TruthTable:
    """Evaluate the expression for all variable combinations in canonical order."""

    rows = []
    for bits in product((0, 1), repeat=3):
        assignment = build_assignment(bits)
        result = evaluate_expression(expression, assignment)
        rows.append(TruthTableRow(index=bits_to_index(bits), bits=bits, result=result))
    return TruthTable(rows=tuple(rows))


__all__ = ["TruthTable", "TruthTableRow", "bits_to_index", "build_truth_table"]
