import unittest

from src.bit_utils import bits_to_str
from src.formats.bcd_2421 import (
    add_2421,
    decode_digit_2421,
    decode_number_2421,
    encode_digit_2421,
    encode_number_2421,
)


class Bcd2421Tests(unittest.TestCase):
    def test_digit_encode_decode(self) -> None:
        for digit in range(10):
            encoded = encode_digit_2421(digit)
            self.assertEqual(digit, decode_digit_2421(encoded))

    def test_digit_validation(self) -> None:
        with self.assertRaises(ValueError):
            encode_digit_2421(10)
        with self.assertRaises(ValueError):
            decode_digit_2421([1, 0, 1])
        with self.assertRaises(ValueError):
            decode_digit_2421([0, 1, 1, 0])  # invalid 2421 nibble

    def test_number_encode_decode(self) -> None:
        bits = encode_number_2421(2905)
        self.assertEqual("0010111100001011", bits_to_str(bits))
        self.assertEqual(2905, decode_number_2421(bits))
        self.assertEqual(0, decode_number_2421(encode_number_2421(0)))

    def test_number_validation(self) -> None:
        with self.assertRaises(ValueError):
            encode_number_2421(-1)
        with self.assertRaises(ValueError):
            decode_number_2421([0, 0, 0])

    def test_bcd_add(self) -> None:
        result = add_2421(789, 456)
        self.assertEqual(1245, result.result_decimal)
        self.assertEqual("110111101111", bits_to_str(result.left_bits))
        self.assertIn("result=1245", result.as_text())

    def test_bcd_add_carry_chain(self) -> None:
        result = add_2421(999, 1)
        self.assertEqual(1000, result.result_decimal)
        self.assertEqual("0001000000000000", bits_to_str(result.result_bits))
        with self.assertRaises(ValueError):
            add_2421(-1, 5)


if __name__ == "__main__":
    unittest.main()
