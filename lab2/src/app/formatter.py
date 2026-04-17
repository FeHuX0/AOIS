"""Formatting utilities for CLI output."""

from __future__ import annotations

from app.analysis import AnalysisResult
from app.numeric_forms import format_index_list
from app.truth_table import TruthTable


def format_truth_table(table: TruthTable) -> str:
    """Format the truth table as aligned plain text."""

    lines = [
        "j | x1 | x2 | x3 | f",
        "--+----+----+----+--",
    ]

    for row in table.rows:
        x1, x2, x3 = row.bits
        lines.append(f"{row.index} |  {x1} |  {x2} |  {x3} | {row.result}")

    return "\n".join(lines)


def format_report(result: AnalysisResult) -> str:
    """Format the full analysis report for CLI output."""

    return "\n".join(
        [
            f"Исходная формула: {result.source_expression}",
            f"Нормализованная форма: {result.normalized_expression}",
            "",
            "Таблица истинности:",
            format_truth_table(result.truth_table),
            "",
            f"СДНФ: {result.canonical_forms.sdnf}",
            f"Наборы, где f=1: {format_index_list(result.canonical_forms.minterm_indices)}",
            f"СКНФ: {result.canonical_forms.sknf}",
            f"Наборы, где f=0: {format_index_list(result.canonical_forms.maxterm_indices)}",
            "",
            "Числовая форма:",
            result.numeric_forms.sigma_form,
            result.numeric_forms.pi_form,
            "",
            "Индексная форма:",
            f"f = {result.numeric_forms.index_bits}_2 = {result.numeric_forms.index_value}_10",
        ]
    )
