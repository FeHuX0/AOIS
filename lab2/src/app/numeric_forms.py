"""Numeric and index forms derived from a truth table."""

from __future__ import annotations

from dataclasses import dataclass

from app.truth_table import TruthTable

EMPTY_SET = "∅"


@dataclass(frozen=True, slots=True)
class NumericForms:
    """Numeric forms and index representation of the function."""

    minterm_indices: tuple[int, ...]
    maxterm_indices: tuple[int, ...]
    sigma_form: str
    pi_form: str
    index_bits: str
    index_value: int


def format_index_list(indices: tuple[int, ...]) -> str:
    """Render a tuple of indices as comma-separated text or the empty-set marker."""

    if not indices:
        return EMPTY_SET
    return ", ".join(str(index) for index in indices)


def build_numeric_forms(table: TruthTable) -> NumericForms:
    """Build numeric SDNF/SKNF forms and the decimal index of the function."""

    minterm_indices = table.minterm_indices()
    maxterm_indices = table.maxterm_indices()
    index_bits = "".join(str(bit) for bit in table.result_vector())

    return NumericForms(
        minterm_indices=minterm_indices,
        maxterm_indices=maxterm_indices,
        sigma_form=f"Σ({format_index_list(minterm_indices)})",
        pi_form=f"Π({format_index_list(maxterm_indices)})",
        index_bits=index_bits,
        index_value=int(index_bits, 2),
    )
