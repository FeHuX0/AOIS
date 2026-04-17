"""Tests for truth table generation."""

from __future__ import annotations

from app.parser import parse_expression
from app.truth_table import build_truth_table


def test_truth_table_uses_canonical_row_order() -> None:
    table = build_truth_table(parse_expression("x1 & x2 | x3"))
    assert [row.bits for row in table.rows] == [
        (0, 0, 0),
        (0, 0, 1),
        (0, 1, 0),
        (0, 1, 1),
        (1, 0, 0),
        (1, 0, 1),
        (1, 1, 0),
        (1, 1, 1),
    ]
    assert table.result_vector() == (0, 1, 0, 1, 0, 1, 1, 1)


def test_truth_table_exposes_row_indices_and_assignments() -> None:
    table = build_truth_table(parse_expression("x1 & x2 | x3"))
    assert table.rows[0].index == 0
    assert table.rows[0].assignment == {"x1": False, "x2": False, "x3": False}
    assert table.minterm_indices() == (1, 3, 5, 6, 7)
    assert table.maxterm_indices() == (0, 2, 4)
