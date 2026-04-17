"""Karnaugh map construction and grouping."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from boolean_algebra.minimization.table_method import build_expression_from_implicants
from models.minimization import Implicant, KarnaughGroup, KarnaughMapResult, KarnaughSolution
from models.truth_table import TruthTable
from utils.binary import bit_tuple_to_int, gray_code


@dataclass(frozen=True, slots=True)
class _KarnaughLayout:
    """Internal layout description for 0-5 variable Karnaugh maps."""

    layer_variables: tuple[str, ...]
    row_variables: tuple[str, ...]
    column_variables: tuple[str, ...]
    layer_codes: tuple[tuple[int, ...], ...]
    row_codes: tuple[tuple[int, ...], ...]
    column_codes: tuple[tuple[int, ...], ...]

    def compose_bits(self, layer_index: int, row_index: int, column_index: int) -> tuple[int, ...]:
        """Return assignment bits in the canonical variable order."""

        return (
            self.row_codes[row_index]
            + self.column_codes[column_index]
            + self.layer_codes[layer_index]
        )


class KarnaughMapBuilder:
    """Build a Karnaugh map and derive minimized forms for up to five variables."""

    def build(self, table: TruthTable) -> KarnaughMapResult:
        """Build the map, visualization and selected groups."""

        if len(table.variables) > 5:
            return KarnaughMapResult(
                layer_variables=(),
                row_variables=(),
                column_variables=(),
                layer_codes=(),
                row_codes=(),
                column_codes=(),
                layers=(),
                visualization="Karnaugh map is supported only for up to 5 variables.",
                dnf_solution=None,
                cnf_solution=None,
            )

        layout = _build_layout(table.variables)
        lookup = table.lookup()
        layers = tuple(
            tuple(
                tuple(
                    lookup[layout.compose_bits(layer_index, row_index, column_index)]
                    for column_index in range(len(layout.column_codes))
                )
                for row_index in range(len(layout.row_codes))
            )
            for layer_index in range(len(layout.layer_codes))
        )
        visualization = _render_map(layout, layers)
        dnf_solution = self._solve(table, layout, layers, target_value=1)
        cnf_solution = self._solve(table, layout, layers, target_value=0)
        return KarnaughMapResult(
            layer_variables=layout.layer_variables,
            row_variables=layout.row_variables,
            column_variables=layout.column_variables,
            layer_codes=layout.layer_codes,
            row_codes=layout.row_codes,
            column_codes=layout.column_codes,
            layers=layers,
            visualization=visualization,
            dnf_solution=dnf_solution,
            cnf_solution=cnf_solution,
        )

    def _solve(
        self,
        table: TruthTable,
        layout: _KarnaughLayout,
        layers: tuple[tuple[tuple[int, ...], ...], ...],
        target_value: int,
    ) -> KarnaughSolution:
        target_cells = {
            bit_tuple_to_int(layout.compose_bits(layer_index, row_index, column_index))
            for layer_index, layer in enumerate(layers)
            for row_index, row in enumerate(layer)
            for column_index, value in enumerate(row)
            if value == target_value
        }
        if not target_cells:
            return KarnaughSolution(
                target_value=target_value,
                groups=(),
                expression="0" if target_value == 1 else "1",
            )

        candidate_groups = self._build_candidate_groups(table.variables, layout, layers, target_value)
        prime_groups = [
            group
            for group in candidate_groups
            if not any(set(group.cells) < set(other.cells) for other in candidate_groups)
        ]
        selected = self._select_groups(prime_groups, target_cells)
        implicants = tuple(Implicant(pattern=group.pattern, covered_indices=tuple(sorted(group.cells))) for group in selected)
        expression = build_expression_from_implicants(implicants, table.variables, target_value)
        return KarnaughSolution(target_value=target_value, groups=tuple(selected), expression=expression)

    def _build_candidate_groups(
        self,
        variables: tuple[str, ...],
        layout: _KarnaughLayout,
        layers: tuple[tuple[tuple[int, ...], ...], ...],
        target_value: int,
    ) -> list[KarnaughGroup]:
        layer_count = len(layout.layer_codes)
        row_count = len(layout.row_codes)
        column_count = len(layout.column_codes)
        valid_layer_sizes = _powers_of_two_up_to(layer_count)
        valid_heights = _powers_of_two_up_to(row_count)
        valid_widths = _powers_of_two_up_to(column_count)
        groups: dict[frozenset[int], KarnaughGroup] = {}

        for layer_size in valid_layer_sizes:
            for height in valid_heights:
                for width in valid_widths:
                    for layer_index in range(layer_count):
                        for row_index in range(row_count):
                            for column_index in range(column_count):
                                coordinates = {
                                    (
                                        (layer_index + layer_offset) % layer_count,
                                        (row_index + row_offset) % row_count,
                                        (column_index + column_offset) % column_count,
                                    )
                                    for layer_offset in range(layer_size)
                                    for row_offset in range(height)
                                    for column_offset in range(width)
                                }
                                if any(
                                    layers[layer][row][column] != target_value
                                    for layer, row, column in coordinates
                                ):
                                    continue
                                full_assignments = [
                                    layout.compose_bits(layer, row, column)
                                    for layer, row, column in coordinates
                                ]
                                cells = frozenset(bit_tuple_to_int(bits) for bits in full_assignments)
                                pattern = _common_pattern(tuple(full_assignments))
                                term = _pattern_to_term(pattern, variables, target_value)
                                groups[cells] = KarnaughGroup(
                                    target_value=target_value,
                                    cells=tuple(sorted(cells)),
                                    pattern=pattern,
                                    term=term,
                                )
        return list(groups.values())

    def _select_groups(self, groups: list[KarnaughGroup], target_cells: set[int]) -> list[KarnaughGroup]:
        essential_cells = {
            cell: [group for group in groups if cell in group.cells]
            for cell in target_cells
        }
        essential_groups = {
            cell_groups[0]
            for cell_groups in essential_cells.values()
            if len(cell_groups) == 1
        }
        covered = {cell for group in essential_groups for cell in group.cells}
        remaining = target_cells - covered
        if not remaining:
            return sorted(essential_groups, key=lambda group: (len(group.cells), group.term))

        candidates = [group for group in groups if group not in essential_groups]
        best_subset: tuple[KarnaughGroup, ...] | None = None
        best_score: tuple[int, int] | None = None
        for size in range(1, len(candidates) + 1):
            for subset in combinations(candidates, size):
                covered_cells = covered | {cell for group in subset for cell in group.cells}
                if not remaining.issubset(covered_cells):
                    continue
                score = (len(subset), sum(sum(bit is not None for bit in group.pattern) for group in subset))
                if best_score is None or score < best_score:
                    best_score = score
                    best_subset = subset
            if best_subset is not None:
                break

        selected = tuple(essential_groups) + (best_subset or ())
        return sorted(selected, key=lambda group: (len(group.cells), group.term))


def _build_layout(variables: tuple[str, ...]) -> _KarnaughLayout:
    if len(variables) <= 4:
        row_variables, column_variables = _split_variables(variables)
        layer_variables: tuple[str, ...] = ()
    else:
        row_variables, column_variables = _split_variables(variables[:-1])
        layer_variables = variables[-1:]

    return _KarnaughLayout(
        layer_variables=layer_variables,
        row_variables=row_variables,
        column_variables=column_variables,
        layer_codes=gray_code(len(layer_variables)),
        row_codes=gray_code(len(row_variables)),
        column_codes=gray_code(len(column_variables)),
    )


def _split_variables(variables: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    row_count = len(variables) // 2
    return variables[:row_count], variables[row_count:]


def _render_map(
    layout: _KarnaughLayout,
    layers: tuple[tuple[tuple[int, ...], ...], ...],
) -> str:
    row_label = "".join(layout.row_variables) or "-"
    column_label = "".join(layout.column_variables) or "-"
    lines = []
    if layout.layer_variables:
        layer_label = "".join(layout.layer_variables)
        lines.append(f"layers={layer_label}, rows={row_label}, cols={column_label}")
        for layer_code, layer in zip(layout.layer_codes, layers, strict=True):
            if lines:
                lines.append("")
            lines.extend(
                _render_layer(
                    title=_assignment_to_label(layout.layer_variables, layer_code),
                    row_codes=layout.row_codes,
                    column_codes=layout.column_codes,
                    matrix=layer,
                )
            )
        return "\n".join(lines)

    lines.append(f"rows={row_label}, cols={column_label}")
    lines.extend(
        _render_layer(
            title=None,
            row_codes=layout.row_codes,
            column_codes=layout.column_codes,
            matrix=layers[0],
        )
    )
    return "\n".join(lines)


def _render_layer(
    title: str | None,
    row_codes: tuple[tuple[int, ...], ...],
    column_codes: tuple[tuple[int, ...], ...],
    matrix: tuple[tuple[int, ...], ...],
) -> list[str]:
    lines: list[str] = []
    if title is not None:
        lines.append(title)
    header = "      | " + " | ".join(_bits_to_string(code) for code in column_codes)
    lines.append(header)
    lines.append("-" * len(header))
    for row_code, row in zip(row_codes, matrix, strict=True):
        lines.append(f"{_bits_to_string(row_code):>5} | " + " | ".join(str(value) for value in row))
    return lines


def _assignment_to_label(variables: tuple[str, ...], bits: tuple[int, ...]) -> str:
    return ", ".join(
        f"{variable}={bit}"
        for variable, bit in zip(variables, bits, strict=True)
    ) or "-"


def _bits_to_string(bits: tuple[int, ...]) -> str:
    return "".join(str(bit) for bit in bits) or "-"


def _powers_of_two_up_to(limit: int) -> tuple[int, ...]:
    values: list[int] = []
    current = 1
    while current <= max(limit, 1):
        values.append(current)
        current *= 2
    return tuple(values)


def _common_pattern(assignments: tuple[tuple[int, ...], ...]) -> tuple[int | None, ...]:
    pattern: list[int | None] = []
    for column in zip(*assignments, strict=True):
        unique_values = set(column)
        pattern.append(unique_values.pop() if len(unique_values) == 1 else None)
    return tuple(pattern)


def _pattern_to_term(pattern: tuple[int | None, ...], variables: tuple[str, ...], target_value: int) -> str:
    implicant = Implicant(pattern=pattern, covered_indices=())
    if target_value == 1:
        return implicant.to_dnf_term(variables)
    return implicant.to_cnf_clause(variables)
