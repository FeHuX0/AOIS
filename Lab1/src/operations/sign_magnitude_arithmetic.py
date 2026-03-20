"""Arithmetic in sign-magnitude code."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from src.bit_utils import (
    BITS_32,
    add_unsigned_bits,
    bits_to_str,
    compare_unsigned_bits,
    int_to_unsigned_bits,
    is_zero,
    subtract_unsigned_bits,
    unsigned_bits_to_int,
)
from src.codes.signed_codes import decimal_to_sign_magnitude

Bits = List[int]


def _trim_leading_zeros(bits: Bits) -> Bits:
    index = 0
    while index < len(bits) - 1 and bits[index] == 0:
        index += 1
    return bits[index:]


def _unsigned_division(dividend: Bits, divisor: Bits) -> Tuple[Bits, Bits]:
    """Unsigned long division for fixed-width bit arrays."""
    if len(dividend) != len(divisor):
        raise ValueError("dividend and divisor must have equal length")
    if is_zero(divisor):
        raise ZeroDivisionError("division by zero")

    width = len(dividend)
    quotient = [0] * width
    remainder = [0] * width

    for index, bit in enumerate(dividend):
        remainder = remainder[1:] + [bit]
        if compare_unsigned_bits(remainder, divisor) >= 0:
            remainder = subtract_unsigned_bits(remainder, divisor)
            quotient[index] = 1
    return quotient, remainder


def _fractional_binary_bits(remainder: int, divisor: int, count: int) -> Bits:
    bits: Bits = []
    current = remainder
    for _ in range(count):
        current *= 2
        if current >= divisor:
            bits.append(1)
            current -= divisor
        else:
            bits.append(0)
    return bits


def _fractional_decimal_digits(remainder: int, divisor: int, precision: int) -> str:
    digits: List[str] = []
    current = remainder
    for _ in range(precision):
        current *= 10
        digit = 0
        while current >= divisor:
            current -= divisor
            digit += 1
        digits.append(str(digit))
    return "".join(digits)


@dataclass(frozen=True)
class SignMagnitudeMulResult:
    """Sign-magnitude multiplication details."""

    left_decimal: int
    right_decimal: int
    left_bits: Bits
    right_bits: Bits
    full_magnitude_product_bits: Bits
    result_bits: Bits
    result_decimal: int
    overflow: bool

    def as_text(self) -> str:
        return (
            f"a={self.left_decimal} ({bits_to_str(self.left_bits)}), "
            f"b={self.right_decimal} ({bits_to_str(self.right_bits)}), "
            f"result={self.result_decimal} ({bits_to_str(self.result_bits)}), "
            f"overflow={self.overflow}"
        )


@dataclass(frozen=True)
class SignMagnitudeDivResult:
    """Sign-magnitude division details."""

    left_decimal: int
    right_decimal: int
    left_bits: Bits
    right_bits: Bits
    quotient_bits: Bits
    quotient_decimal: str
    quotient_binary: str
    remainder_decimal: int

    def as_text(self) -> str:
        return (
            f"a={self.left_decimal} ({bits_to_str(self.left_bits)}), "
            f"b={self.right_decimal} ({bits_to_str(self.right_bits)}), "
            f"q={self.quotient_decimal} ({self.quotient_binary}), "
            f"remainder={self.remainder_decimal}"
        )


def multiply_in_sign_magnitude(left: int, right: int, bits: int = BITS_32) -> SignMagnitudeMulResult:
    """Multiply two integers using sign-magnitude internal representation."""
    left_bits = decimal_to_sign_magnitude(left, bits)
    right_bits = decimal_to_sign_magnitude(right, bits)

    n = bits - 1
    left_mag = left_bits[1:]
    right_mag = right_bits[1:]

    accumulator = [0] * (2 * n)
    for shift in range(n):
        right_bit = right_mag[n - 1 - shift]
        if right_bit == 0:
            continue
        partial = [0] * (n - shift) + left_mag + [0] * shift
        accumulator, _ = add_unsigned_bits(accumulator, partial)

    overflow = any(accumulator[:n])
    result_magnitude = accumulator[n:]
    sign = 0 if is_zero(result_magnitude) else (left_bits[0] ^ right_bits[0])
    result_bits = [sign] + result_magnitude
    result_decimal = unsigned_bits_to_int(result_magnitude)
    if sign == 1:
        result_decimal = -result_decimal

    return SignMagnitudeMulResult(
        left_decimal=left,
        right_decimal=right,
        left_bits=left_bits,
        right_bits=right_bits,
        full_magnitude_product_bits=accumulator,
        result_bits=result_bits,
        result_decimal=result_decimal,
        overflow=overflow,
    )


def divide_in_sign_magnitude(
    left: int,
    right: int,
    *,
    bits: int = BITS_32,
    precision: int = 5,
    fractional_binary_precision: int = 20,
) -> SignMagnitudeDivResult:
    """Divide two integers in sign-magnitude and return decimal/binary text forms."""
    if right == 0:
        raise ZeroDivisionError("division by zero")
    if precision < 0:
        raise ValueError("precision must be non-negative")
    if fractional_binary_precision < 0:
        raise ValueError("fractional_binary_precision must be non-negative")

    left_bits = decimal_to_sign_magnitude(left, bits)
    right_bits = decimal_to_sign_magnitude(right, bits)

    left_mag = left_bits[1:]
    right_mag = right_bits[1:]
    quotient_mag_bits, remainder_bits = _unsigned_division(left_mag, right_mag)

    quotient_mag_int = unsigned_bits_to_int(quotient_mag_bits)
    remainder = unsigned_bits_to_int(remainder_bits)
    divisor = abs(right)
    sign = 1 if (left < 0) ^ (right < 0) else 0

    fraction_digits = _fractional_decimal_digits(remainder, divisor, precision)
    non_zero_fraction = any(ch != "0" for ch in fraction_digits)
    is_negative_output = sign == 1 and (quotient_mag_int != 0 or non_zero_fraction)
    sign_prefix = "-" if is_negative_output else ""
    quotient_decimal = f"{sign_prefix}{quotient_mag_int}"
    if precision > 0:
        quotient_decimal = f"{quotient_decimal}.{fraction_digits}"

    fraction_binary = _fractional_binary_bits(remainder, divisor, fractional_binary_precision)
    int_text = bits_to_str(_trim_leading_zeros(quotient_mag_bits))
    if int_text == "":
        int_text = "0"
    quotient_binary = f"{'-' if is_negative_output else ''}{int_text}"
    if fractional_binary_precision > 0:
        quotient_binary = f"{quotient_binary}.{bits_to_str(fraction_binary)}"

    quotient_bits = [0 if quotient_mag_int == 0 and not non_zero_fraction else sign] + quotient_mag_bits
    return SignMagnitudeDivResult(
        left_decimal=left,
        right_decimal=right,
        left_bits=left_bits,
        right_bits=right_bits,
        quotient_bits=quotient_bits,
        quotient_decimal=quotient_decimal,
        quotient_binary=quotient_binary,
        remainder_decimal=remainder,
    )
