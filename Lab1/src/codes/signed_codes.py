"""Conversions between decimal integers and signed binary codes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.bit_utils import (
    BITS_32,
    add_unsigned_bits,
    bits_to_str,
    int_to_unsigned_bits,
    invert_bits,
    twos_complement_negate,
    unsigned_bits_to_int,
    validate_bits,
)

Bits = List[int]

SIGNED_MAGNITUDE_MAX = (1 << 31) - 1
SIGNED_MAGNITUDE_MIN = -SIGNED_MAGNITUDE_MAX
TWOS_COMPLEMENT_MAX = (1 << 31) - 1
TWOS_COMPLEMENT_MIN = -(1 << 31)


def _validate_code_width(bits: int) -> None:
    if bits < 2:
        raise ValueError("bits must be at least 2")


def _validate_sign_magnitude_range(value: int, bits: int) -> None:
    _validate_code_width(bits)
    max_magnitude = (1 << (bits - 1)) - 1
    min_value = -max_magnitude
    if value < min_value or value > max_magnitude:
        raise OverflowError(f"{value} does not fit into sign-magnitude {bits}-bit code")


def _validate_ones_complement_range(value: int, bits: int) -> None:
    _validate_code_width(bits)
    max_magnitude = (1 << (bits - 1)) - 1
    min_value = -max_magnitude
    if value < min_value or value > max_magnitude:
        raise OverflowError(f"{value} does not fit into one's complement {bits}-bit code")


def _validate_twos_complement_range(value: int, bits: int) -> None:
    _validate_code_width(bits)
    max_value = (1 << (bits - 1)) - 1
    min_value = -(1 << (bits - 1))
    if value < min_value or value > max_value:
        raise OverflowError(f"{value} does not fit into two's complement {bits}-bit code")


@dataclass(frozen=True)
class CodeTriplet:
    """Binary forms for one decimal integer."""

    decimal: int
    sign_magnitude: Bits
    ones_complement: Bits
    twos_complement: Bits

    def as_text(self) -> str:
        return (
            f"dec={self.decimal}, "
            f"direct={bits_to_str(self.sign_magnitude)}, "
            f"inverse={bits_to_str(self.ones_complement)}, "
            f"additional={bits_to_str(self.twos_complement)}"
        )


def decimal_to_sign_magnitude(value: int, bits: int = BITS_32) -> Bits:
    """Convert decimal integer to sign-magnitude code."""
    _validate_sign_magnitude_range(value, bits)

    sign = 1 if value < 0 else 0
    magnitude = int_to_unsigned_bits(abs(value), bits - 1)
    return [sign] + magnitude


def sign_magnitude_to_decimal(bits: Bits) -> int:
    """Convert sign-magnitude code to decimal integer."""
    array = validate_bits(bits)
    if len(array) < 2:
        raise ValueError("bits must contain at least sign and one magnitude bit")

    sign = array[0]
    magnitude = unsigned_bits_to_int(array[1:])
    if sign == 1 and magnitude == 0:
        return 0
    return -magnitude if sign else magnitude


def decimal_to_ones_complement(value: int, bits: int = BITS_32) -> Bits:
    """Convert decimal integer to one's complement code."""
    _validate_ones_complement_range(value, bits)

    positive = [0] + int_to_unsigned_bits(abs(value), bits - 1)
    if value >= 0:
        return positive
    return invert_bits(positive)


def ones_complement_to_decimal(bits: Bits) -> int:
    """Convert one's complement code to decimal integer."""
    array = validate_bits(bits)
    if array[0] == 0:
        return unsigned_bits_to_int(array)

    restored = invert_bits(array)
    magnitude = unsigned_bits_to_int(restored)
    if magnitude == 0:
        return 0
    return -magnitude


def decimal_to_twos_complement(value: int, bits: int = BITS_32) -> Bits:
    """Convert decimal integer to two's complement code."""
    _validate_twos_complement_range(value, bits)

    if value >= 0:
        return int_to_unsigned_bits(value, bits)

    positive = int_to_unsigned_bits(abs(value), bits)
    inverted = invert_bits(positive)
    negated, _ = add_unsigned_bits(inverted, int_to_unsigned_bits(1, bits))
    return negated


def twos_complement_to_decimal(bits: Bits) -> int:
    """Convert two's complement code to decimal integer."""
    array = validate_bits(bits)
    if array[0] == 0:
        return unsigned_bits_to_int(array)

    magnitude_bits = twos_complement_negate(array)
    magnitude = unsigned_bits_to_int(magnitude_bits)
    return -magnitude


def build_code_triplet(value: int, bits: int = BITS_32) -> CodeTriplet:
    """Create all three codes for one decimal integer."""
    return CodeTriplet(
        decimal=value,
        sign_magnitude=decimal_to_sign_magnitude(value, bits),
        ones_complement=decimal_to_ones_complement(value, bits),
        twos_complement=decimal_to_twos_complement(value, bits),
    )
