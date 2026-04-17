"""Boolean derivative models."""

from __future__ import annotations

from dataclasses import dataclass

from models.truth_table import TruthTable


@dataclass(frozen=True, slots=True)
class DerivativeResult:
    """One partial or mixed boolean derivative."""

    variables: tuple[str, ...]
    truth_table: TruthTable
    expression: str


@dataclass(frozen=True, slots=True)
class DerivativesSummary:
    """All derivative-related artefacts."""

    partial: tuple[DerivativeResult, ...]
    mixed: tuple[DerivativeResult, ...]
    fictitious_variables: tuple[str, ...]
