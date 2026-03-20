import unittest

from src.bit_utils import bits_to_str
from src.codes.signed_codes import (
    build_code_triplet,
    decimal_to_ones_complement,
    decimal_to_sign_magnitude,
    decimal_to_twos_complement,
    ones_complement_to_decimal,
    sign_magnitude_to_decimal,
    twos_complement_to_decimal,
)


class SignedCodeTests(unittest.TestCase):
    def test_sign_magnitude_conversion(self) -> None:
        self.assertEqual("00000000000000000000000000000101", bits_to_str(decimal_to_sign_magnitude(5)))
        self.assertEqual("10000000000000000000000000000101", bits_to_str(decimal_to_sign_magnitude(-5)))
        self.assertEqual(13, sign_magnitude_to_decimal(decimal_to_sign_magnitude(13)))
        self.assertEqual(-13, sign_magnitude_to_decimal(decimal_to_sign_magnitude(-13)))
        self.assertEqual(0, sign_magnitude_to_decimal([1] + [0] * 31))

    def test_ones_complement_conversion(self) -> None:
        positive = decimal_to_ones_complement(9)
        negative = decimal_to_ones_complement(-9)
        self.assertEqual("00000000000000000000000000001001", bits_to_str(positive))
        self.assertEqual("11111111111111111111111111110110", bits_to_str(negative))
        self.assertEqual(9, ones_complement_to_decimal(positive))
        self.assertEqual(-9, ones_complement_to_decimal(negative))
        self.assertEqual(0, ones_complement_to_decimal([1] * 32))

    def test_twos_complement_conversion(self) -> None:
        self.assertEqual("00000000000000000000000000001010", bits_to_str(decimal_to_twos_complement(10)))
        self.assertEqual("11111111111111111111111111110110", bits_to_str(decimal_to_twos_complement(-10)))
        self.assertEqual(10, twos_complement_to_decimal(decimal_to_twos_complement(10)))
        self.assertEqual(-10, twos_complement_to_decimal(decimal_to_twos_complement(-10)))

    def test_twos_complement_min_value(self) -> None:
        bits = decimal_to_twos_complement(-(1 << 31))
        self.assertEqual(-(1 << 31), twos_complement_to_decimal(bits))
        self.assertEqual(1, bits[0])
        self.assertTrue(all(bit == 0 for bit in bits[1:]))

    def test_overflow_cases(self) -> None:
        with self.assertRaises(OverflowError):
            decimal_to_sign_magnitude(1 << 31)
        with self.assertRaises(OverflowError):
            decimal_to_sign_magnitude(-(1 << 31))
        with self.assertRaises(OverflowError):
            decimal_to_ones_complement(-(1 << 31))
        with self.assertRaises(OverflowError):
            decimal_to_twos_complement((1 << 31))
        with self.assertRaises(OverflowError):
            decimal_to_twos_complement(-(1 << 31) - 1)
        with self.assertRaises(ValueError):
            decimal_to_sign_magnitude(1, 1)
        with self.assertRaises(ValueError):
            decimal_to_ones_complement(1, 1)
        with self.assertRaises(ValueError):
            decimal_to_twos_complement(1, 1)

    def test_build_triplet(self) -> None:
        triplet = build_code_triplet(-7)
        self.assertEqual(-7, triplet.decimal)
        self.assertEqual(32, len(triplet.sign_magnitude))
        self.assertEqual(32, len(triplet.ones_complement))
        self.assertEqual(32, len(triplet.twos_complement))
        self.assertIn("dec=-7", triplet.as_text())
        with self.assertRaises(ValueError):
            sign_magnitude_to_decimal([1])


if __name__ == "__main__":
    unittest.main()
