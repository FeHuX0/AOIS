import unittest

from src.bit_utils import (
    add_unsigned_bits,
    bits_to_str,
    compare_unsigned_bits,
    increment_bits,
    int_to_unsigned_bits,
    invert_bits,
    is_zero,
    shift_left,
    shift_right,
    subtract_unsigned_bits,
    take_tail,
    twos_complement_negate,
    unsigned_bits_to_int,
    validate_bits,
    zeros,
)


class BitUtilsTests(unittest.TestCase):
    def test_unsigned_conversion_roundtrip(self) -> None:
        bits = int_to_unsigned_bits(37, 8)
        self.assertEqual("00100101", bits_to_str(bits))
        self.assertEqual(37, unsigned_bits_to_int(bits))

    def test_unsigned_conversion_errors(self) -> None:
        with self.assertRaises(ValueError):
            int_to_unsigned_bits(-1, 8)
        with self.assertRaises(OverflowError):
            int_to_unsigned_bits(256, 8)
        with self.assertRaises(ValueError):
            int_to_unsigned_bits(1, 0)

    def test_validate_bits_and_zeroes(self) -> None:
        self.assertEqual([0, 0, 0], validate_bits([0, 0, 0], length=3))
        with self.assertRaises(ValueError):
            validate_bits([0, 2, 1])
        with self.assertRaises(ValueError):
            validate_bits([0, 1], length=3)
        with self.assertRaises(ValueError):
            zeros(0)

    def test_add_and_increment(self) -> None:
        sum_bits, carry = add_unsigned_bits([1, 1, 1, 1], [0, 0, 0, 1])
        self.assertEqual("0000", bits_to_str(sum_bits))
        self.assertEqual(1, carry)

        incremented, carry2 = increment_bits([1, 1, 1])
        self.assertEqual([0, 0, 0], incremented)
        self.assertEqual(1, carry2)
        with self.assertRaises(ValueError):
            add_unsigned_bits([1, 0], [1])

    def test_subtract_compare_and_zero(self) -> None:
        self.assertEqual(1, compare_unsigned_bits([1, 0, 0], [0, 1, 1]))
        self.assertEqual(-1, compare_unsigned_bits([0, 1], [1, 0]))
        self.assertEqual(0, compare_unsigned_bits([1, 0], [1, 0]))
        with self.assertRaises(ValueError):
            compare_unsigned_bits([1, 0], [1])

        result = subtract_unsigned_bits([1, 0, 1, 0], [0, 0, 1, 1])
        self.assertEqual("0111", bits_to_str(result))
        self.assertTrue(is_zero([0, 0, 0]))
        self.assertFalse(is_zero([0, 1, 0]))

        with self.assertRaises(ValueError):
            subtract_unsigned_bits([0, 0, 1], [0, 1, 0])

    def test_invert_negate_and_shifts(self) -> None:
        self.assertEqual("1010", bits_to_str(invert_bits([0, 1, 0, 1])))
        self.assertEqual("1111", bits_to_str(twos_complement_negate([0, 0, 0, 1])))
        self.assertEqual("1000", bits_to_str(shift_left([0, 1, 0, 0], 1)))
        self.assertEqual("0010", bits_to_str(shift_right([1, 0, 1, 0], 2)))
        self.assertEqual("101", bits_to_str(shift_left([1, 0, 1], 0)))
        self.assertEqual("101", bits_to_str(shift_right([1, 0, 1], 0)))
        self.assertEqual("000", bits_to_str(shift_left([1, 0, 1], 5)))
        self.assertEqual("000", bits_to_str(shift_right([1, 0, 1], 3)))

        with self.assertRaises(ValueError):
            shift_left([1, 0], -1)
        with self.assertRaises(ValueError):
            shift_right([1, 0], -1)

    def test_take_tail(self) -> None:
        self.assertEqual([1, 0, 1], take_tail([0, 1, 0, 1], 3))
        self.assertEqual([0, 0, 1], take_tail([1], 3))
        with self.assertRaises(ValueError):
            take_tail([1], 0)


if __name__ == "__main__":
    unittest.main()
