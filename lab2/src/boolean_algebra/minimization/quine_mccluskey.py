"""Quine-McCluskey calculation method."""

from __future__ import annotations

from collections import defaultdict

from models.minimization import CombinationRecord, CombinationRound, Implicant
from utils.binary import int_to_bit_tuple


class QuineMcCluskeyMinimizer:
    """Generate prime implicants through iterative gluing."""

    def generate_prime_implicants(
        self,
        indices: tuple[int, ...],
        variable_count: int,
    ) -> tuple[tuple[Implicant, ...], tuple[CombinationRound, ...]]:
        """Return prime implicants and detailed gluing stages."""

        if not indices:
            return (), ()

        current_level = tuple(
            Implicant(pattern=int_to_bit_tuple(index, variable_count), covered_indices=(index,))
            for index in indices
        )
        rounds: list[CombinationRound] = []
        prime_implicants: list[Implicant] = []
        stage = 1

        while current_level:
            grouped = self._group_by_ones(current_level)
            combined_next: dict[tuple[int | None, ...], Implicant] = {}
            combinations: list[CombinationRecord] = []
            used_patterns: set[tuple[int | None, ...]] = set()

            ordered_groups = sorted(grouped.items())
            for position, (ones_count, left_group) in enumerate(ordered_groups[:-1]):
                right_ones, right_group = ordered_groups[position + 1]
                if right_ones - ones_count != 1:
                    continue
                for left in left_group:
                    for right in right_group:
                        combined_pattern = _combine_patterns(left.pattern, right.pattern)
                        if combined_pattern is None:
                            continue
                        used_patterns.add(left.pattern)
                        used_patterns.add(right.pattern)
                        combined_indices = tuple(sorted(set(left.covered_indices + right.covered_indices)))
                        combined_next[combined_pattern] = Implicant(
                            pattern=combined_pattern,
                            covered_indices=combined_indices,
                        )
                        combinations.append(
                            CombinationRecord(
                                left=left.pattern_string(),
                                right=right.pattern_string(),
                                result=_pattern_to_string(combined_pattern),
                            )
                        )

            current_primes = tuple(
                implicant
                for implicant in current_level
                if implicant.pattern not in used_patterns
            )
            prime_implicants.extend(current_primes)
            rounds.append(
                CombinationRound(
                    stage=stage,
                    groups=tuple(
                        (ones_count, tuple(item.pattern_string() for item in group_items))
                        for ones_count, group_items in ordered_groups
                    ),
                    combinations=tuple(combinations),
                    prime_implicants=tuple(item.pattern_string() for item in current_primes),
                )
            )

            if not combined_next:
                break
            current_level = tuple(sorted(combined_next.values(), key=lambda item: item.pattern_string()))
            stage += 1

        unique_primes = _deduplicate_implicants(tuple(prime_implicants))
        return unique_primes, tuple(rounds)

    @staticmethod
    def _group_by_ones(implicants: tuple[Implicant, ...]) -> dict[int, list[Implicant]]:
        groups: dict[int, list[Implicant]] = defaultdict(list)
        for implicant in implicants:
            groups[implicant.ones_count()].append(implicant)
        return groups


def _combine_patterns(
    left: tuple[int | None, ...],
    right: tuple[int | None, ...],
) -> tuple[int | None, ...] | None:
    differences = 0
    combined: list[int | None] = []
    for left_bit, right_bit in zip(left, right, strict=True):
        if left_bit == right_bit:
            combined.append(left_bit)
            continue
        if left_bit is None or right_bit is None:
            return None
        differences += 1
        combined.append(None)
        if differences > 1:
            return None
    if differences != 1:
        return None
    return tuple(combined)


def _pattern_to_string(pattern: tuple[int | None, ...]) -> str:
    return "".join("-" if bit is None else str(bit) for bit in pattern)


def _deduplicate_implicants(implicants: tuple[Implicant, ...]) -> tuple[Implicant, ...]:
    deduplicated: dict[tuple[int | None, ...], Implicant] = {}
    for implicant in implicants:
        existing = deduplicated.get(implicant.pattern)
        if existing is None:
            deduplicated[implicant.pattern] = implicant
            continue
        deduplicated[implicant.pattern] = Implicant(
            pattern=implicant.pattern,
            covered_indices=tuple(sorted(set(existing.covered_indices + implicant.covered_indices))),
        )
    return tuple(sorted(deduplicated.values(), key=lambda item: item.pattern_string()))
