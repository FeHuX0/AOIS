import unittest

from src.errors import InvalidKeyError, InvalidTableSizeError
from src.hash_utils import (
    ALPHABET_SIZE,
    calculate_hash,
    calculate_v,
    get_letter_index,
    normalize_key,
    validate_table_size,
)


class HashUtilsTestCase(unittest.TestCase):
    def test_normalize_key_strips_spaces_and_converts_to_uppercase(self) -> None:
        self.assertEqual(normalize_key("  абрикос "), "АБРИКОС")

    def test_calculate_v_uses_first_two_letters(self) -> None:
        self.assertEqual(calculate_v("АБРИКОС"), 1)
        self.assertEqual(calculate_v("БА"), ALPHABET_SIZE)

    def test_calculate_hash_uses_modulo_and_base(self) -> None:
        self.assertEqual(calculate_hash(67, 11), 1)
        self.assertEqual(calculate_hash(67, 11, 3), 4)
        self.assertEqual(calculate_hash(10, 11, 14), 2)

    def test_get_letter_index_returns_position_in_russian_alphabet(self) -> None:
        self.assertEqual(get_letter_index("А"), 0)
        self.assertEqual(get_letter_index("Ё"), 6)
        self.assertEqual(get_letter_index("Я"), 32)

    def test_get_letter_index_rejects_invalid_input(self) -> None:
        with self.assertRaises(InvalidKeyError):
            get_letter_index("A")

        with self.assertRaises(InvalidKeyError):
            get_letter_index("АБ")

    def test_normalize_key_rejects_short_key(self) -> None:
        with self.assertRaises(InvalidKeyError):
            normalize_key("А")

    def test_normalize_key_rejects_non_russian_letters(self) -> None:
        with self.assertRaises(InvalidKeyError):
            normalize_key("AБ")

    def test_normalize_key_accepts_letter_yo(self) -> None:
        self.assertEqual(normalize_key("ёж"), "ЁЖ")

    def test_validate_table_size_rejects_non_positive_values(self) -> None:
        with self.assertRaises(InvalidTableSizeError):
            validate_table_size(0)

        with self.assertRaises(InvalidTableSizeError):
            validate_table_size(-5)

    def test_validate_table_size_rejects_non_integer_values(self) -> None:
        with self.assertRaises(InvalidTableSizeError):
            validate_table_size(3.5)

        with self.assertRaises(InvalidTableSizeError):
            validate_table_size(True)

    def test_calculate_hash_rejects_invalid_arguments(self) -> None:
        with self.assertRaises(ValueError):
            calculate_hash("10", 11)

        with self.assertRaises(ValueError):
            calculate_hash(10, 11, False)


if __name__ == "__main__":
    unittest.main()
