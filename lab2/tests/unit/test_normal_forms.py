"""Canonical form tests."""

from __future__ import annotations

from boolean_algebra.normal_forms import CanonicalFormBuilder
from boolean_algebra.truth_table import TruthTableGenerator
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser


def build_forms(expression: str):
    parser = ExpressionParser()
    table = TruthTableGenerator(ExpressionEvaluator()).generate(parser.parse(expression))
    return CanonicalFormBuilder().build(table)


def test_canonical_forms_for_conjunction() -> None:
    forms = build_forms("a & b")

    assert forms.sdnf == "(a & b)"
    assert forms.sknf == "(a | b) & (a | !b) & (!a | b)"
    assert forms.numeric_sdnf == "Sigma(3)"
    assert forms.numeric_sknf == "Pi(0, 1, 2)"
    assert forms.index_form.notation == "f = 0001_2 = 1_10"


def test_constant_zero_has_degenerate_forms() -> None:
    forms = build_forms("0")

    assert forms.sdnf == "0"
    assert forms.sknf == "0"
    assert forms.numeric_sdnf == "Sigma(empty)"
    assert forms.numeric_sknf == "Pi(0)"
    assert forms.index_form.bits == "0"


def test_numeric_forms_and_index_form_match_three_variable_function() -> None:
    forms = build_forms("(a & !b) | c")

    assert forms.sdnf == (
        "(!a & !b & c) | (!a & b & c) | (a & !b & !c) | (a & !b & c) | (a & b & c)"
    )
    assert forms.sknf == "(a | b | c) & (a | !b | c) & (!a | !b | c)"
    assert forms.numeric_sdnf == "Sigma(1, 3, 4, 5, 7)"
    assert forms.numeric_sknf == "Pi(0, 2, 6)"
    assert forms.index_form.notation == "f = 01011101_2 = 93_10"
