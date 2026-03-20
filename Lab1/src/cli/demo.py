"""CLI demo for manual numeric-code algorithms."""

from __future__ import annotations

import argparse
from typing import Callable, Final

from src.bit_utils import bits_to_str
from src.cli.operation_factory import OperationFactory, OperationSpec
from src.codes.signed_codes import build_code_triplet
from src.formats.bcd_2421 import add_2421
from src.formats.ieee754_32 import (
    Float32OperationResult,
    add_decimal as ieee_add_decimal,
    divide_decimal as ieee_divide_decimal,
    multiply_decimal as ieee_multiply_decimal,
    subtract_decimal as ieee_subtract_decimal,
)
from src.operations.sign_magnitude_arithmetic import divide_in_sign_magnitude, multiply_in_sign_magnitude
from src.operations.twos_complement_arithmetic import add_in_twos_complement, subtract_in_twos_complement

IeeeHandler = Callable[[float, float], Float32OperationResult]

_IEEE_HANDLERS: Final[dict[str, tuple[IeeeHandler, str]]] = {
    "add": (ieee_add_decimal, "IEEE-754 add"),
    "sub": (ieee_subtract_decimal, "IEEE-754 subtract"),
    "mul": (ieee_multiply_decimal, "IEEE-754 multiply"),
    "div": (ieee_divide_decimal, "IEEE-754 divide"),
}


def _print_header(title: str) -> None:
    print(f"\n=== {title} ===")


def _read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: нужно ввести целое число.")


def _read_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Ошибка: нужно ввести число с плавающей точкой.")


def show_codes(value: int) -> None:
    triplet = build_code_triplet(value)
    _print_header("Decimal to direct/inverse/additional codes")
    print(f"decimal: {triplet.decimal}")
    print(f"direct code:      {bits_to_str(triplet.sign_magnitude)}")
    print(f"inverse code:     {bits_to_str(triplet.ones_complement)}")
    print(f"additional code:  {bits_to_str(triplet.twos_complement)}")


def show_twos_add(left: int, right: int) -> None:
    result = add_in_twos_complement(left, right)
    _print_header("Addition in two's complement")
    print(f"left decimal:  {left}")
    print(f"right decimal: {right}")
    print(f"left bits:     {bits_to_str(result.left_bits)}")
    print(f"right bits:    {bits_to_str(result.right_bits)}")
    print(f"result bits:   {bits_to_str(result.result_bits)}")
    print(f"result dec:    {result.result_decimal}")
    print(f"overflow:      {result.overflow}")


def show_twos_sub(left: int, right: int) -> None:
    result = subtract_in_twos_complement(left, right)
    _print_header("Subtraction in two's complement (a + (-b))")
    print(f"left decimal:      {left}")
    print(f"right decimal:     {right}")
    print(f"left bits:         {bits_to_str(result.left_bits)}")
    print(f"negated right bits:{bits_to_str(result.right_bits)}")
    print(f"result bits:       {bits_to_str(result.result_bits)}")
    print(f"result dec:        {result.result_decimal}")
    print(f"overflow:          {result.overflow}")


def show_sign_mul(left: int, right: int) -> None:
    result = multiply_in_sign_magnitude(left, right)
    _print_header("Multiplication in sign-magnitude code")
    print(f"left decimal:  {left}")
    print(f"right decimal: {right}")
    print(f"left bits:     {bits_to_str(result.left_bits)}")
    print(f"right bits:    {bits_to_str(result.right_bits)}")
    print(f"result bits:   {bits_to_str(result.result_bits)}")
    print(f"result dec:    {result.result_decimal}")
    print(f"overflow:      {result.overflow}")


def show_sign_div(left: int, right: int) -> None:
    result = divide_in_sign_magnitude(left, right)
    _print_header("Division in sign-magnitude code")
    print(f"left decimal:   {left}")
    print(f"right decimal:  {right}")
    print(f"left bits:      {bits_to_str(result.left_bits)}")
    print(f"right bits:     {bits_to_str(result.right_bits)}")
    print(f"quotient bits:  {bits_to_str(result.quotient_bits)}")
    print(f"quotient binary:{result.quotient_binary}")
    print(f"quotient dec:   {result.quotient_decimal}")
    print(f"remainder dec:  {result.remainder_decimal}")


def show_ieee(op: str, left: float, right: float) -> None:
    operation = _IEEE_HANDLERS.get(op)
    if operation is None:
        raise ValueError(f"unknown IEEE op: {op}")
    operation_fn, title = operation
    result = operation_fn(left, right)

    _print_header(title)
    print(f"left decimal:  {left}")
    print(f"right decimal: {right}")
    print(f"left bits:     {bits_to_str(result.left_bits)}")
    print(f"right bits:    {bits_to_str(result.right_bits)}")
    print(f"result bits:   {bits_to_str(result.result_bits)}")
    print(f"result dec:    {result.result_decimal}")


def show_bcd_add(left: int, right: int) -> None:
    result = add_2421(left, right)
    _print_header("2421 BCD addition")
    print(f"left decimal:  {left}")
    print(f"right decimal: {right}")
    print(f"left bits:     {bits_to_str(result.left_bits)}")
    print(f"right bits:    {bits_to_str(result.right_bits)}")
    print(f"result bits:   {bits_to_str(result.result_bits)}")
    print(f"result dec:    {result.result_decimal}")


