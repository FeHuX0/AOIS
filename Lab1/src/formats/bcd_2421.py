"""Binary-coded decimal 2421 encoding and arithmetic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from src.bit_utils import bits_to_str, validate_bits

Bits = List[int]

BCD_2421_MAP: Dict[int, Bits] = {
    0: [0, 0, 0, 0],
    1: [0, 0, 0, 1],
    2: [0, 0, 1, 0],
    3: [0, 0, 1, 1],
    4: [0, 1, 0, 0],
    5: [1, 0, 1, 1],
    6: [1, 1, 0, 0],
    7: [1, 1, 0, 1],
    8: [1, 1, 1, 0],
    9: [1, 1, 1, 1],
}

BCD_2421_REVERSE: Dict[str, int] = {bits_to_str(bits): digit for digit, bits in BCD_2421_MAP.items()}


@dataclass(frozen=True)
class Bcd2421AdditionResult:
    """Result for 2421 BCD addition."""

    left_decimal: int
    right_decimal: int
    left_bits: Bits
    right_bits: Bits
    result_bits: Bits
    result_decimal: int

    def as_text(self) -> str:
        return (
            f"a={self.left_decimal} ({bits_to_str(self.left_bits)}), "
            f"b={self.right_decimal} ({bits_to_str(self.right_bits)}), "
            f"result={self.result_decimal} ({bits_to_str(self.result_bits)})"
        )


def _to_digits(value: int) -> List[int]:
    if value < 0:
        raise ValueError("2421 BCD supports non-negative integers only")
    if value == 0:
        return [0]
    digits: List[int] = []
    current = value
    while current > 0:
        digits.append(current % 10)
        current //= 10
    digits.reverse()
    return digits


def _from_digits(digits: List[int]) -> int:
    if not digits:
        return 0
    value = 0
    for digit in digits:
        value = value * 10 + digit
    return value


def encode_digit_2421(digit: int) -> Bits:
    """Encode one decimal digit to 2421 nibble."""
    if digit not in BCD_2421_MAP:
        raise ValueError("digit must be in range 0..9")
    return BCD_2421_MAP[digit][:]


def decode_digit_2421(bits: Bits) -> int:
    """Decode one 2421 nibble to decimal digit."""
    nibble = validate_bits(bits, length=4)
    key = bits_to_str(nibble)
    if key not in BCD_2421_REVERSE:
        raise ValueError(f"invalid 2421 nibble: {key}")
    return BCD_2421_REVERSE[key]


def encode_number_2421(value: int) -> Bits:
    """Encode non-negative integer into concatenated 2421 nibbles."""
    digits = _to_digits(value)
    encoded: Bits = []
    for digit in digits:
        encoded.extend(encode_digit_2421(digit))
    return encoded


def decode_number_2421(bits: Bits) -> int:
    """Decode concatenated 2421 nibbles into integer."""
    array = validate_bits(bits)
    if len(array) % 4 != 0:
        raise ValueError("2421 bit array length must be divisible by 4")
    digits: List[int] = []
    for index in range(0, len(array), 4):
        digits.append(decode_digit_2421(array[index : index + 4]))
    return _from_digits(digits)


def add_2421(left: int, right: int) -> Bcd2421AdditionResult:
    """Add two non-negative integers using decimal digit carry logic in 2421 BCD."""
    left_digits = _to_digits(left)
    right_digits = _to_digits(right)

    i = len(left_digits) - 1
    j = len(right_digits) - 1
    carry = 0
    result_reversed: List[int] = []

    while i >= 0 or j >= 0 or carry > 0:
        left_digit = left_digits[i] if i >= 0 else 0
        right_digit = right_digits[j] if j >= 0 else 0
        total = left_digit + right_digit + carry
        result_reversed.append(total % 10)
        carry = total // 10
        i -= 1
        j -= 1

    result_digits = list(reversed(result_reversed))
    result_decimal = _from_digits(result_digits)
    return Bcd2421AdditionResult(
        left_decimal=left,
        right_decimal=right,
        left_bits=encode_number_2421(left),
        right_bits=encode_number_2421(right),
        result_bits=encode_number_2421(result_decimal),
        result_decimal=result_decimal,
    )

