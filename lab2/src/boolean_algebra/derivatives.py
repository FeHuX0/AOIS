"""Boolean derivatives and fictitious variables."""

from __future__ import annotations

from itertools import product

from boolean_algebra.normal_forms import CanonicalFormBuilder
from models.derivatives import DerivativeResult, DerivativesSummary
from models.truth_table import TruthTable, TruthTableRow
from utils.binary import bit_tuple_to_int, powerset


class BooleanDerivativeAnalyzer:
    """Compute partial and mixed boolean derivatives."""

    def __init__(self, canonical_form_builder: CanonicalFormBuilder | None = None) -> None:
        self._canonical_form_builder = canonical_form_builder or CanonicalFormBuilder()

    def analyze(self, table: TruthTable) -> DerivativesSummary:
        """Build all partial and mixed derivatives."""

        partial: list[DerivativeResult] = []
        mixed: list[DerivativeResult] = []
        for variables in powerset(table.variables):
            derivative = self.derivative(table, variables)
            if len(variables) == 1:
                partial.append(derivative)
            else:
                mixed.append(derivative)

        fictitious = tuple(
            derivative.variables[0]
            for derivative in partial
            if all(row.result == 0 for row in derivative.truth_table.rows)
        )
        return DerivativesSummary(
            partial=tuple(partial),
            mixed=tuple(mixed),
            fictitious_variables=fictitious,
        )

    def derivative(self, table: TruthTable, variables: tuple[str, ...]) -> DerivativeResult:
        """Compute a derivative with respect to a sequence of variables."""

        current_table = table
        for variable in variables:
            current_table = self._partial_derivative(current_table, variable)
        expression = self._canonical_form_builder.build(current_table).sdnf
        return DerivativeResult(variables=variables, truth_table=current_table, expression=expression)

    def _partial_derivative(self, table: TruthTable, variable: str) -> TruthTable:
        variable_index = table.variables.index(variable)
        remaining_variables = tuple(name for name in table.variables if name != variable)
        lookup = table.lookup()

        rows: list[TruthTableRow] = []
        for bits in product((0, 1), repeat=len(remaining_variables)):
            left_bits = bits[:variable_index] + (0,) + bits[variable_index:]
            right_bits = bits[:variable_index] + (1,) + bits[variable_index:]
            result = lookup[left_bits] ^ lookup[right_bits]
            rows.append(TruthTableRow(index=bit_tuple_to_int(bits), inputs=bits, result=result))
        return TruthTable(variables=remaining_variables, rows=tuple(rows))
