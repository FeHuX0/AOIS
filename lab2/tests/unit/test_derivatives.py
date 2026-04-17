"""Boolean derivative tests."""

from __future__ import annotations

from itertools import product

from boolean_algebra.analyzer import BooleanFunctionAnalyzer
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser


def test_partial_and_mixed_derivatives() -> None:
    result = BooleanFunctionAnalyzer().analyze("a & b")
    partial = {derivative.variables: derivative.expression for derivative in result.derivatives.partial}
    mixed = {derivative.variables: derivative.expression for derivative in result.derivatives.mixed}

    assert partial[("a",)] == "(b)"
    assert partial[("b",)] == "(a)"
    assert mixed[("a", "b")] == "1"
    assert result.derivatives.fictitious_variables == ()


def test_fictitious_variable_is_detected() -> None:
    result = BooleanFunctionAnalyzer().analyze("a | (b & !b)")
    partial = {derivative.variables: derivative.expression for derivative in result.derivatives.partial}

    assert partial[("b",)] == "0"
    assert result.derivatives.fictitious_variables == ("b",)


def test_partial_derivatives_follow_definition_for_five_variables() -> None:
    expression = "(a & b) | (!c & d) | e"
    result = BooleanFunctionAnalyzer().analyze(expression)
    parser = ExpressionParser()
    evaluator = ExpressionEvaluator()
    parsed_expression = parser.parse(expression)

    for derivative in result.derivatives.partial:
        variable = derivative.variables[0]
        variable_index = result.truth_table.variables.index(variable)
        expected_values: list[int] = []
        for bits in product((0, 1), repeat=len(derivative.truth_table.variables)):
            left_bits = bits[:variable_index] + (0,) + bits[variable_index:]
            right_bits = bits[:variable_index] + (1,) + bits[variable_index:]
            left_assignment = dict(zip(result.truth_table.variables, left_bits, strict=True))
            right_assignment = dict(zip(result.truth_table.variables, right_bits, strict=True))
            expected_values.append(
                int(
                    evaluator.evaluate(parsed_expression, left_assignment)
                    ^ evaluator.evaluate(parsed_expression, right_assignment)
                )
            )

        assert derivative.truth_table.result_vector == tuple(expected_values)


def test_mixed_derivatives_match_sequential_boolean_differentiation() -> None:
    expression = "(a & b) | (!c & d) | e"
    result = BooleanFunctionAnalyzer().analyze(expression)
    parser = ExpressionParser()
    evaluator = ExpressionEvaluator()
    parsed_expression = parser.parse(expression)
    derivatives = {
        derivative.variables: derivative
        for derivative in result.derivatives.partial + result.derivatives.mixed
    }

    for variables in (("a", "b"), ("a", "c", "e"), ("b", "d", "e")):
        derivative = derivatives[variables]
        remaining_variables = derivative.truth_table.variables
        expected_values: list[int] = []
        for bits in product((0, 1), repeat=len(remaining_variables)):
            base_assignment = dict(zip(remaining_variables, bits, strict=True))
            derivative_value = 0
            for toggles in product((0, 1), repeat=len(variables)):
                assignment = base_assignment | dict(zip(variables, toggles, strict=True))
                derivative_value ^= int(evaluator.evaluate(parsed_expression, assignment))
            expected_values.append(derivative_value)

        assert derivative.truth_table.result_vector == tuple(expected_values)
