"""Post class tests."""

from __future__ import annotations

from boolean_algebra.post_classes import PostClassAnalyzer
from boolean_algebra.truth_table import TruthTableGenerator
from boolean_algebra.zhegalkin import ZhegalkinPolynomialBuilder
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser


def analyze(expression: str):
    parser = ExpressionParser()
    table = TruthTableGenerator(ExpressionEvaluator()).generate(parser.parse(expression))
    polynomial = ZhegalkinPolynomialBuilder().build(table)
    return PostClassAnalyzer().analyze(table, polynomial)


def test_post_classes_for_conjunction() -> None:
    membership = analyze("a & b")

    assert membership.t0 is True
    assert membership.t1 is True
    assert membership.s is False
    assert membership.m is True
    assert membership.l is False


def test_post_classes_for_negation() -> None:
    membership = analyze("!a")

    assert membership.t0 is False
    assert membership.t1 is False
    assert membership.s is True
    assert membership.m is False
    assert membership.l is True


def test_post_classes_for_xor() -> None:
    membership = analyze("(!a & b) | (a & !b)")

    assert membership.t0 is True
    assert membership.t1 is False
    assert membership.s is False
    assert membership.m is False
    assert membership.l is True
