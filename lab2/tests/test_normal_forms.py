"""Tests for SDNF and SKNF construction."""

from __future__ import annotations

from app.normal_forms import (
    build_canonical_forms,
    build_constituent_of_one,
    build_constituent_of_zero,
)
from app.parser import parse_expression
from app.truth_table import build_truth_table


def test_constituent_builders_follow_canonical_rules() -> None:
    assert build_constituent_of_one((0, 1, 0)) == "(!x1 & x2 & !x3)"
    assert build_constituent_of_zero((1, 0, 1)) == "(!x1 | x2 | !x3)"


def test_build_sdnf_for_single_true_row() -> None:
    forms = build_canonical_forms(build_truth_table(parse_expression("x1 & x2 & x3")))
    assert forms.sdnf == "(x1 & x2 & x3)"
    assert forms.minterm_indices == (7,)


def test_build_sknf_for_single_false_row() -> None:
    forms = build_canonical_forms(build_truth_table(parse_expression("x1 | x2 | x3")))
    assert forms.sknf == "(x1 | x2 | x3)"
    assert forms.maxterm_indices == (0,)


def test_build_canonical_forms_for_constant_false_expression() -> None:
    forms = build_canonical_forms(build_truth_table(parse_expression("x1 & !x1")))
    assert forms.sdnf == "0"
    assert forms.minterm_indices == ()
    assert forms.maxterm_indices == tuple(range(8))
