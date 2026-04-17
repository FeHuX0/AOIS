"""Minimization algorithm tests."""

from __future__ import annotations

from itertools import product

from boolean_algebra.analyzer import BooleanFunctionAnalyzer
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser


def equivalent(left: str, right: str, variables: tuple[str, ...]) -> bool:
    parser = ExpressionParser()
    evaluator = ExpressionEvaluator()
    left_expression = parser.parse(left)
    right_expression = parser.parse(right)
    for bits in product((0, 1), repeat=len(variables)):
        assignment = {variable: bit for variable, bit in zip(variables, bits, strict=True)}
        if evaluator.evaluate(left_expression, assignment) != evaluator.evaluate(right_expression, assignment):
            return False
    return True


def test_minimization_reduces_expression_to_single_variable() -> None:
    result = BooleanFunctionAnalyzer().analyze("a & b | a & !b")

    assert result.dnf_calculation.minimized_expression == "a"
    assert result.dnf_table_method.expression == "a"
    assert result.cnf_table_method.expression == "(a)"
    assert result.karnaugh_map.dnf_solution is not None
    assert result.karnaugh_map.dnf_solution.expression == "a"
    assert equivalent("a & b | a & !b", result.dnf_table_method.expression, ("a", "b"))


def test_prime_implicant_rounds_are_exposed() -> None:
    result = BooleanFunctionAnalyzer().analyze("a & b | a & !b")

    assert result.dnf_calculation.rounds
    assert result.dnf_calculation.rounds[0].combinations
    assert any(implicant.pattern_string() == "1-" for implicant in result.dnf_calculation.prime_implicants)


def test_cnf_and_karnaugh_for_disjunction() -> None:
    result = BooleanFunctionAnalyzer().analyze("a | b")

    assert result.cnf_table_method.expression == "(a | b)"
    assert result.karnaugh_map.cnf_solution is not None
    assert result.karnaugh_map.cnf_solution.expression == "(a | b)"


def test_five_variable_karnaugh_map_supports_cross_layer_grouping() -> None:
    expression = "(a & b & c & d & !e) | (a & b & c & d & e)"
    result = BooleanFunctionAnalyzer().analyze(expression)

    assert result.truth_table.variables == ("a", "b", "c", "d", "e")
    assert result.karnaugh_map.layer_variables == ("e",)
    assert result.karnaugh_map.row_variables == ("a", "b")
    assert result.karnaugh_map.column_variables == ("c", "d")
    assert result.karnaugh_map.dnf_solution is not None
    assert result.karnaugh_map.dnf_solution.expression == "(a & b & c & d)"
    assert any(len(group.cells) == 2 for group in result.karnaugh_map.dnf_solution.groups)
    assert equivalent(expression, result.karnaugh_map.dnf_solution.expression, ("a", "b", "c", "d", "e"))


def test_five_variable_karnaugh_map_produces_equivalent_cnf_and_dnf() -> None:
    expression = "e | (a & b & (c | !c) & (d | !d))"
    result = BooleanFunctionAnalyzer().analyze(expression)

    assert result.karnaugh_map.dnf_solution is not None
    assert result.karnaugh_map.cnf_solution is not None
    assert "e=0" in result.karnaugh_map.visualization
    assert "e=1" in result.karnaugh_map.visualization
    assert equivalent(expression, result.karnaugh_map.dnf_solution.expression, ("a", "b", "c", "d", "e"))
    assert equivalent(expression, result.karnaugh_map.cnf_solution.expression, ("a", "b", "c", "d", "e"))
