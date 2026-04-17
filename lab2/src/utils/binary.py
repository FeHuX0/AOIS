"""Binary and combinatorial helpers."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import combinations


def bit_tuple_to_int(bits: tuple[int, ...]) -> int:
    """Convert a tuple of bits to an integer."""

    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def int_to_bit_tuple(value: int, width: int) -> tuple[int, ...]:
    """Convert an integer to a fixed-width bit tuple."""

    return tuple((value >> shift) & 1 for shift in range(width - 1, -1, -1))


def gray_code(width: int) -> tuple[tuple[int, ...], ...]:
    """Build a Gray code sequence of the requested width."""

    if width == 0:
        return ((),)
    if width == 1:
        return ((0,), (1,))
    previous = gray_code(width - 1)
    return tuple((0, *item) for item in previous) + tuple((1, *item) for item in reversed(previous))


def powerset(items: Iterable[str]) -> Iterator[tuple[str, ...]]:
    """Yield the non-empty power set of the provided iterable."""

    normalized = tuple(items)
    for size in range(1, len(normalized) + 1):
        yield from combinations(normalized, size)
