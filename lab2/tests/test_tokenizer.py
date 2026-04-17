"""Tests for the tokenizer."""

from __future__ import annotations

import pytest

from app.exceptions import EmptyExpressionError, UnknownSymbolError, UnknownVariableError
from app.tokenizer import tokenize


def summarize_tokens(expression: str) -> list[tuple[str, str]]:
    """Convert tokens to a compact type/value summary."""

    return [(token.type, token.value) for token in tokenize(expression)]


def test_tokenizer_normalizes_supported_operators() -> None:
    assert summarize_tokens("¬(x1·x2)+x3") == [
        ("NOT", "!"),
        ("LPAREN", "("),
        ("VAR", "x1"),
        ("AND", "&"),
        ("VAR", "x2"),
        ("RPAREN", ")"),
        ("OR", "|"),
        ("VAR", "x3"),
        ("EOF", ""),
    ]


def test_tokenizer_supports_compact_form_without_spaces() -> None:
    assert summarize_tokens("X1v~x2") == [
        ("VAR", "x1"),
        ("OR", "|"),
        ("NOT", "!"),
        ("VAR", "x2"),
        ("EOF", ""),
    ]


def test_tokenizer_rejects_empty_expression() -> None:
    with pytest.raises(EmptyExpressionError):
        tokenize("   ")


def test_tokenizer_rejects_unknown_symbol() -> None:
    with pytest.raises(UnknownSymbolError):
        tokenize("x1 ^ x2")


def test_tokenizer_rejects_unknown_variable() -> None:
    with pytest.raises(UnknownVariableError):
        tokenize("x4 | x1")