def _handle_codes_namespace(namespace: argparse.Namespace) -> None:
    show_codes(namespace.value)


def _handle_add_namespace(namespace: argparse.Namespace) -> None:
    show_twos_add(namespace.left, namespace.right)


def _handle_sub_namespace(namespace: argparse.Namespace) -> None:
    show_twos_sub(namespace.left, namespace.right)


def _handle_mul_namespace(namespace: argparse.Namespace) -> None:
    show_sign_mul(namespace.left, namespace.right)


def _handle_div_namespace(namespace: argparse.Namespace) -> None:
    show_sign_div(namespace.left, namespace.right)


def _handle_ieee_namespace(namespace: argparse.Namespace) -> None:
    show_ieee(namespace.op, namespace.left, namespace.right)


def _handle_bcd_namespace(namespace: argparse.Namespace) -> None:
    show_bcd_add(namespace.left, namespace.right)


def _run_codes_interactive() -> None:
    value = _read_int("Введите десятичное число: ")
    show_codes(value)


def _run_add_interactive() -> None:
    left = _read_int("Введите первое целое число: ")
    right = _read_int("Введите второе целое число: ")
    show_twos_add(left, right)


def _run_sub_interactive() -> None:
    left = _read_int("Введите уменьшаемое: ")
    right = _read_int("Введите вычитаемое: ")
    show_twos_sub(left, right)


def _run_mul_interactive() -> None:
    left = _read_int("Введите первый множитель: ")
    right = _read_int("Введите второй множитель: ")
    show_sign_mul(left, right)


def _run_div_interactive() -> None:
    left = _read_int("Введите делимое: ")
    right = _read_int("Введите делитель: ")
    show_sign_div(left, right)


def _run_ieee_interactive() -> None:
    op = input("Введите IEEE-операцию (add/sub/mul/div): ").strip().lower()
    left = _read_float("Введите первое число: ")
    right = _read_float("Введите второе число: ")
    show_ieee(op, left, right)


def _run_bcd_interactive() -> None:
    left = _read_int("Введите первое неотрицательное число: ")
    right = _read_int("Введите второе неотрицательное число: ")
    show_bcd_add(left, right)


def _build_operation_factory() -> OperationFactory:
    specs = [
        OperationSpec("codes", "decimal -> direct/inverse/additional", _handle_codes_namespace, _run_codes_interactive),
        OperationSpec("add", "two's complement add", _handle_add_namespace, _run_add_interactive),
        OperationSpec("sub", "two's complement subtract", _handle_sub_namespace, _run_sub_interactive),
        OperationSpec("mul", "sign-magnitude multiply", _handle_mul_namespace, _run_mul_interactive),
        OperationSpec("div", "sign-magnitude divide", _handle_div_namespace, _run_div_interactive),
        OperationSpec("ieee", "IEEE-754 operation", _handle_ieee_namespace, _run_ieee_interactive),
        OperationSpec("bcd-add", "BCD 2421 addition", _handle_bcd_namespace, _run_bcd_interactive),
    ]
    return OperationFactory(specs)


def run_interactive(factory: OperationFactory) -> None:
    _print_header("Interactive mode")
    print("Доступные операции:")
    for spec in factory.interactive_specs():
        print(f"  - {spec.key}: {spec.title}")
    print("  - exit: завершить работу")

    while True:
        command = input("\nВведите команду: ").strip().lower()
        if command in {"exit", "quit", "q"}:
            print("Интерактивный режим завершен.")
            return

        handler = factory.interactive_handler(command)
        if handler is None:
            print("Неизвестная команда. Повторите ввод.")
            continue

        try:
            handler()
        except Exception as error:  # noqa: BLE001 - interactive mode must stay alive
            print(f"Ошибка выполнения команды: {error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manual number codes and arithmetic demo")
    sub = parser.add_subparsers(dest="command")

    codes = sub.add_parser("codes", help="decimal to direct/inverse/additional codes")
    codes.add_argument("value", type=int)

    add = sub.add_parser("add", help="add in two's complement")
    add.add_argument("left", type=int)
    add.add_argument("right", type=int)

    sub_cmd = sub.add_parser("sub", help="subtract in two's complement")
    sub_cmd.add_argument("left", type=int)
    sub_cmd.add_argument("right", type=int)

    mul = sub.add_parser("mul", help="multiply in sign-magnitude")
    mul.add_argument("left", type=int)
    mul.add_argument("right", type=int)

    div = sub.add_parser("div", help="divide in sign-magnitude")
    div.add_argument("left", type=int)
    div.add_argument("right", type=int)

    ieee = sub.add_parser("ieee", help="IEEE-754 operation")
    ieee.add_argument("op", choices=["add", "sub", "mul", "div"])
    ieee.add_argument("left", type=float)
    ieee.add_argument("right", type=float)

    bcd = sub.add_parser("bcd-add", help="add in BCD 2421")
    bcd.add_argument("left", type=int)
    bcd.add_argument("right", type=int)

    sub.add_parser("interactive", help="interactive mode with user input")
    return parser


def run_cli() -> None:
    parser = build_parser()
    args = parser.parse_args()
    factory = _build_operation_factory()

    if args.command == "interactive":
        run_interactive(factory)
        return

    handler = factory.namespace_handler(args.command)
    if handler is None:
        parser.print_help()
        return
    handler(args)

