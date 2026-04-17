"""Canonical SDNF and SKNF construction."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.evaluator import BitTuple, VARIABLE_NAMES
from app.truth_table import TruthTable


@dataclass(frozen=True, slots=True)
class CanonicalForms:
    """Canonical forms derived from a truth table."""

    sdnf: str
    sknf: str
    minterm_indices: tuple[int, ...]
    maxterm_indices: tuple[int, ...]


def _build_constituent(
    bits: BitTuple,
    joiner: str,
    negate_when: int,
) -> str:
    """Build a canonical constituent using the provided negation rule."""

    literals = [
        f"!{name}" if value == negate_when else name
        for name, value in zip(VARIABLE_NAMES, bits, strict=True)
    ]
    return f"({joiner.join(literals)})"


def build_constituent_of_one(bits: BitTuple) -> str:
    """Build a minterm for the provided variable values."""

    return _build_constituent(bits, " & ", negate_when=0)


def build_constituent_of_zero(bits: BitTuple) -> str:
    """Build a maxterm for the provided variable values."""

    return _build_constituent(bits, " | ", negate_when=1)


def _build_canonical_form(
    table: TruthTable,
    value: int,
    term_builder: Callable[[BitTuple], str],
    empty_value: str,
    joiner: str,
) -> str:
    """Build a canonical form by filtering table rows for the requested value."""

    terms = [term_builder(row.bits) for row in table.rows if row.result == value]
    if not terms:
        return empty_value
    return joiner.join(terms)


def build_sdnf(table: TruthTable) -> str:
    """Build the canonical SDNF from the truth table."""

    return _build_canonical_form(table, 1, build_constituent_of_one, "0", " | ")


def build_sknf(table: TruthTable) -> str:
    """Build the canonical SKNF from the truth table."""

    return _build_canonical_form(table, 0, build_constituent_of_zero, "1", " & ")


def build_canonical_forms(table: TruthTable) -> CanonicalForms:
    """Build both canonical forms and the corresponding row index lists."""

    return CanonicalForms(
        sdnf=build_sdnf(table),
        sknf=build_sknf(table),
        minterm_indices=table.minterm_indices(),
        maxterm_indices=table.maxterm_indices(),
    )
