import unittest

from src.errors import InvalidKeyError, InvalidTableSizeError, KeyNotFoundError
from src.hash_entry import HashEntry
from src.hash_status import HashStatus
from src.hash_table import HashTable


class EdgeCasesTestCase(unittest.TestCase):
    def test_hash_table_rejects_invalid_size(self) -> None:
        with self.assertRaises(InvalidTableSizeError):
            HashTable(0)

        with self.assertRaises(InvalidTableSizeError):
            HashTable(True)

    def test_non_string_key_is_rejected(self) -> None:
        table = HashTable(11)
        with self.assertRaises(InvalidKeyError):
            table.insert(123, "значение")

    def test_too_short_key_is_rejected(self) -> None:
        table = HashTable(11)
        with self.assertRaises(InvalidKeyError):
            table.insert("А", "значение")

    def test_key_with_invalid_characters_is_rejected(self) -> None:
        table = HashTable(11)
        with self.assertRaises(InvalidKeyError):
            table.insert("AБ", "значение")

    def test_update_missing_key_raises_error(self) -> None:
        table = HashTable(11)
        with self.assertRaises(KeyNotFoundError):
            table.update("АБ", "значение")

    def test_delete_missing_key_raises_error(self) -> None:
        table = HashTable(11)
        with self.assertRaises(KeyNotFoundError):
            table.delete("АБ")

    def test_deleted_slot_is_reused_when_no_empty_cells_left(self) -> None:
        table = HashTable(11)
        keys = ["АА", "АБ", "АВ", "АГ", "АД", "АЕ", "АЁ", "АЖ", "АЗ", "АИ", "АЙ"]

        for number, key in enumerate(keys):
            table.insert(key, number)

        table.delete("АБ")
        reused_index = table.insert("ББ", "новое значение")

        self.assertEqual(reused_index, 1)
        self.assertEqual(table.search("ББ"), "новое значение")

    def test_hash_entry_status_value_and_string_representation(self) -> None:
        entry = HashEntry()
        self.assertEqual(entry.status, HashStatus.EMPTY)
        self.assertIsNone(entry.key)
        self.assertIsNone(entry.value)
        self.assertEqual(
            str(entry),
            "ID=None, C=0, U=0, T=0, L=0, D=0, P0=None, Pi=None",
        )

        entry.occupy("АБ", "значение", collision=True)
        self.assertEqual(entry.status, HashStatus.OCCUPIED)
        self.assertEqual(entry.key, "АБ")
        self.assertEqual(entry.value, "значение")
        entry.value = "обновленное значение"
        self.assertEqual(entry.value, "обновленное значение")
        self.assertEqual(
            str(entry),
            "ID=АБ, C=1, U=1, T=1, L=0, D=0, P0=None, Pi=обновленное значение",
        )

        entry.mark_deleted()
        self.assertEqual(entry.status, HashStatus.DELETED)
        self.assertEqual(entry.u, 0)
        self.assertEqual(entry.d, 1)
        self.assertEqual(
            str(entry),
            "ID=АБ, C=1, U=0, T=0, L=0, D=1, P0=None, Pi=обновленное значение",
        )


if __name__ == "__main__":
    unittest.main()
