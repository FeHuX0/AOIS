import unittest
from unittest.mock import patch

import main
from src.hash_table import HashTable


class MainModuleTestCase(unittest.TestCase):
    @patch("main.run_cli")
    def test_main_creates_default_table_and_starts_cli(self, run_cli_mock) -> None:
        main.main()

        run_cli_mock.assert_called_once()
        table = run_cli_mock.call_args.args[0]
        self.assertIsInstance(table, HashTable)
        self.assertEqual(table.size, main.DEFAULT_TABLE_SIZE)


if __name__ == "__main__":
    unittest.main()
