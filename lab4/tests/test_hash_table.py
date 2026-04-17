import unittest

from src.errors import DuplicateKeyError, KeyNotFoundError, TableFullError
from src.hash_status import HashStatus
from src.hash_table import HashTable


class HashTableTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.table = HashTable(size=11)

    def test_properties_reflect_table_state(self) -> None:
        self.assertEqual(self.table.size, 11)
        self.assertEqual(self.table.count, 0)
        self.assertEqual(len(self.table), 0)

    def test_insert_without_collisions(self) -> None:
        index_one = self.table.insert("АА", "значение 1")
        index_two = self.table.insert("АБ", "значение 2")
        first_entry = self.table.get_entry(index_one)
        second_entry = self.table.get_entry(index_two)

        self.assertEqual(index_one, 0)
        self.assertEqual(index_two, 1)
        self.assertEqual(self.table.search("АА"), "значение 1")
        self.assertEqual(self.table.search("АБ"), "значение 2")
        self.assertEqual(first_entry.id_word, "АА")
        self.assertEqual(first_entry.c, 0)
        self.assertEqual(first_entry.u, 1)
        self.assertEqual(first_entry.t, 1)
        self.assertEqual(first_entry.l, 0)
        self.assertEqual(first_entry.d, 0)
        self.assertIsNone(first_entry.p0)
        self.assertEqual(first_entry.pi, "значение 1")
        self.assertEqual(second_entry.c, 0)

    def test_insert_with_collisions_uses_quadratic_probing_first(self) -> None:
        first_index = self.table.insert("АБРИКОС", "фрукт")
        second_index = self.table.insert("АБАЖУР", "лампа")
        third_index = self.table.insert("АБОРДАЖ", "термин")
        second_entry = self.table.get_entry(second_index)
        third_entry = self.table.get_entry(third_index)

        self.assertEqual(first_index, 1)
        self.assertEqual(second_index, 2)
        self.assertEqual(third_index, 5)
        self.assertEqual(self.table.search("АБОРДАЖ"), "термин")
        self.assertEqual(second_entry.c, 1)
        self.assertEqual(third_entry.c, 1)
        self.assertEqual(second_entry.u, 1)
        self.assertEqual(third_entry.t, 1)

    def test_insert_uses_fallback_scan_when_quadratic_sequence_repeats(self) -> None:
        colliding_keys = [
            "АБРИКОС",
            "АБАЖУР",
            "АБОРДАЖ",
            "АБСУРД",
            "АБЗАЦ",
            "АББАТ",
            "АББРЕВИАТУРА",
        ]

        inserted_indexes = [self.table.insert(key, number) for number, key in enumerate(colliding_keys, start=1)]

        self.assertEqual(inserted_indexes[:6], [1, 2, 5, 10, 6, 4])
        self.assertEqual(inserted_indexes[6], 3)
        self.assertEqual(self.table.search("АББРЕВИАТУРА"), 7)
        self.assertEqual(self.table.count, 7)

    def test_search_existing_key_returns_value(self) -> None:
        self.table.insert("БАНАН", "желтый")
        self.assertEqual(self.table.search("БАНАН"), "желтый")

    def test_search_missing_key_raises_error(self) -> None:
        with self.assertRaises(KeyNotFoundError):
            self.table.search("ВИШНЯ")

    def test_update_existing_key_changes_value(self) -> None:
        self.table.insert("БАНАН", "желтый")
        updated_index = self.table.update("БАНАН", "спелый")

        self.assertEqual(self.table.search("БАНАН"), "спелый")
        self.assertEqual(updated_index, 0)

    def test_delete_existing_key_marks_slot_deleted(self) -> None:
        self.table.insert("АБРИКОС", "фрукт")
        removed_value = self.table.delete("АБРИКОС")
        deleted_entry = self.table.get_entry(1)

        self.assertEqual(removed_value, "фрукт")
        self.assertEqual(self.table.count, 0)
        self.assertEqual(deleted_entry.status, HashStatus.DELETED)
        self.assertEqual(deleted_entry.id_word, "АБРИКОС")
        self.assertEqual(deleted_entry.pi, "фрукт")
        self.assertEqual(deleted_entry.u, 0)
        self.assertEqual(deleted_entry.d, 1)
        self.assertEqual(deleted_entry.t, 0)

        with self.assertRaises(KeyNotFoundError):
            self.table.search("АБРИКОС")

    def test_search_continues_after_deleted_slot(self) -> None:
        self.table.insert("АБРИКОС", "фрукт")
        self.table.insert("АБАЖУР", "лампа")
        self.table.insert("АБОРДАЖ", "термин")
        self.table.delete("АБАЖУР")

        self.assertEqual(self.table.search("АБОРДАЖ"), "термин")

    def test_insert_reuses_deleted_slot(self) -> None:
        self.table.insert("АБРИКОС", "фрукт")
        self.table.insert("АБАЖУР", "лампа")
        self.table.delete("АБРИКОС")

        reused_index = self.table.insert("АБСУРД", "повторная вставка")
        reused_entry = self.table.get_entry(reused_index)

        self.assertEqual(reused_index, 1)
        self.assertEqual(self.table.search("АБСУРД"), "повторная вставка")
        self.assertEqual(reused_entry.id_word, "АБСУРД")
        self.assertEqual(reused_entry.d, 0)
        self.assertEqual(reused_entry.u, 1)

    def test_insert_detects_duplicate_key_after_normalization(self) -> None:
        self.table.insert("груша", "значение")

        with self.assertRaises(DuplicateKeyError):
            self.table.insert(" ГРУША ", "дубликат")

    def test_table_full_raises_error_only_when_table_has_no_free_slots(self) -> None:
        full_table = HashTable(size=3)
        full_table.insert("АА", 1)
        full_table.insert("АБ", 2)
        full_table.insert("АВ", 3)

        with self.assertRaises(TableFullError):
            full_table.insert("АГ", 4)

    def test_load_factor_and_length_are_calculated_correctly(self) -> None:
        self.table.insert("АА", 1)
        self.table.insert("АБ", 2)
        self.table.insert("АВ", 3)

        self.assertEqual(len(self.table), 3)
        self.assertAlmostEqual(self.table.get_load_factor(), 3 / 11)

    def test_display_returns_human_readable_table_state(self) -> None:
        self.table.insert("АА", "пусто")
        self.table.insert("АБ", "занято")
        self.table.delete("АА")

        table_view = self.table.display()

        self.assertIn("HashTable(size=11, count=1", table_view)
        self.assertIn("idx | ID | C | U | T | L | D | P0 | Pi", table_view)
        self.assertIn("0 | АА", table_view)
        self.assertIn("1 | АБ", table_view)
        self.assertIn("| 0 | 1 | 1 | 0 | 0 | None | занято", table_view)

    def test_display_table_alias_and_string_conversion_return_same_text(self) -> None:
        self.table.insert("АА", "значение")
        self.assertEqual(self.table.display_table(), self.table.display())
        self.assertEqual(str(self.table), self.table.display())


if __name__ == "__main__":
    unittest.main()
