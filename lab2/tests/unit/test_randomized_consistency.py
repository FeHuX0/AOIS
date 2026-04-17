"""Randomized consistency tests."""

from __future__ import annotations

import random
from itertools import product

from boolean_algebra.analyzer import BooleanFunctionAnalyzer
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser

VARIABLES = ("a", "b", "c", "d", "e")
BINARY_OPERATORS = ("&", "|", "->", "~")


def build_random_expression(rng: random.Random, variables: tuple[str, ...], depth: int) -> str:
    if depth == 0 or rng.random() < 0.3:
        atom = rng.choice(variables + ("0", "1"))
        return f"!{atom}" if atom in variables and rng.random() < 0.2 else atom
    if rng.random() < 0.25:
        return f"!({build_random_expression(rng, variables, depth - 1)})"
    left = build_random_expression(rng, variables, depth - 1)
    right = build_random_expression(rng, variables, depth - 1)
    operator = rng.choice(BINARY_OPERATORS)
    return f"({left} {operator} {right})"


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


def test_randomized_forms_and_minimizations_remain_equivalent() -> None:
    rng = random.Random(42)
    analyzer = BooleanFunctionAnalyzer()

    for _ in range(20):
        variable_count = rng.randint(1, 5)
        variables = VARIABLES[:variable_count]
        expression = build_random_expression(rng, variables, depth=3)
        result = analyzer.analyze(expression)

        assert equivalent(expression, result.canonical_forms.sdnf, variables)
        assert equivalent(expression, result.canonical_forms.sknf, variables)
        assert equivalent(expression, result.dnf_table_method.expression, variables)
        assert equivalent(expression, result.cnf_table_method.expression, variables)
        if result.karnaugh_map.dnf_solution is not None:
            assert equivalent(expression, result.karnaugh_map.dnf_solution.expression, variables)
        if result.karnaugh_map.cnf_solution is not None:
            assert equivalent(expression, result.karnaugh_map.cnf_solution.expression, variables)
