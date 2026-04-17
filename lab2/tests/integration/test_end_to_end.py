"""End-to-end integration tests."""

from __future__ import annotations

from boolean_algebra.analyzer import BooleanFunctionAnalyzer


def test_end_to_end_analysis_for_sample_expression() -> None:
    result = BooleanFunctionAnalyzer().analyze("!(!a -> !b) | c")

    assert result.truth_table.variables == ("a", "b", "c")
    assert result.canonical_forms.numeric_sdnf.startswith("Sigma(")
    assert result.zhegalkin.polynomial
    assert result.dnf_table_method.expression
    assert result.karnaugh_map.dnf_solution is not None


def test_karnaugh_map_is_available_for_five_variables() -> None:
    result = BooleanFunctionAnalyzer().analyze("a | b | c | d | e")

    assert result.truth_table.variables == ("a", "b", "c", "d", "e")
    assert result.karnaugh_map.layer_variables == ("e",)
    assert result.karnaugh_map.dnf_solution is not None
    assert result.karnaugh_map.cnf_solution is not None
    assert "e=0" in result.karnaugh_map.visualization
    assert "e=1" in result.karnaugh_map.visualization
