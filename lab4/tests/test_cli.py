import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import cli
from src.hash_table import HashTable


class CLITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.table = HashTable(size=11)

    def _run_command(self, command: str, inputs: list[str] | None = None) -> tuple[bool, str]:
        output = io.StringIO()
        input_values = inputs or []

        with patch("builtins.input", side_effect=input_values), redirect_stdout(output):
            should_continue = cli.handle_command(self.table, command)

        return should_continue, output.getvalue()

    def test_print_menu_outputs_all_items(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            cli.print_menu()

        rendered = output.getvalue()
        self.assertIn("1. Добавить элемент", rendered)
        self.assertIn("5. Показать таблицу", rendered)
        self.assertIn("0. Выход", rendered)

    def test_format_public_table_hides_internal_flags(self) -> None:
        self.table.insert("АБ", "значение")
        rendered = cli.format_public_table(self.table)

        self.assertIn("Индекс | Ключ | Значение", rendered)
        self.assertIn("1 | АБ | значение", rendered)
        self.assertIn("0 | - | -", rendered)
        self.assertNotIn("C=", rendered)
        self.assertNotIn("U=", rendered)

    def test_handle_command_insert_adds_item(self) -> None:
        should_continue, rendered = self._run_command("1", ["АБ", "лампа"])

        self.assertTrue(should_continue)
        self.assertEqual(self.table.search("АБ"), "лампа")
        self.assertIn("Элемент успешно добавлен", rendered)

    def test_handle_command_insert_handles_duplicate_key(self) -> None:
        self.table.insert("АБ", "лампа")

        should_continue, rendered = self._run_command("1", ["АБ", "дубликат"])

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: такой ключ уже существует.", rendered)

    def test_handle_command_insert_handles_full_table(self) -> None:
        small_table = HashTable(size=1)
        small_table.insert("АА", "первый")
        output = io.StringIO()

        with patch("builtins.input", side_effect=["АБ", "второй"]), redirect_stdout(output):
            should_continue = cli.handle_command(small_table, "1")

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: таблица заполнена.", output.getvalue())

    def test_handle_command_insert_handles_validation_error(self) -> None:
        should_continue, rendered = self._run_command("1", ["AБ", "лампа"])

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: Key must contain only Russian letters.", rendered)

    def test_handle_command_search_prints_value(self) -> None:
        self.table.insert("АБ", "лампа")

        should_continue, rendered = self._run_command("2", ["АБ"])

        self.assertTrue(should_continue)
        self.assertIn("Найдено значение: лампа", rendered)

    def test_handle_command_search_prints_not_found_message(self) -> None:
        should_continue, rendered = self._run_command("2", ["АБ"])

        self.assertTrue(should_continue)
        self.assertIn("Элемент не найден.", rendered)

    def test_handle_command_search_handles_validation_error(self) -> None:
        should_continue, rendered = self._run_command("2", ["AБ"])

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: Key must contain only Russian letters.", rendered)

    def test_handle_command_update_changes_value(self) -> None:
        self.table.insert("АБ", "старое")

        should_continue, rendered = self._run_command("3", ["АБ", "новое"])

        self.assertTrue(should_continue)
        self.assertEqual(self.table.search("АБ"), "новое")
        self.assertIn("Элемент обновлен", rendered)

    def test_handle_command_update_prints_missing_key_message(self) -> None:
        should_continue, rendered = self._run_command("3", ["АБ", "новое"])

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: ключ не найден.", rendered)

    def test_handle_command_update_handles_validation_error(self) -> None:
        should_continue, rendered = self._run_command("3", ["AБ", "новое"])

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: Key must contain only Russian letters.", rendered)

    def test_handle_command_delete_removes_item(self) -> None:
        self.table.insert("АБ", "лампа")

        should_continue, rendered = self._run_command("4", ["АБ"])

        self.assertTrue(should_continue)
        self.assertIn("Элемент удален", rendered)

    def test_handle_command_delete_prints_missing_key_message(self) -> None:
        should_continue, rendered = self._run_command("4", ["АБ"])

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: ключ не найден.", rendered)

    def test_handle_command_delete_handles_validation_error(self) -> None:
        should_continue, rendered = self._run_command("4", ["AБ"])

        self.assertTrue(should_continue)
        self.assertIn("Ошибка: Key must contain only Russian letters.", rendered)

    def test_handle_command_show_prints_public_table(self) -> None:
        self.table.insert("АБ", "лампа")
        output = io.StringIO()

        with redirect_stdout(output):
            should_continue = cli.handle_command(self.table, "5")

        self.assertTrue(should_continue)
        self.assertIn("Индекс | Ключ | Значение", output.getvalue())
        self.assertIn("1 | АБ | лампа", output.getvalue())

    def test_handle_command_load_factor_prints_ratio(self) -> None:
        self.table.insert("АБ", "лампа")
        output = io.StringIO()

        with redirect_stdout(output):
            should_continue = cli.handle_command(self.table, "6")

        self.assertTrue(should_continue)
        self.assertIn("Коэффициент заполнения: 0.09", output.getvalue())

    def test_handle_command_strips_whitespace_from_choice(self) -> None:
        should_continue, rendered = self._run_command(" 0 ")

        self.assertFalse(should_continue)
        self.assertIn("Завершение работы.", rendered)

    def test_handle_command_handles_unknown_choice(self) -> None:
        should_continue, rendered = self._run_command("abc")

        self.assertTrue(should_continue)
        self.assertIn("Некорректная команда", rendered)

    def test_handle_command_exit_stops_loop(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            should_continue = cli.handle_command(self.table, "0")

        self.assertFalse(should_continue)
        self.assertIn("Завершение работы.", output.getvalue())

    def test_run_cli_processes_commands_until_exit(self) -> None:
        output = io.StringIO()
        inputs = ["1", "АБ", "лампа", "5", "0"]

        with patch("builtins.input", side_effect=inputs), redirect_stdout(output):
            cli.run_cli(self.table)

        rendered = output.getvalue()
        self.assertIn("Консольный интерфейс для работы с хеш-таблицей.", rendered)
        self.assertIn("Элемент успешно добавлен", rendered)
        self.assertIn("1 | АБ | лампа", rendered)
        self.assertIn("Завершение работы.", rendered)


if __name__ == "__main__":
    unittest.main()
