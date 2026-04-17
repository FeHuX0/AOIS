"""Tokenizer for logical expressions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import unicodedata

from utils.constants import ALLOWED_VARIABLES
from utils.exceptions import TokenizationError


class TokenType(str, Enum):
    """Supported token types."""

    VARIABLE = "VARIABLE"
    CONSTANT = "CONSTANT"
    NOT = "NOT"
    AND = "AND"
    OR = "OR"
    IMPLIES = "IMPLIES"
    EQUIVALENT = "EQUIVALENT"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


@dataclass(frozen=True, slots=True)
class Token:
    """A lexical token."""

    type: TokenType
    value: str
    position: int


@dataclass(frozen=True, slots=True)
class _OperatorMatch:
    """Internal operator match result."""

    token: Token
    next_position: int


class Tokenizer:
    """Convert an input string into a sequence of tokens."""

    _OPERATORS: tuple[tuple[str, TokenType, str], ...] = (
        ("<->", TokenType.EQUIVALENT, "~"),
        ("->", TokenType.IMPLIES, "->"),
        ("\u2194", TokenType.EQUIVALENT, "~"),
        ("\u2261", TokenType.EQUIVALENT, "~"),
        ("\u2192", TokenType.IMPLIES, "->"),
        ("\u21d2", TokenType.IMPLIES, "->"),
        ("\u00ac", TokenType.NOT, "!"),
        ("!", TokenType.NOT, "!"),
        ("\u2227", TokenType.AND, "&"),
        ("&", TokenType.AND, "&"),
        ("\u00b7", TokenType.AND, "&"),
        ("*", TokenType.AND, "&"),
        ("\u2228", TokenType.OR, "|"),
        ("|", TokenType.OR, "|"),
        ("+", TokenType.OR, "|"),
        ("~", TokenType.EQUIVALENT, "~"),
        ("(", TokenType.LPAREN, "("),
        (")", TokenType.RPAREN, ")"),
    )

    def tokenize(self, expression: str) -> list[Token]:
        """Tokenize a logical expression."""

        if not expression or not expression.strip():
            raise TokenizationError("Expression cannot be empty")

        normalized_expression = unicodedata.normalize("NFKC", expression)
        tokens: list[Token] = []
        index = 0
        while index < len(normalized_expression):
            symbol = normalized_expression[index]

            if symbol.isspace():
                index += 1
                continue

            operator_token = self._match_operator(normalized_expression, index)
            if operator_token is not None:
                tokens.append(operator_token.token)
                index = operator_token.next_position
                continue

            if symbol in {"0", "1"}:
                tokens.append(Token(TokenType.CONSTANT, symbol, index))
                index += 1
                continue

            if symbol.isalpha():
                name = symbol.lower()
                if name not in ALLOWED_VARIABLES:
                    allowed = ", ".join(ALLOWED_VARIABLES)
                    raise TokenizationError(
                        f"Unsupported variable '{symbol}'. Allowed variables: {allowed}",
                        index,
                    )
                tokens.append(Token(TokenType.VARIABLE, name, index))
                index += 1
                continue

            raise TokenizationError(f"Unsupported symbol '{symbol}'", index)

        tokens.append(Token(TokenType.EOF, "", len(normalized_expression)))
        return tokens

    def _match_operator(self, expression: str, index: int) -> _OperatorMatch | None:
        """Return a matched operator token if the input starts with one."""

        for raw_symbol, token_type, normalized_value in self._OPERATORS:
            if expression.startswith(raw_symbol, index):
                return _OperatorMatch(
                    token=Token(token_type, normalized_value, index),
                    next_position=index + len(raw_symbol),
                )
        return None
