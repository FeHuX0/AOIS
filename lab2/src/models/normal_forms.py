"""Canonical and numeric form models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IndexForm:
    """Index representation of a boolean function."""

    bits: str
    value: int

    @property
    def notation(self) -> str:
        """Return a human-readable index notation."""

        return f"f = {self.bits}_2 = {self.value}_10"


@dataclass(frozen=True, slots=True)
class CanonicalForms:
    """Canonical, numeric and index forms."""

    sdnf: str
    sknf: str
    numeric_sdnf: str
    numeric_sknf: str
    minterm_indices: tuple[int, ...]
    maxterm_indices: tuple[int, ...]
    index_form: IndexForm
