"""Recursive descent parser with explicit operator precedence."""

from __future__ import annotations

from core.ast.nodes import (
    AndNode,
    ConstantNode,
    EquivalentNode,
    ExpressionNode,
    ImpliesNode,
    NotNode,
    OrNode,
    VariableNode,
)
from core.parser.tokenizer import Token, TokenType, Tokenizer
from utils.exceptions import ParseError


class ExpressionParser:
    """Parse token sequences into AST nodes."""

    def __init__(self, tokenizer: Tokenizer | None = None) -> None:
        self._tokenizer = tokenizer or Tokenizer()
        self._tokens: list[Token] = []
        self._position = 0

    def parse(self, expression: str) -> ExpressionNode:
        """Parse a source expression into an AST."""

        self._tokens = self._tokenizer.tokenize(expression)
        self._position = 0
        result = self._parse_equivalence()
        if self.current.type is not TokenType.EOF:
            raise ParseError(f"Unexpected token '{self.current.value}'", self.current.position)
        return result

    @property
    def current(self) -> Token:
        """Return the current token."""

        return self._tokens[self._position]

    def _consume(self, token_type: TokenType) -> Token | None:
        if self.current.type is token_type:
            token = self.current
            self._position += 1
            return token
        return None

    def _expect(self, token_type: TokenType, message: str) -> Token:
        token = self._consume(token_type)
        if token is None:
            raise ParseError(message, self.current.position)
        return token

    def _parse_equivalence(self) -> ExpressionNode:
        expression = self._parse_implication()
        while self._consume(TokenType.EQUIVALENT) is not None:
            expression = EquivalentNode(expression, self._parse_implication())
        return expression

    def _parse_implication(self) -> ExpressionNode:
        left = self._parse_or()
        if self._consume(TokenType.IMPLIES) is None:
            return left
        return ImpliesNode(left, self._parse_implication())

    def _parse_or(self) -> ExpressionNode:
        expression = self._parse_and()
        while self._consume(TokenType.OR) is not None:
            expression = OrNode(expression, self._parse_and())
        return expression

    def _parse_and(self) -> ExpressionNode:
        expression = self._parse_not()
        while self._consume(TokenType.AND) is not None:
            expression = AndNode(expression, self._parse_not())
        return expression

    def _parse_not(self) -> ExpressionNode:
        if self._consume(TokenType.NOT) is not None:
            return NotNode(self._parse_not())
        return self._parse_primary()

    def _parse_primary(self) -> ExpressionNode:
        variable = self._consume(TokenType.VARIABLE)
        if variable is not None:
            return VariableNode(variable.value)

        constant = self._consume(TokenType.CONSTANT)
        if constant is not None:
            return ConstantNode(constant.value == "1")

        if self._consume(TokenType.LPAREN) is not None:
            expression = self._parse_equivalence()
            self._expect(TokenType.RPAREN, "Missing closing parenthesis")
            return expression

        if self.current.type is TokenType.EOF:
            raise ParseError("Unexpected end of expression", self.current.position)

        raise ParseError(f"Unexpected token '{self.current.value}'", self.current.position)
