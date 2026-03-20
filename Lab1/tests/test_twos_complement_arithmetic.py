import unittest

from src.bit_utils import bits_to_str
from src.operations.twos_complement_arithmetic import add_in_twos_complement, subtract_in_twos_complement


class TwosComplementArithmeticTests(unittest.TestCase):
    def test_add_without_overflow(self) -> None:
        result = add_in_twos_complement(15, -7)
        self.assertEqual(8, result.result_decimal)
        self.assertFalse(result.overflow)
        self.assertEqual("00000000000000000000000000001000", bits_to_str(result.result_bits))

    def test_add_with_positive_overflow(self) -> None:
        result = add_in_twos_complement((1 << 31) - 1, 1)
        self.assertTrue(result.overflow)
        self.assertEqual(-(1 << 31), result.result_decimal)

    def test_add_with_negative_overflow(self) -> None:
        result = add_in_twos_complement(-(1 << 31), -1)
        self.assertTrue(result.overflow)
        self.assertEqual((1 << 31) - 1, result.result_decimal)

    def test_subtract_without_overflow(self) -> None:
        result = subtract_in_twos_complement(10, 3)
        self.assertEqual(7, result.result_decimal)
        self.assertFalse(result.overflow)
        self.assertEqual("00000000000000000000000000000111", bits_to_str(result.result_bits))

    def test_subtract_with_overflow(self) -> None:
        result = subtract_in_twos_complement((1 << 31) - 1, -1)
        self.assertTrue(result.overflow)
        self.assertEqual(-(1 << 31), result.result_decimal)

    def test_text_representation(self) -> None:
        result = add_in_twos_complement(1, 2)
        text = result.as_text()
        self.assertIn("a=1", text)
        self.assertIn("b=2", text)
        self.assertIn("overflow=False", text)


if __name__ == "__main__":
    unittest.main()

