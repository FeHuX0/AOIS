import math
import unittest

from src.bit_utils import bits_to_str, unsigned_bits_to_int
from src.formats.ieee754_32 import (
    IEEE_MANTISSA_BITS,
    _assemble_bits,
    _finite_to_scaled,
    _inf_bits,
    _pack_from_scaled,
    _shift_right_round_even,
    _zero_bits,
    add_decimal,
    add_ieee754_bits,
    divide_decimal,
    divide_ieee754_bits,
    float_to_ieee754_bits,
    ieee754_bits_to_float,
    multiply_decimal,
    multiply_ieee754_bits,
    subtract_decimal,
    subtract_ieee754_bits,
)


class Ieee754Tests(unittest.TestCase):
    def test_known_encodings(self) -> None:
        self.assertEqual("00111111100000000000000000000000", bits_to_str(float_to_ieee754_bits(1.0)))
        self.assertEqual("11000000001000000000000000000000", bits_to_str(float_to_ieee754_bits(-2.5)))
        self.assertEqual("00000000000000000000000000000000", bits_to_str(float_to_ieee754_bits(0.0)))
        self.assertEqual("10000000000000000000000000000000", bits_to_str(float_to_ieee754_bits(-0.0)))

    def test_special_encodings(self) -> None:
        self.assertEqual("01111111100000000000000000000000", bits_to_str(float_to_ieee754_bits(float("inf"))))
        self.assertEqual("11111111100000000000000000000000", bits_to_str(float_to_ieee754_bits(float("-inf"))))
        self.assertEqual("01111111110000000000000000000000", bits_to_str(float_to_ieee754_bits(float("nan"))))

    def test_roundtrip_for_regular_values(self) -> None:
        for value in [0.5, -13.25, 3.75, 123.5]:
            bits = float_to_ieee754_bits(value)
            restored = ieee754_bits_to_float(bits)
            self.assertAlmostEqual(value, restored, places=6)

    def test_subnormal_encoding(self) -> None:
        bits = float_to_ieee754_bits(1.0e-40)
        exponent_bits = bits[1:9]
        mantissa_bits = bits[9:]
        self.assertTrue(all(bit == 0 for bit in exponent_bits))
        self.assertTrue(any(bit == 1 for bit in mantissa_bits))

    def test_add_subtract(self) -> None:
        left = float_to_ieee754_bits(1.5)
        right = float_to_ieee754_bits(2.25)
        result_add = add_ieee754_bits(left, right)
        result_sub = subtract_ieee754_bits(float_to_ieee754_bits(5.5), float_to_ieee754_bits(2.0))
        self.assertAlmostEqual(3.75, ieee754_bits_to_float(result_add), places=6)
        self.assertAlmostEqual(3.5, ieee754_bits_to_float(result_sub), places=6)

    def test_multiply_divide(self) -> None:
        result_mul = multiply_ieee754_bits(float_to_ieee754_bits(-3.0), float_to_ieee754_bits(0.5))
        result_div = divide_ieee754_bits(float_to_ieee754_bits(7.0), float_to_ieee754_bits(2.0))
        self.assertAlmostEqual(-1.5, ieee754_bits_to_float(result_mul), places=6)
        self.assertAlmostEqual(3.5, ieee754_bits_to_float(result_div), places=6)

    def test_special_operation_cases(self) -> None:
        nan_result = add_ieee754_bits(float_to_ieee754_bits(float("inf")), float_to_ieee754_bits(float("-inf")))
        inf_plus_inf = add_ieee754_bits(float_to_ieee754_bits(float("inf")), float_to_ieee754_bits(float("inf")))
        zero_div_zero = divide_ieee754_bits(float_to_ieee754_bits(0.0), float_to_ieee754_bits(0.0))
        mul_inf_zero = multiply_ieee754_bits(float_to_ieee754_bits(float("inf")), float_to_ieee754_bits(0.0))
        finite_div_zero = divide_ieee754_bits(float_to_ieee754_bits(-6.0), float_to_ieee754_bits(0.0))
        finite_div_inf = divide_ieee754_bits(float_to_ieee754_bits(8.0), float_to_ieee754_bits(float("inf")))
        inf_div_inf = divide_ieee754_bits(float_to_ieee754_bits(float("inf")), float_to_ieee754_bits(float("inf")))
        nan_mul = multiply_ieee754_bits(float_to_ieee754_bits(float("nan")), float_to_ieee754_bits(1.0))
        nan_add = add_ieee754_bits(float_to_ieee754_bits(float("nan")), float_to_ieee754_bits(1.0))
        huge_mul = multiply_ieee754_bits(float_to_ieee754_bits(3.4e38), float_to_ieee754_bits(2.0))
        tiny_div = divide_ieee754_bits(float_to_ieee754_bits(1.0e-38), float_to_ieee754_bits(2.0))

        self.assertTrue(math.isnan(ieee754_bits_to_float(nan_result)))
        self.assertEqual(float("inf"), ieee754_bits_to_float(inf_plus_inf))
        self.assertTrue(math.isnan(ieee754_bits_to_float(zero_div_zero)))
        self.assertTrue(math.isnan(ieee754_bits_to_float(mul_inf_zero)))
        self.assertEqual(float("-inf"), ieee754_bits_to_float(finite_div_zero))
        self.assertEqual(0.0, ieee754_bits_to_float(finite_div_inf))
        self.assertTrue(math.isnan(ieee754_bits_to_float(inf_div_inf)))
        self.assertTrue(math.isnan(ieee754_bits_to_float(nan_mul)))
        self.assertTrue(math.isnan(ieee754_bits_to_float(nan_add)))
        self.assertEqual(float("inf"), ieee754_bits_to_float(huge_mul))
        self.assertLessEqual(unsigned_bits_to_int(tiny_div[1:9]), 1)

    def test_wrappers_and_text(self) -> None:
        add_result = add_decimal(0.25, 0.5)
        sub_result = subtract_decimal(2.0, 1.25)
        mul_result = multiply_decimal(2.0, -4.0)
        div_result = divide_decimal(3.0, 4.0)

        self.assertAlmostEqual(0.75, add_result.result_decimal, places=6)
        self.assertAlmostEqual(0.75, sub_result.result_decimal, places=6)
        self.assertAlmostEqual(-8.0, mul_result.result_decimal, places=6)
        self.assertAlmostEqual(0.75, div_result.result_decimal, places=6)
        self.assertIn("result=", add_result.as_text())

    def test_internal_helpers_and_validation_errors(self) -> None:
        self.assertEqual(2, _shift_right_round_even(7, 2))
        self.assertEqual(4, _shift_right_round_even(7, 1))

        with self.assertRaisesRegex(ValueError, "sign"):
            _assemble_bits(2, 0, 0)
        with self.assertRaisesRegex(ValueError, "exponent"):
            _assemble_bits(0, 256, 0)
        with self.assertRaisesRegex(ValueError, "mantissa"):
            _assemble_bits(0, 0, 1 << IEEE_MANTISSA_BITS)
        with self.assertRaisesRegex(ValueError, "finite"):
            _finite_to_scaled(_inf_bits())

    def test_pack_from_scaled_edge_cases(self) -> None:
        self.assertEqual(_zero_bits(1), _pack_from_scaled(1, 0, 10))
        self.assertEqual(_inf_bits(0), _pack_from_scaled(0, (1 << 25) - 1, 103))
        self.assertEqual(_assemble_bits(0, 0, 1), _pack_from_scaled(0, 1, -149))
        self.assertEqual(_zero_bits(0), _pack_from_scaled(0, 1, -200))
        self.assertEqual(_assemble_bits(0, 1, 0), _pack_from_scaled(0, (1 << 24) - 1, -150))

    def test_conversion_extremes_and_subnormal_boundaries(self) -> None:
        self.assertEqual(_inf_bits(0), float_to_ieee754_bits(1.0e39))

        near_min_normal = math.ldexp((1 << IEEE_MANTISSA_BITS) - 0.5, -149)
        self.assertEqual(_assemble_bits(0, 1, 0), float_to_ieee754_bits(near_min_normal))

        negative_subnormal = ieee754_bits_to_float(_assemble_bits(1, 0, 1))
        self.assertLess(negative_subnormal, 0.0)
        self.assertEqual(math.ldexp(1.0, -149), abs(negative_subnormal))
        self.assertEqual(8.0, ieee754_bits_to_float(float_to_ieee754_bits(8.0)))

    def test_operation_branch_edges(self) -> None:
        pos_inf = float_to_ieee754_bits(float("inf"))
        neg_inf = float_to_ieee754_bits(float("-inf"))
        nan_bits = float_to_ieee754_bits(float("nan"))
        one_bits = float_to_ieee754_bits(1.0)

        self.assertEqual(float("inf"), ieee754_bits_to_float(add_ieee754_bits(pos_inf, one_bits)))
        self.assertEqual(float("-inf"), ieee754_bits_to_float(add_ieee754_bits(one_bits, neg_inf)))
        self.assertEqual(-1.0, ieee754_bits_to_float(add_ieee754_bits(float_to_ieee754_bits(-1.5), float_to_ieee754_bits(0.5))))
        self.assertEqual(0.0, ieee754_bits_to_float(add_ieee754_bits(float_to_ieee754_bits(2.5), float_to_ieee754_bits(-2.5))))

        self.assertEqual(
            float("-inf"),
            ieee754_bits_to_float(multiply_ieee754_bits(pos_inf, float_to_ieee754_bits(-3.0))),
        )
        zero_product = ieee754_bits_to_float(multiply_ieee754_bits(float_to_ieee754_bits(0.0), float_to_ieee754_bits(-3.0)))
        self.assertEqual(0.0, zero_product)
        self.assertEqual(-1.0, math.copysign(1.0, zero_product))

        self.assertTrue(math.isnan(ieee754_bits_to_float(divide_ieee754_bits(nan_bits, one_bits))))
        self.assertEqual(
            float("-inf"),
            ieee754_bits_to_float(divide_ieee754_bits(neg_inf, float_to_ieee754_bits(2.0))),
        )
        zero_quotient = ieee754_bits_to_float(divide_ieee754_bits(float_to_ieee754_bits(-0.0), float_to_ieee754_bits(2.0)))
        self.assertEqual(0.0, zero_quotient)
        self.assertEqual(-1.0, math.copysign(1.0, zero_quotient))

        rounded_case: tuple[float, float] | None = None
        for left in range(1, 16):
            for right in range(2, 16):
                left_value = float(left)
                right_value = float(right)
                left_bits = float_to_ieee754_bits(left_value)
                right_bits = float_to_ieee754_bits(right_value)
                _, left_sig, _ = _finite_to_scaled(left_bits)
                _, right_sig, _ = _finite_to_scaled(right_bits)
                numerator = left_sig << 80
                quotient = numerator // right_sig
                remainder = numerator - quotient * right_sig
                if remainder * 2 > right_sig or (remainder * 2 == right_sig and quotient % 2 == 1):
                    rounded_case = (left_value, right_value)
                    break
            if rounded_case is not None:
                break

        self.assertIsNotNone(rounded_case)
        left_value, right_value = rounded_case
        quotient_bits = divide_ieee754_bits(float_to_ieee754_bits(left_value), float_to_ieee754_bits(right_value))
        self.assertAlmostEqual(left_value / right_value, ieee754_bits_to_float(quotient_bits), places=6)


if __name__ == "__main__":
    unittest.main()
