"""Truth table generation tests."""

from __future__ import annotations

from boolean_algebra.truth_table import TruthTableGenerator
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser
from utils.binary import int_to_bit_tuple


def build_table(expression: str):
    parser = ExpressionParser()
    generator = TruthTableGenerator(ExpressionEvaluator())
    return generator.generate(parser.parse(expression))


def test_truth_table_uses_canonical_variable_order() -> None:
    table = build_table("c | a")

    assert table.variables == ("a", "c")
    assert tuple(row.inputs for row in table.rows) == ((0, 0), (0, 1), (1, 0), (1, 1))
    assert table.result_vector == (0, 1, 1, 1)
    assert table.minterm_indices == (1, 2, 3)


def test_truth_table_for_constant_expression() -> None:
    table = build_table("1")

    assert table.variables == ()
    assert len(table.rows) == 1
    assert table.rows[0].index == 0
    assert table.rows[0].result == 1


def test_truth_table_indices_follow_binary_order_for_five_variables() -> None:
    table = build_table("a | b | c | d | e")

    assert table.variables == ("a", "b", "c", "d", "e")
    assert tuple(row.index for row in table.rows) == tuple(range(32))
    assert tuple(row.inputs for row in table.rows) == tuple(
        int_to_bit_tuple(index, 5)
        for index in range(32)
    )
    assert table.result_vector[0] == 0
    assert all(value == 1 for value in table.result_vector[1:])
