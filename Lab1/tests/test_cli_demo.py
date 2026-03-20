import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src.cli.demo import (
    _read_float,
    _read_int,
    _run_add_interactive,
    _run_bcd_interactive,
    _run_codes_interactive,
    _run_div_interactive,
    _run_ieee_interactive,
    _run_mul_interactive,
    _run_sub_interactive,
    build_parser,
    run_cli,
    run_interactive,
    show_bcd_add,
    show_codes,
    show_ieee,
    show_sign_div,
    show_sign_mul,
    show_twos_add,
    show_twos_sub,
)
from src.cli.operation_factory import OperationFactory, OperationSpec


class CliDemoTests(unittest.TestCase):
    def _capture(self, fn, *args):
        stream = io.StringIO()
        with redirect_stdout(stream):
            fn(*args)
        return stream.getvalue()

    def test_show_functions_print_expected_sections(self) -> None:
        self.assertIn("direct code", self._capture(show_codes, -3))
        self.assertIn("overflow", self._capture(show_twos_add, 5, 7))
        self.assertIn("negated right bits", self._capture(show_twos_sub, 9, 4))
        self.assertIn("Multiplication in sign-magnitude code", self._capture(show_sign_mul, 2, 3))
        self.assertIn("quotient dec", self._capture(show_sign_div, 7, 2))
        self.assertIn("IEEE-754 add", self._capture(show_ieee, "add", 1.0, 2.0))
        self.assertIn("2421 BCD addition", self._capture(show_bcd_add, 8, 9))

    def test_show_ieee_unknown_operation(self) -> None:
        with self.assertRaises(ValueError):
            show_ieee("unknown", 1.0, 2.0)

    def test_parser_construction(self) -> None:
        parser = build_parser()
        self.assertIsNotNone(parser)
        self.assertEqual("codes", parser.parse_args(["codes", "3"]).command)

    def test_run_cli_commands(self) -> None:
        commands = [
            ["prog", "codes", "5"],
            ["prog", "add", "3", "4"],
            ["prog", "sub", "3", "1"],
            ["prog", "mul", "3", "-2"],
            ["prog", "div", "9", "2"],
            ["prog", "ieee", "mul", "1.5", "2.0"],
            ["prog", "bcd-add", "12", "34"],
            ["prog"],
        ]
        for argv in commands:
            with self.subTest(argv=argv):
                output = io.StringIO()
                with patch("sys.argv", argv), redirect_stdout(output):
                    run_cli()
                self.assertTrue(len(output.getvalue()) > 0)

    def test_run_cli_interactive_exit(self) -> None:
        output = io.StringIO()
        with patch("sys.argv", ["prog", "interactive"]), patch("builtins.input", side_effect=["exit"]), redirect_stdout(
            output
        ):
            run_cli()
        self.assertIn("Interactive mode", output.getvalue())

    def test_read_helpers_retry_after_invalid_input(self) -> None:
        output = io.StringIO()
        with patch("builtins.input", side_effect=["oops", " 42 "]), redirect_stdout(output):
            self.assertEqual(42, _read_int("int: "))
        self.assertIn("Ошибка: нужно ввести целое число.", output.getvalue())

        output = io.StringIO()
        with patch("builtins.input", side_effect=["oops", " 3.5 "]), redirect_stdout(output):
            self.assertEqual(3.5, _read_float("float: "))
        self.assertIn("Ошибка: нужно ввести число с плавающей точкой.", output.getvalue())

    def test_interactive_operation_helpers_collect_values(self) -> None:
        cases = [
            (_run_codes_interactive, ["5"], "src.cli.demo.show_codes", (5,)),
            (_run_add_interactive, ["3", "4"], "src.cli.demo.show_twos_add", (3, 4)),
            (_run_sub_interactive, ["9", "2"], "src.cli.demo.show_twos_sub", (9, 2)),
            (_run_mul_interactive, ["-3", "2"], "src.cli.demo.show_sign_mul", (-3, 2)),
            (_run_div_interactive, ["7", "2"], "src.cli.demo.show_sign_div", (7, 2)),
            (_run_ieee_interactive, ["Mul", "1.5", "-2.0"], "src.cli.demo.show_ieee", ("mul", 1.5, -2.0)),
            (_run_bcd_interactive, ["12", "8"], "src.cli.demo.show_bcd_add", (12, 8)),
        ]

        for fn, inputs, target, expected in cases:
            with self.subTest(helper=fn.__name__):
                with patch("builtins.input", side_effect=inputs), patch(target) as mocked:
                    fn()
                mocked.assert_called_once_with(*expected)

    def test_run_interactive_handles_unknown_commands_and_exceptions(self) -> None:
        def boom() -> None:
            raise RuntimeError("boom")

        factory = OperationFactory([OperationSpec("boom", "broken op", lambda _: None, boom)])
        output = io.StringIO()

        with patch("builtins.input", side_effect=["missing", "boom", "exit"]), redirect_stdout(output):
            run_interactive(factory)

        text = output.getvalue()
        self.assertIn("Неизвестная команда. Повторите ввод.", text)
        self.assertIn("Ошибка выполнения команды: boom", text)
        self.assertIn("Интерактивный режим завершен.", text)


if __name__ == "__main__":
    unittest.main()
