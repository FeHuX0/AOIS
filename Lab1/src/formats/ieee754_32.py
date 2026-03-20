"""Manual IEEE-754 (binary32) conversion and arithmetic."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Tuple

from src.bit_utils import bits_to_str, int_to_unsigned_bits, unsigned_bits_to_int, validate_bits

Bits = List[int]

IEEE_EXP_BITS = 8
IEEE_MANTISSA_BITS = 23
IEEE_BIAS = 127


@dataclass(frozen=True)
class Float32OperationResult:
    """Operation report for IEEE-754 binary32."""

    left_decimal: float
    right_decimal: float
    left_bits: Bits
    right_bits: Bits
    result_bits: Bits
    result_decimal: float

    def as_text(self) -> str:
        return (
            f"a={self.left_decimal} ({bits_to_str(self.left_bits)}), "
            f"b={self.right_decimal} ({bits_to_str(self.right_bits)}), "
            f"result={self.result_decimal} ({bits_to_str(self.result_bits)})"
        )


def _zero_bits(sign: int = 0) -> Bits:
    return [sign] + [0] * IEEE_EXP_BITS + [0] * IEEE_MANTISSA_BITS


def _inf_bits(sign: int = 0) -> Bits:
    return [sign] + [1] * IEEE_EXP_BITS + [0] * IEEE_MANTISSA_BITS


def _nan_bits() -> Bits:
    return [0] + [1] * IEEE_EXP_BITS + [1] + [0] * (IEEE_MANTISSA_BITS - 1)


def _bit_length(value: int) -> int:
    count = 0
    current = value
    while current > 0:
        current //= 2
        count += 1
    return count


def _shift_right_round_even(value: int, shift: int) -> int:
    if shift <= 0:
        return value << (-shift)
    divisor = 1 << shift
    quotient = value // divisor
    remainder = value - quotient * divisor
    half = divisor // 2
    if remainder > half:
        quotient += 1
    elif remainder == half and quotient % 2 == 1:
        quotient += 1
    return quotient


def _split_bits(bits: Bits) -> Tuple[int, int, int]:
    array = validate_bits(bits, length=32)
    sign = array[0]
    exponent = unsigned_bits_to_int(array[1:9])
    mantissa = unsigned_bits_to_int(array[9:])
    return sign, exponent, mantissa


def _assemble_bits(sign: int, exponent: int, mantissa: int) -> Bits:
    if sign not in (0, 1):
        raise ValueError("sign must be 0 or 1")
    if exponent < 0 or exponent > 0xFF:
        raise ValueError("exponent out of range")
    if mantissa < 0 or mantissa >= (1 << IEEE_MANTISSA_BITS):
        raise ValueError("mantissa out of range")
    return [sign] + int_to_unsigned_bits(exponent, IEEE_EXP_BITS) + int_to_unsigned_bits(mantissa, IEEE_MANTISSA_BITS)


def _is_nan(bits: Bits) -> bool:
    _, exponent, mantissa = _split_bits(bits)
    return exponent == 0xFF and mantissa != 0


def _is_inf(bits: Bits) -> bool:
    _, exponent, mantissa = _split_bits(bits)
    return exponent == 0xFF and mantissa == 0


def _is_zero(bits: Bits) -> bool:
    _, exponent, mantissa = _split_bits(bits)
    return exponent == 0 and mantissa == 0


def _finite_to_scaled(bits: Bits) -> Tuple[int, int, int]:
    sign, exponent, mantissa = _split_bits(bits)
    if exponent == 0xFF:
        raise ValueError("NaN/Inf is not finite")
    if exponent == 0:
        if mantissa == 0:
            return sign, 0, 0
        return sign, mantissa, -149
    return sign, (1 << IEEE_MANTISSA_BITS) + mantissa, exponent - 150


def _pack_from_scaled(sign: int, significand: int, power: int) -> Bits:
    """Pack signed value: sign * significand * 2**power."""
    if significand == 0:
        return _zero_bits(sign)

    highest = _bit_length(significand) - 1
    exponent = highest + power

    if exponent > 127:
        return _inf_bits(sign)

    if exponent >= -126:
        shift = highest - IEEE_MANTISSA_BITS
        sig24 = _shift_right_round_even(significand, shift)
        if sig24 >= (1 << (IEEE_MANTISSA_BITS + 1)):
            sig24 //= 2
            exponent += 1
            if exponent > 127:
                return _inf_bits(sign)

        if exponent < -126:
            return _zero_bits(sign)
        exponent_bits = exponent + IEEE_BIAS
        mantissa = sig24 - (1 << IEEE_MANTISSA_BITS)
        if mantissa < 0:
            mantissa = 0
        return _assemble_bits(sign, exponent_bits, mantissa)

    # Subnormal or underflow to zero.
    scale = power + 149
    if scale >= 0:
        mantissa = significand << scale
    else:
        mantissa = _shift_right_round_even(significand, -scale)

    if mantissa == 0:
        return _zero_bits(sign)
    if mantissa >= (1 << IEEE_MANTISSA_BITS):
        return _assemble_bits(sign, 1, 0)
    return _assemble_bits(sign, 0, mantissa)


def float_to_ieee754_bits(value: float) -> Bits:
    """Convert Python float to binary32 bit array without struct/binary helpers."""
    if math.isnan(value):
        return _nan_bits()

    sign = 1 if math.copysign(1.0, value) < 0 else 0
    if math.isinf(value):
        return _inf_bits(sign)
    if value == 0.0:
        return _zero_bits(sign)

    absolute = -value if value < 0 else value

    exponent = 0
    normalized = absolute
    while normalized >= 2.0:
        normalized /= 2.0
        exponent += 1
    while normalized < 1.0:
        normalized *= 2.0
        exponent -= 1

    if exponent > 127:
        return _inf_bits(sign)

    if exponent >= -126:
        fraction = normalized - 1.0
        mantissa = 0
        for _ in range(IEEE_MANTISSA_BITS):
            fraction *= 2.0
            if fraction >= 1.0:
                mantissa = mantissa * 2 + 1
                fraction -= 1.0
            else:
                mantissa *= 2

        fraction *= 2.0
        guard = 1 if fraction >= 1.0 else 0
        if guard == 1:
            fraction -= 1.0
        fraction *= 2.0
        round_bit = 1 if fraction >= 1.0 else 0
        if round_bit == 1:
            fraction -= 1.0
        sticky = 1 if fraction > 0.0 else 0

        if guard == 1 and (round_bit == 1 or sticky == 1 or mantissa % 2 == 1):
            mantissa += 1
            if mantissa == (1 << IEEE_MANTISSA_BITS):
                mantissa = 0
                exponent += 1
                if exponent > 127:
                    return _inf_bits(sign)

        return _assemble_bits(sign, exponent + IEEE_BIAS, mantissa)

    # Subnormal from decimal input.
    scaled = absolute
    for _ in range(149):
        scaled *= 2.0
    mantissa = int(scaled)
    fraction = scaled - mantissa
    if fraction > 0.5 or (fraction == 0.5 and mantissa % 2 == 1):
        mantissa += 1
    if mantissa >= (1 << IEEE_MANTISSA_BITS):
        return _assemble_bits(sign, 1, 0)
    return _assemble_bits(sign, 0, mantissa)


def ieee754_bits_to_float(bits: Bits) -> float:
    """Convert binary32 bit array to Python float manually."""
    sign, exponent, mantissa = _split_bits(bits)
    if exponent == 0xFF:
        if mantissa == 0:
            return float("-inf") if sign == 1 else float("inf")
        return float("nan")

    if exponent == 0:
        if mantissa == 0:
            return -0.0 if sign == 1 else 0.0
        significand = float(mantissa)
        power = -149
    else:
        significand = float((1 << IEEE_MANTISSA_BITS) + mantissa)
        power = exponent - 150

    value = significand
    if power >= 0:
        for _ in range(power):
            value *= 2.0
    else:
        for _ in range(-power):
            value /= 2.0
    if sign == 1:
        value = -value
    return value


def add_ieee754_bits(left_bits: Bits, right_bits: Bits) -> Bits:
    """Add two binary32 values."""
    if _is_nan(left_bits) or _is_nan(right_bits):
        return _nan_bits()

    ls, _, _ = _split_bits(left_bits)
    rs, _, _ = _split_bits(right_bits)

    if _is_inf(left_bits) and _is_inf(right_bits):
        if ls != rs:
            return _nan_bits()
        return left_bits[:]
    if _is_inf(left_bits):
        return left_bits[:]
    if _is_inf(right_bits):
        return right_bits[:]

    left_sign, left_sig, left_pow = _finite_to_scaled(left_bits)
    right_sign, right_sig, right_pow = _finite_to_scaled(right_bits)

    common_pow = left_pow if left_pow < right_pow else right_pow
    left_scaled = left_sig << (left_pow - common_pow)
    right_scaled = right_sig << (right_pow - common_pow)
    if left_sign == 1:
        left_scaled = -left_scaled
    if right_sign == 1:
        right_scaled = -right_scaled

    total = left_scaled + right_scaled
    if total == 0:
        return _zero_bits(0)

    sign = 1 if total < 0 else 0
    magnitude = -total if total < 0 else total
    return _pack_from_scaled(sign, magnitude, common_pow)


def subtract_ieee754_bits(left_bits: Bits, right_bits: Bits) -> Bits:
    """Subtract two binary32 values."""
    toggled = validate_bits(right_bits, length=32)
    toggled = [1 - toggled[0]] + toggled[1:]
    return add_ieee754_bits(left_bits, toggled)


def multiply_ieee754_bits(left_bits: Bits, right_bits: Bits) -> Bits:
    """Multiply two binary32 values."""
    if _is_nan(left_bits) or _is_nan(right_bits):
        return _nan_bits()

    ls, _, _ = _split_bits(left_bits)
    rs, _, _ = _split_bits(right_bits)
    result_sign = ls ^ rs

    if (_is_inf(left_bits) and _is_zero(right_bits)) or (_is_inf(right_bits) and _is_zero(left_bits)):
        return _nan_bits()
    if _is_inf(left_bits) or _is_inf(right_bits):
        return _inf_bits(result_sign)

    _, left_sig, left_pow = _finite_to_scaled(left_bits)
    _, right_sig, right_pow = _finite_to_scaled(right_bits)

    if left_sig == 0 or right_sig == 0:
        return _zero_bits(result_sign)

    magnitude = left_sig * right_sig
    power = left_pow + right_pow
    return _pack_from_scaled(result_sign, magnitude, power)


def divide_ieee754_bits(left_bits: Bits, right_bits: Bits) -> Bits:
    """Divide two binary32 values."""
    if _is_nan(left_bits) or _is_nan(right_bits):
        return _nan_bits()

    ls, _, _ = _split_bits(left_bits)
    rs, _, _ = _split_bits(right_bits)
    result_sign = ls ^ rs

    if _is_inf(left_bits) and _is_inf(right_bits):
        return _nan_bits()
    if _is_zero(left_bits) and _is_zero(right_bits):
        return _nan_bits()
    if _is_inf(left_bits):
        return _inf_bits(result_sign)
    if _is_inf(right_bits):
        return _zero_bits(result_sign)

    _, left_sig, left_pow = _finite_to_scaled(left_bits)
    _, right_sig, right_pow = _finite_to_scaled(right_bits)

    if right_sig == 0:
        return _inf_bits(result_sign)
    if left_sig == 0:
        return _zero_bits(result_sign)

    extra_precision = 80
    numerator = left_sig << extra_precision
    quotient = numerator // right_sig
    remainder = numerator - quotient * right_sig
    if remainder * 2 > right_sig or (remainder * 2 == right_sig and quotient % 2 == 1):
        quotient += 1

    power = left_pow - right_pow - extra_precision
    return _pack_from_scaled(result_sign, quotient, power)


def _operate_decimal(
    left: float,
    right: float,
    bit_operator: Callable[[Bits, Bits], Bits],
) -> Float32OperationResult:
    left_bits = float_to_ieee754_bits(left)
    right_bits = float_to_ieee754_bits(right)
    result_bits = bit_operator(left_bits, right_bits)
    return Float32OperationResult(left, right, left_bits, right_bits, result_bits, ieee754_bits_to_float(result_bits))


def add_decimal(left: float, right: float) -> Float32OperationResult:
    return _operate_decimal(left, right, add_ieee754_bits)


def subtract_decimal(left: float, right: float) -> Float32OperationResult:
    return _operate_decimal(left, right, subtract_ieee754_bits)


def multiply_decimal(left: float, right: float) -> Float32OperationResult:
    return _operate_decimal(left, right, multiply_ieee754_bits)


def divide_decimal(left: float, right: float) -> Float32OperationResult:
    return _operate_decimal(left, right, divide_ieee754_bits)
