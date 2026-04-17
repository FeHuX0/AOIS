"""Recursive descent parser for logical expressions."""

from __future__ import annotations

from collections.abc import Callable

from app.ast_nodes import Expression
from app.expression_factory import DefaultExpressionFactory, ExpressionFactory
from app.exceptions import MissingParenthesisError, TrailingTokensError, UnexpectedTokenError
from app.tokenizer import Token, tokenize

OperandParser = Callable[[], Expression]
BinaryNodeFactory = Callable[[Expression, Expression], Expression]


class Parser:
    """Parse a token sequence into an AST."""

    def __init__(
        self,
        tokens: list[Token],
        factory: ExpressionFactory | None = None,
    ) -> None:
        self.tokens = tokens
        self.position = 0
        self.factory = factory or DefaultExpressionFactory()

    @property
    def current(self) -> Token:
        """Return the current token."""

        return self.tokens[self.position]

    def consume(self, token_type: str) -> Token | None:
        """Consume and return the current token if it matches the expected type."""

        if self.current.type != token_type:
            return None
        token = self.current
        self.position += 1
        return token

    def parse(self) -> Expression:
        """Parse the full expression and ensure the token stream is exhausted."""

        expression = self.parse_or()
        if self.current.type != "EOF":
            raise TrailingTokensError(
                f"Unexpected token '{self.current.value or self.current.type}'",
                self.current.position,
            )
        return expression

    def parse_or(self) -> Expression:
        """Parse a left-associative OR-expression."""

        return self.parse_binary_chain(self.parse_and, "OR", self.factory.create_or)

    def parse_and(self) -> Expression:
        """Parse a left-associative AND-expression."""

        return self.parse_binary_chain(self.parse_not, "AND", self.factory.create_and)

    def parse_not(self) -> Expression:
        """Parse unary negation."""

        if self.consume("NOT") is not None:
            return self.factory.create_not(self.parse_not())
        return self.parse_primary()

    def parse_primary(self) -> Expression:
        """Parse a variable reference or a parenthesized expression."""

        variable_token = self.consume("VAR")
        if variable_token is not None:
            return self.factory.create_variable(variable_token.value)

        if self.consume("LPAREN") is not None:
            expression = self.parse_or()
            if self.consume("RPAREN") is None:
                raise MissingParenthesisError("Missing closing parenthesis ')'", self.current.position)
            return expression

        if self.current.type == "EOF":
            raise UnexpectedTokenError("Unexpected end of expression, operand expected", self.current.position)

        raise UnexpectedTokenError(
            f"Unexpected token '{self.current.value or self.current.type}', operand expected",
            self.current.position,
        )

    def parse_binary_chain(
        self,
        operand_parser: OperandParser,
        operator_token_type: str,
        node_factory: BinaryNodeFactory,
    ) -> Expression:
        """Parse a left-associative chain of binary operations."""

        expression = operand_parser()
        while self.consume(operator_token_type) is not None:
            expression = node_factory(expression, operand_parser())
        return expression


def parse_expression(
    expression: str,
    factory: ExpressionFactory | None = None,
) -> Expression:
    """Tokenize and parse a logical expression."""

    parser = Parser(tokenize(expression), factory=factory)
    return parser.parse()
