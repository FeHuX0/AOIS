"""Tests for expression evaluation."""

from __future__ import annotations

import pytest

from app.ast_nodes import And, Not, Or, Variable
from app.evaluator import build_assignment, evaluate_expression
from app.exceptions import EvaluationError
from app.parser import parse_expression


def test_build_assignment_maps_bits_to_variable_names() -> None:
    assert build_assignment((1, 0, 1)) == {"x1": True, "x2": False, "x3": True}


def test_evaluate_nested_expression() -> None:
    expression = parse_expression("!(x1 & x2) | x3")
    assert evaluate_expression(expression, {"x1": 1, "x2": 1, "x3": 0}) == 0
    assert evaluate_expression(expression, {"x1": 1, "x2": 0, "x3": 0}) == 1


def test_manual_ast_evaluation_and_pretty_print() -> None:
    expression = Or(And(Variable("x1"), Not(Variable("x2"))), Variable("x3"))
    assert str(expression) == "x1 & !x2 | x3"
    assert evaluate_expression(expression, {"x1": 1, "x2": 0, "x3": 0}) == 1


def test_variable_requires_assignment() -> None:
    with pytest.raises(EvaluationError):
        evaluate_expression(Variable("x1"), {"x2": 1, "x3": 0})
