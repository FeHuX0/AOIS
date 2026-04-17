"""High-level expression analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from app.ast_nodes import Expression
from app.normal_forms import CanonicalForms, build_canonical_forms
from app.numeric_forms import NumericForms, build_numeric_forms
from app.parser import parse_expression
from app.truth_table import TruthTable, build_truth_table


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Full analysis result for a parsed logical expression."""

    source_expression: str
    normalized_expression: Expression
    truth_table: TruthTable
    canonical_forms: CanonicalForms
    numeric_forms: NumericForms


def analyze_expression(expression_text: str) -> AnalysisResult:
    """Parse an expression and build all derived representations."""

    expression = parse_expression(expression_text)
    truth_table = build_truth_table(expression)
    return AnalysisResult(
        source_expression=expression_text,
        normalized_expression=expression,
        truth_table=truth_table,
        canonical_forms=build_canonical_forms(truth_table),
        numeric_forms=build_numeric_forms(truth_table),
    )
