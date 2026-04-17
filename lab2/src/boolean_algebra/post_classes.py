"""Checks for Post classes."""

from __future__ import annotations

from models.post import PostClassMembership
from models.truth_table import TruthTable
from models.zhegalkin import ZhegalkinPolynomial


class PostClassAnalyzer:
    """Check membership of a boolean function in Post classes."""

    def analyze(self, table: TruthTable, polynomial: ZhegalkinPolynomial) -> PostClassMembership:
        """Evaluate all required Post classes."""

        lookup = table.lookup()
        all_zero = tuple(0 for _ in table.variables)
        all_one = tuple(1 for _ in table.variables)
        t0 = lookup[all_zero] == 0
        t1 = lookup[all_one] == 1
        s = self._is_self_dual(table)
        m = self._is_monotone(table)
        l = self._is_linear(polynomial, len(table.variables))
        return PostClassMembership(t0=t0, t1=t1, s=s, m=m, l=l)

    @staticmethod
    def _is_self_dual(table: TruthTable) -> bool:
        lookup = table.lookup()
        for inputs, value in lookup.items():
            complement = tuple(1 - bit for bit in inputs)
            if value == lookup[complement]:
                return False
        return True

    @staticmethod
    def _is_monotone(table: TruthTable) -> bool:
        rows = list(table.rows)
        for left in rows:
            for right in rows:
                if _is_componentwise_leq(left.inputs, right.inputs) and left.result > right.result:
                    return False
        return True

    @staticmethod
    def _is_linear(polynomial: ZhegalkinPolynomial, variable_count: int) -> bool:
        for index, coefficient in enumerate(polynomial.coefficients):
            if coefficient == 0:
                continue
            if index.bit_count() > 1:
                return False
        return True


def _is_componentwise_leq(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return all(left_bit <= right_bit for left_bit, right_bit in zip(left, right, strict=True))
