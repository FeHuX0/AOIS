import unittest

from src.bit_utils import bits_to_str
from src.operations.sign_magnitude_arithmetic import _unsigned_division, divide_in_sign_magnitude, multiply_in_sign_magnitude


class SignMagnitudeArithmeticTests(unittest.TestCase):
    def test_multiply_basic_cases(self) -> None:
        positive = multiply_in_sign_magnitude(7, 6)
        self.assertEqual(42, positive.result_decimal)
        self.assertFalse(positive.overflow)

        negative = multiply_in_sign_magnitude(-7, 6)
        self.assertEqual(-42, negative.result_decimal)
        self.assertEqual(1, negative.result_bits[0])

        zero_result = multiply_in_sign_magnitude(0, -123)
        self.assertEqual(0, zero_result.result_decimal)
        self.assertEqual(0, zero_result.result_bits[0])

    def test_multiply_overflow_flag(self) -> None:
        result = multiply_in_sign_magnitude(65536, 65536)
        self.assertTrue(result.overflow)
        self.assertEqual(0, result.result_decimal)

    def test_divide_basic_case(self) -> None:
        result = divide_in_sign_magnitude(10, 3)
        self.assertEqual("3.33333", result.quotient_decimal)
        self.assertEqual(1, result.remainder_decimal)
        self.assertEqual("00000000000000000000000000000011", bits_to_str(result.quotient_bits))
        self.assertTrue(result.quotient_binary.startswith("11.01010"))

    def test_divide_negative_case(self) -> None:
        result = divide_in_sign_magnitude(-22, 7)
        self.assertEqual("-3.14285", result.quotient_decimal)
        self.assertTrue(result.quotient_binary.startswith("-11.00100"))
        self.assertEqual(1, result.quotient_bits[0])

    def test_divide_fractional_less_than_one(self) -> None:
        result = divide_in_sign_magnitude(1, 8)
        self.assertEqual("0.12500", result.quotient_decimal)
        self.assertTrue(result.quotient_binary.startswith("0.001"))
        self.assertEqual(0, result.quotient_bits[0])

    def test_divide_without_fraction_output(self) -> None:
        result = divide_in_sign_magnitude(9, 4, precision=0, fractional_binary_precision=0)
        self.assertEqual("2", result.quotient_decimal)
        self.assertEqual("10", result.quotient_binary)

    def test_division_validation(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            divide_in_sign_magnitude(10, 0)
        with self.assertRaises(ValueError):
            divide_in_sign_magnitude(10, 2, precision=-1)
        with self.assertRaises(ValueError):
            divide_in_sign_magnitude(10, 2, fractional_binary_precision=-1)

    def test_text_representation(self) -> None:
        text_mul = multiply_in_sign_magnitude(2, 3).as_text()
        text_div = divide_in_sign_magnitude(5, 2).as_text()
        self.assertIn("result=", text_mul)
        self.assertIn("q=", text_div)

    def test_unsigned_division_validation(self) -> None:
        with self.assertRaises(ValueError):
            _unsigned_division([0, 1], [1])
        with self.assertRaises(ZeroDivisionError):
            _unsigned_division([1, 0], [0, 0])


if __name__ == "__main__":
    unittest.main()
