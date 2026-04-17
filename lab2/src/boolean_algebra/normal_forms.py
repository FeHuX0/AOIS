"""Canonical, numeric and index forms."""

from __future__ import annotations

from models.normal_forms import CanonicalForms, IndexForm
from models.truth_table import TruthTable

EMPTY_SET_MARKER = "empty"


class CanonicalFormBuilder:
    """Build canonical and numeric forms from a truth table."""

    def build(self, table: TruthTable) -> CanonicalForms:
        """Construct SDNF, SKNF, numeric forms and index form."""

        minterms = table.minterm_indices
        maxterms = table.maxterm_indices
        bits = "".join(str(value) for value in table.result_vector)
        index_form = IndexForm(bits=bits, value=int(bits, 2) if bits else 0)
        return CanonicalForms(
            sdnf=self._build_sdnf(table),
            sknf=self._build_sknf(table),
            numeric_sdnf=f"Sigma({format_index_list(minterms)})",
            numeric_sknf=f"Pi({format_index_list(maxterms)})",
            minterm_indices=minterms,
            maxterm_indices=maxterms,
            index_form=index_form,
        )

    def _build_sdnf(self, table: TruthTable) -> str:
        terms = [self._build_minterm(table.variables, row.inputs) for row in table.rows if row.result == 1]
        if not table.variables:
            return "1" if table.rows[0].result == 1 else "0"
        return " | ".join(f"({term})" for term in terms) if terms else "0"

    def _build_sknf(self, table: TruthTable) -> str:
        clauses = [self._build_maxterm(table.variables, row.inputs) for row in table.rows if row.result == 0]
        if not table.variables:
            return "1" if table.rows[0].result == 1 else "0"
        return " & ".join(f"({clause})" for clause in clauses) if clauses else "1"

    @staticmethod
    def _build_minterm(variables: tuple[str, ...], inputs: tuple[int, ...]) -> str:
        literals = [
            variable if value == 1 else f"!{variable}"
            for variable, value in zip(variables, inputs, strict=True)
        ]
        return " & ".join(literals) if literals else "1"

    @staticmethod
    def _build_maxterm(variables: tuple[str, ...], inputs: tuple[int, ...]) -> str:
        literals = [
            variable if value == 0 else f"!{variable}"
            for variable, value in zip(variables, inputs, strict=True)
        ]
        return " | ".join(literals) if literals else "0"


def format_index_list(indices: tuple[int, ...]) -> str:
    """Format minterm/maxterm indices."""

    if not indices:
        return EMPTY_SET_MARKER
    return ", ".join(str(index) for index in indices)
