import importlib
import runpy
import unittest
from unittest.mock import patch

import src.main


class MainEntrypointTests(unittest.TestCase):
    def test_main_calls_cli(self) -> None:
        with patch("src.main.run_cli") as mocked:
            src.main.main()
            mocked.assert_called_once()

    def test_package_modules_reload_cleanly(self) -> None:
        for module_name in ["src", "src.cli", "src.codes", "src.formats", "src.operations"]:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIs(module, importlib.reload(module))

    def test_python_module_entrypoint_calls_main(self) -> None:
        with patch("src.main.main") as mocked:
            runpy.run_module("src.__main__", run_name="__main__")
            mocked.assert_called_once()


if __name__ == "__main__":
    unittest.main()
