"""Custom exceptions used across the project."""

from __future__ import annotations


class LogicLabError(Exception):
    """Base application exception."""


class ValidationError(LogicLabError):
    """Raised when high-level validation fails."""


class TokenizationError(LogicLabError):
    """Raised when the tokenizer cannot process the input string."""

    def __init__(self, message: str, position: int | None = None) -> None:
        if position is not None:
            message = f"{message} at position {position}"
        super().__init__(message)
        self.position = position


class ParseError(LogicLabError):
    """Raised when the token stream cannot be parsed into an AST."""

    def __init__(self, message: str, position: int | None = None) -> None:
        if position is not None:
            message = f"{message} at position {position}"
        super().__init__(message)
        self.position = position


class EvaluationError(LogicLabError):
    """Raised when an expression cannot be evaluated."""
