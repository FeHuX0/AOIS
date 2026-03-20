"""Arithmetic in two's complement over 32-bit arrays."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from src.bit_utils import BITS_32, add_unsigned_bits, bits_to_str, twos_complement_negate
from src.codes.signed_codes import decimal_to_twos_complement, twos_complement_to_decimal

Bits = List[int]


@dataclass(frozen=True)
class TwoComplementOpResult:
    """Result of operation in two's complement."""

    left_decimal: int
    right_decimal: int
    left_bits: Bits
    right_bits: Bits
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


def _is_overflow_for_add(left: Bits, right: Bits, result: Bits) -> bool:
    """Signed overflow check for two's complement addition."""
    return left[0] == right[0] and result[0] != left[0]


def _run_operation(
    left: int,
    right: int,
    bits: int,
    right_transform: Callable[[Bits], Bits],
) -> TwoComplementOpResult:
    left_bits = decimal_to_twos_complement(left, bits)
    original_right_bits = decimal_to_twos_complement(right, bits)
    prepared_right_bits = right_transform(original_right_bits)
    result_bits, _ = add_unsigned_bits(left_bits, prepared_right_bits)
    overflow = _is_overflow_for_add(left_bits, prepared_right_bits, result_bits)
    result_decimal = twos_complement_to_decimal(result_bits)
    return TwoComplementOpResult(
        left_decimal=left,
        right_decimal=right,
        left_bits=left_bits,
        right_bits=prepared_right_bits,
        result_bits=result_bits,
        result_decimal=result_decimal,
        overflow=overflow,
    )


def add_in_twos_complement(left: int, right: int, bits: int = BITS_32) -> TwoComplementOpResult:
    """Add two decimal numbers in two's complement."""
    return _run_operation(left, right, bits, lambda bits_value: bits_value)


def subtract_in_twos_complement(left: int, right: int, bits: int = BITS_32) -> TwoComplementOpResult:
    """Subtract two decimal numbers as left + (-right)."""
    return _run_operation(left, right, bits, twos_complement_negate)
