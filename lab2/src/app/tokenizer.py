"""Tokenizer for logical expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

from app.exceptions import EmptyExpressionError, UnknownSymbolError, UnknownVariableError

TokenType: TypeAlias = Literal["NOT", "AND", "OR", "LPAREN", "RPAREN", "VAR", "EOF"]
TokenValue: TypeAlias = str
OperatorDefinition: TypeAlias = tuple[TokenType, TokenValue]

ALLOWED_VARIABLES: frozenset[str] = frozenset({"x1", "x2", "x3"})
OPERATOR_MAP: dict[str, OperatorDefinition] = {
    "!": ("NOT", "!"),
    "~": ("NOT", "!"),
    "¬": ("NOT", "!"),
    "&": ("AND", "&"),
    "*": ("AND", "&"),
    "·": ("AND", "&"),
    "∧": ("AND", "&"),
    "|": ("OR", "|"),
    "+": ("OR", "|"),
    "v": ("OR", "|"),
    "V": ("OR", "|"),
    "∨": ("OR", "|"),
    "(": ("LPAREN", "("),
    ")": ("RPAREN", ")"),
}


@dataclass(frozen=True, slots=True)
class Token:
    """A normalized token produced by the tokenizer."""

    type: TokenType
    value: TokenValue
    position: int


def _read_variable(expression: str, start: int) -> tuple[str, int]:
    """Read and validate a variable token starting at the given position."""

    index = start + 1

    while index < len(expression) and expression[index].isdigit():
        index += 1

    if index == start + 1:
        raise UnknownVariableError("Variable must be one of x1, x2, x3", start)

    variable_name = f"x{expression[start + 1:index]}"
    if variable_name not in ALLOWED_VARIABLES:
        raise UnknownVariableError(f"Unknown variable '{variable_name}'", start)

    return variable_name, index


def tokenize(expression: str) -> list[Token]:
    """Convert a raw expression string into a normalized token sequence."""

    if not expression or not expression.strip():
        raise EmptyExpressionError("Expression is empty")

    tokens: list[Token] = []
    index = 0

    while index < len(expression):
        char = expression[index]

        if char.isspace():
            index += 1
            continue

        if char in OPERATOR_MAP:
            token_type, normalized_value = OPERATOR_MAP[char]
            tokens.append(Token(token_type, normalized_value, index))
            index += 1
            continue

        if char in {"x", "X"}:
            start = index
            variable_name, index = _read_variable(expression, start)
            tokens.append(Token("VAR", variable_name, start))
            continue

        raise UnknownSymbolError(f"Unknown symbol '{char}'", index)

    tokens.append(Token("EOF", "", len(expression)))
    return tokens
