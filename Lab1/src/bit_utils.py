"""Shared helpers for manual bit-array algorithms.

All bit arrays are MSB-first and contain integers 0/1 only.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

BITS_32 = 32
Bits = List[int]


def zeros(length: int) -> Bits:
    """Return a zero-filled bit array."""
    if length <= 0:
        raise ValueError("length must be positive")
    return [0] * length


def validate_bits(bits: Iterable[int], *, length: int | None = None) -> Bits:
    """Validate incoming bits and return them as a list."""
    array = list(bits)
    if length is not None and len(array) != length:
        raise ValueError(f"expected {length} bits, got {len(array)}")
    for bit in array:
        if bit not in (0, 1):
            raise ValueError("bits must contain only 0 and 1")
    return array


def bits_to_str(bits: Iterable[int]) -> str:
    """Serialize bits to a plain binary string."""
    return "".join("1" if bit else "0" for bit in bits)


def int_to_unsigned_bits(value: int, length: int) -> Bits:
    """Convert non-negative integer to fixed-width bit array manually."""
    if length <= 0:
        raise ValueError("length must be positive")
    if value < 0:
        raise ValueError("value must be non-negative")
    limit = 1 << length
    if value >= limit:
        raise OverflowError(f"value {value} does not fit into {length} bits")

    result = [0] * length
    current = value
    index = length - 1
    while index >= 0:
        result[index] = current % 2
        current //= 2
        index -= 1
    return result


def unsigned_bits_to_int(bits: Iterable[int]) -> int:
    """Convert unsigned bit array to integer manually."""
    value = 0
    for bit in validate_bits(bits):
        value = value * 2 + bit
    return value


def is_zero(bits: Iterable[int]) -> bool:
    """Return True if bit array represents zero."""
    for bit in validate_bits(bits):
        if bit == 1:
            return False
    return True


def compare_unsigned_bits(left: Iterable[int], right: Iterable[int]) -> int:
    """Compare two unsigned bit arrays of equal length."""
    a = validate_bits(left)
    b = validate_bits(right)
    if len(a) != len(b):
        raise ValueError("bit arrays must have the same length")
    for idx in range(len(a)):
        if a[idx] > b[idx]:
            return 1
        if a[idx] < b[idx]:
            return -1
    return 0


def add_unsigned_bits(left: Iterable[int], right: Iterable[int]) -> Tuple[Bits, int]:
    """Add unsigned numbers represented by equal-length bit arrays."""
    a = validate_bits(left)
    b = validate_bits(right)
    if len(a) != len(b):
        raise ValueError("bit arrays must have the same length")

    carry = 0
    result = [0] * len(a)
    idx = len(a) - 1
    while idx >= 0:
        total = a[idx] + b[idx] + carry
        result[idx] = total % 2
        carry = 1 if total >= 2 else 0
        idx -= 1
    return result, carry


def subtract_unsigned_bits(minuend: Iterable[int], subtrahend: Iterable[int]) -> Bits:
    """Subtract unsigned bit arrays (minuend >= subtrahend)."""
    a = validate_bits(minuend)
    b = validate_bits(subtrahend)
    if len(a) != len(b):
        raise ValueError("bit arrays must have the same length")
    if compare_unsigned_bits(a, b) < 0:
        raise ValueError("minuend must be >= subtrahend")

    result = [0] * len(a)
    borrow = 0
    idx = len(a) - 1
    while idx >= 0:
        diff = a[idx] - b[idx] - borrow
        if diff >= 0:
            result[idx] = diff
            borrow = 0
        else:
            result[idx] = diff + 2
            borrow = 1
        idx -= 1
    return result


def invert_bits(bits: Iterable[int]) -> Bits:
    """Invert every bit in array."""
    return [1 - bit for bit in validate_bits(bits)]


def increment_bits(bits: Iterable[int]) -> Tuple[Bits, int]:
    """Add one to an unsigned bit array."""
    array = validate_bits(bits)
    one = [0] * len(array)
    one[-1] = 1
    return add_unsigned_bits(array, one)


def twos_complement_negate(bits: Iterable[int]) -> Bits:
    """Negate fixed-width two's complement value."""
    inverted = invert_bits(bits)
    negated, _ = increment_bits(inverted)
    return negated


def shift_left(bits: Iterable[int], count: int = 1) -> Bits:
    """Logical left shift in fixed width."""
    array = validate_bits(bits)
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return array[:]
    if count >= len(array):
        return [0] * len(array)
    return array[count:] + [0] * count


def shift_right(bits: Iterable[int], count: int = 1) -> Bits:
    """Logical right shift in fixed width."""
    array = validate_bits(bits)
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return array[:]
    if count >= len(array):
        return [0] * len(array)
    return [0] * count + array[: len(array) - count]


def take_tail(bits: Iterable[int], length: int) -> Bits:
    """Take lower part of bit array with zero-extension when needed."""
    array = validate_bits(bits)
    if length <= 0:
        raise ValueError("length must be positive")
    if len(array) >= length:
        return array[len(array) - length :]
    return [0] * (length - len(array)) + array

