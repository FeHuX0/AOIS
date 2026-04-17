"""Minimization-related models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Implicant:
    """A cube in boolean minimization."""

    pattern: tuple[int | None, ...]
    covered_indices: tuple[int, ...]

    def ones_count(self) -> int:
        """Count explicit ones in the pattern."""

        return sum(bit == 1 for bit in self.pattern)

    def literal_count(self) -> int:
        """Count non-don't-care literals."""

        return sum(bit is not None for bit in self.pattern)

    def pattern_string(self) -> str:
        """Render a binary pattern with '-' wildcards."""

        return "".join("-" if bit is None else str(bit) for bit in self.pattern)

    def to_dnf_term(self, variables: tuple[str, ...]) -> str:
        """Render the implicant as a DNF term."""

        literals = [
            variable if bit == 1 else f"!{variable}"
            for variable, bit in zip(variables, self.pattern, strict=True)
            if bit is not None
        ]
        if not literals:
            return "1"
        return " & ".join(literals)

    def to_cnf_clause(self, variables: tuple[str, ...]) -> str:
        """Render the implicant as a CNF clause for zeros."""

        literals = [
            variable if bit == 0 else f"!{variable}"
            for variable, bit in zip(variables, self.pattern, strict=True)
            if bit is not None
        ]
        if not literals:
            return "0"
        return "(" + " | ".join(literals) + ")"


@dataclass(frozen=True, slots=True)
class CombinationRecord:
    """One gluing operation between implicants."""

    left: str
    right: str
    result: str


@dataclass(frozen=True, slots=True)
class CombinationRound:
    """One Quine-McCluskey gluing stage."""

    stage: int
    groups: tuple[tuple[int, tuple[str, ...]], ...]
    combinations: tuple[CombinationRecord, ...]
    prime_implicants: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CalculationMethodResult:
    """Result of the calculation method with gluing stages."""

    target_value: int
    rounds: tuple[CombinationRound, ...]
    prime_implicants: tuple[Implicant, ...]
    minimized_expression: str


@dataclass(frozen=True, slots=True)
class PrimeImplicantChartResult:
    """Result of the prime implicant chart method."""

    target_value: int
    prime_implicants: tuple[Implicant, ...]
    essential_implicants: tuple[Implicant, ...]
    selected_implicants: tuple[Implicant, ...]
    uncovered_indices: tuple[int, ...]
    chart: tuple[tuple[str, tuple[bool, ...]], ...]
    expression: str


@dataclass(frozen=True, slots=True)
class KarnaughGroup:
    """A selected Karnaugh grouping."""

    target_value: int
    cells: tuple[int, ...]
    pattern: tuple[int | None, ...]
    term: str


@dataclass(frozen=True, slots=True)
class KarnaughSolution:
    """A Karnaugh-based minimized solution."""

    target_value: int
    groups: tuple[KarnaughGroup, ...]
    expression: str


@dataclass(frozen=True, slots=True)
class KarnaughMapResult:
    """Karnaugh map data and visualization."""

    layer_variables: tuple[str, ...]
    row_variables: tuple[str, ...]
    column_variables: tuple[str, ...]
    layer_codes: tuple[tuple[int, ...], ...]
    row_codes: tuple[tuple[int, ...], ...]
    column_codes: tuple[tuple[int, ...], ...]
    layers: tuple[tuple[tuple[int, ...], ...], ...]
    visualization: str
    dnf_solution: KarnaughSolution | None
    cnf_solution: KarnaughSolution | None

    @property
    def matrix(self) -> tuple[tuple[int, ...], ...]:
        """Backward-compatible access to the first Karnaugh layer."""

        return self.layers[0] if self.layers else ()
