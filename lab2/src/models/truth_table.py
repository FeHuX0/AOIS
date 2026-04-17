"""Truth table models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TruthTableRow:
    """Single truth table row."""

    index: int
    inputs: tuple[int, ...]
    result: int

    def as_assignment(self, variables: tuple[str, ...]) -> dict[str, int]:
        """Convert row inputs to a variable mapping."""

        return dict(zip(variables, self.inputs, strict=True))


@dataclass(frozen=True, slots=True)
class TruthTable:
    """Full truth table for a boolean function."""

    variables: tuple[str, ...]
    rows: tuple[TruthTableRow, ...]

    @property
    def result_vector(self) -> tuple[int, ...]:
        """Return function values in canonical order."""

        return tuple(row.result for row in self.rows)

    def indices_with_value(self, value: int) -> tuple[int, ...]:
        """Return row indices for the requested function value."""

        return tuple(row.index for row in self.rows if row.result == value)

    @property
    def minterm_indices(self) -> tuple[int, ...]:
        """Return indices of rows where the function equals one."""

        return self.indices_with_value(1)

    @property
    def maxterm_indices(self) -> tuple[int, ...]:
        """Return indices of rows where the function equals zero."""

        return self.indices_with_value(0)

    def lookup(self) -> dict[tuple[int, ...], int]:
        """Build a fast lookup by input tuple."""

        return {row.inputs: row.result for row in self.rows}
