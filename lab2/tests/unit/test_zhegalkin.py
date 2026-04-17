"""Zhegalkin polynomial tests."""

from __future__ import annotations

from boolean_algebra.truth_table import TruthTableGenerator
from boolean_algebra.zhegalkin import ZhegalkinPolynomialBuilder
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser


def build_polynomial(expression: str) -> str:
    table = TruthTableGenerator(ExpressionEvaluator()).generate(ExpressionParser().parse(expression))
    return ZhegalkinPolynomialBuilder().build(table).polynomial


def test_zhegalkin_for_or() -> None:
    assert build_polynomial("a | b") == "b xor a xor a*b"


def test_zhegalkin_for_equivalence() -> None:
    assert build_polynomial("a ~ b") == "1 xor b xor a"


def test_zhegalkin_for_majority_of_three() -> None:
    assert build_polynomial("(a & b) | (a & c) | (b & c)") == "b*c xor a*c xor a*b"
