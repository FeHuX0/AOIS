"""Tests for numeric and index forms."""

from __future__ import annotations

from app.numeric_forms import build_numeric_forms, format_index_list
from app.parser import parse_expression
from app.truth_table import build_truth_table


def test_numeric_forms_include_sigma_pi_and_index() -> None:
    numeric_forms = build_numeric_forms(build_truth_table(parse_expression("x1 | x3")))
    assert numeric_forms.minterm_indices == (1, 3, 4, 5, 6, 7)
    assert numeric_forms.maxterm_indices == (0, 2)
    assert numeric_forms.sigma_form == "Σ(1, 3, 4, 5, 6, 7)"
    assert numeric_forms.pi_form == "Π(0, 2)"
    assert numeric_forms.index_bits == "01011111"
    assert numeric_forms.index_value == 95


def test_numeric_forms_handle_empty_set_marker() -> None:
    numeric_forms = build_numeric_forms(build_truth_table(parse_expression("x1 & !x1")))
    assert format_index_list(()) == "∅"
    assert numeric_forms.sigma_form == "Σ(∅)"
    assert numeric_forms.index_bits == "00000000"
    assert numeric_forms.index_value == 0
