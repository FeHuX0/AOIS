"""Zhegalkin polynomial construction."""

from __future__ import annotations

from models.truth_table import TruthTable
from models.zhegalkin import ZhegalkinPolynomial
from utils.binary import int_to_bit_tuple


class ZhegalkinPolynomialBuilder:
    """Build the Zhegalkin polynomial via the finite-difference triangle."""

    def build(self, table: TruthTable) -> ZhegalkinPolynomial:
        """Construct the algebraic normal form."""

        current_row = list(table.result_vector)
        coefficients: list[int] = []
        while current_row:
            coefficients.append(current_row[0])
            current_row = [left ^ right for left, right in zip(current_row, current_row[1:], strict=False)]

        monomials = tuple(
            self._monomial_from_index(index, table.variables)
            for index, coefficient in enumerate(coefficients)
            if coefficient == 1
        )
        polynomial = " xor ".join(monomials) if monomials else "0"
        return ZhegalkinPolynomial(coefficients=tuple(coefficients), monomials=monomials, polynomial=polynomial)

    @staticmethod
    def _monomial_from_index(index: int, variables: tuple[str, ...]) -> str:
        if not variables and index == 0:
            return "1"

        bits = int_to_bit_tuple(index, len(variables))
        literals = [variable for variable, bit in zip(variables, bits, strict=True) if bit == 1]
        if not literals:
            return "1"
        return "*".join(literals)
