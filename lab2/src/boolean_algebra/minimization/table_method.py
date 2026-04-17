"""Prime implicant chart minimization."""

from __future__ import annotations

from itertools import combinations

from models.minimization import Implicant, PrimeImplicantChartResult


class PrimeImplicantChartSolver:
    """Select a minimal cover from prime implicants."""

    def solve(
        self,
        prime_implicants: tuple[Implicant, ...],
        target_indices: tuple[int, ...],
        variables: tuple[str, ...],
        target_value: int,
    ) -> PrimeImplicantChartResult:
        """Build the prime implicant chart and choose a minimal cover."""

        if not target_indices:
            return PrimeImplicantChartResult(
                target_value=target_value,
                prime_implicants=prime_implicants,
                essential_implicants=(),
                selected_implicants=(),
                uncovered_indices=(),
                chart=(),
                expression=build_expression_from_implicants((), variables, target_value),
            )

        cover_map = {
            implicant.pattern: tuple(index for index in target_indices if index in implicant.covered_indices)
            for implicant in prime_implicants
        }
        essential_patterns: set[tuple[int | None, ...]] = set()
        for index in target_indices:
            covering = [implicant for implicant in prime_implicants if index in cover_map[implicant.pattern]]
            if len(covering) == 1:
                essential_patterns.add(covering[0].pattern)

        essential_implicants = tuple(
            implicant for implicant in prime_implicants if implicant.pattern in essential_patterns
        )
        covered_by_essentials = {
            index for implicant in essential_implicants for index in cover_map[implicant.pattern]
        }
        uncovered_indices = tuple(index for index in target_indices if index not in covered_by_essentials)

        selected_implicants = essential_implicants + self._find_best_cover(
            tuple(implicant for implicant in prime_implicants if implicant.pattern not in essential_patterns),
            uncovered_indices,
            cover_map,
        )
        chart = tuple(
            (
                implicant.pattern_string(),
                tuple(index in cover_map[implicant.pattern] for index in target_indices),
            )
            for implicant in prime_implicants
        )
        return PrimeImplicantChartResult(
            target_value=target_value,
            prime_implicants=prime_implicants,
            essential_implicants=essential_implicants,
            selected_implicants=selected_implicants,
            uncovered_indices=(),
            chart=chart,
            expression=build_expression_from_implicants(selected_implicants, variables, target_value),
        )

    def _find_best_cover(
        self,
        candidates: tuple[Implicant, ...],
        uncovered_indices: tuple[int, ...],
        cover_map: dict[tuple[int | None, ...], tuple[int, ...]],
    ) -> tuple[Implicant, ...]:
        if not uncovered_indices:
            return ()

        required = set(uncovered_indices)
        best_subset: tuple[Implicant, ...] | None = None
        best_score: tuple[int, int] | None = None
        for size in range(1, len(candidates) + 1):
            for subset in combinations(candidates, size):
                covered = {index for implicant in subset for index in cover_map[implicant.pattern]}
                if not required.issubset(covered):
                    continue
                score = (len(subset), sum(implicant.literal_count() for implicant in subset))
                if best_score is None or score < best_score:
                    best_score = score
                    best_subset = subset
            if best_subset is not None:
                return best_subset
        return ()


def build_expression_from_implicants(
    implicants: tuple[Implicant, ...],
    variables: tuple[str, ...],
    target_value: int,
) -> str:
    """Render selected implicants as a minimized expression."""

    if not implicants:
        return "0" if target_value == 1 else "1"

    if target_value == 1:
        parts = [implicant.to_dnf_term(variables) for implicant in implicants]
        if any(part == "1" for part in parts):
            return "1"
        return " | ".join(f"({part})" if " & " in part else part for part in parts)

    parts = [implicant.to_cnf_clause(variables) for implicant in implicants]
    if any(part == "0" for part in parts):
        return "0"
    return " & ".join(parts)
