"""Custom exceptions for the logic algebra application."""

from __future__ import annotations


def _attach_position(message: str, position: int | None) -> str:
    """Attach a character position to an error message when available."""

    if position is None:
        return message
    return f"{message} at position {position}"


class LogicLabError(Exception):
    """Base exception for all domain-specific errors."""


class TokenizerError(LogicLabError):
    """Base exception for tokenizer failures."""

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(_attach_position(message, position))
        self.position = position


class EmptyExpressionError(TokenizerError):
    """Raised when the input expression is empty."""


class UnknownSymbolError(TokenizerError):
    """Raised when the tokenizer encounters an unsupported symbol."""


class UnknownVariableError(TokenizerError):
    """Raised when the tokenizer encounters an unsupported variable name."""


class ParserError(LogicLabError):
    """Base exception for parser failures."""

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(_attach_position(message, position))
        self.position = position


class UnexpectedTokenError(ParserError):
    """Raised when token order does not match the grammar."""


class MissingParenthesisError(ParserError):
    """Raised when a closing parenthesis is missing."""


class TrailingTokensError(ParserError):
    """Raised when extra tokens remain after successful parsing."""


class EvaluationError(LogicLabError):
    """Raised when expression evaluation cannot be completed."""
