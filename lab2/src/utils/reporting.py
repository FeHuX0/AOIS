"""Text report formatting helpers."""

from __future__ import annotations

from models.analysis import AnalysisResult
from models.derivatives import DerivativeResult
from models.minimization import CalculationMethodResult, KarnaughSolution, PrimeImplicantChartResult
from models.truth_table import TruthTable


def format_report(result: AnalysisResult) -> str:
    """Format the full CLI report."""

    lines: list[str] = [
        f"Expression: {result.source_expression}",
        f"Normalized: {result.normalized_expression}",
        f"Variables: {', '.join(result.truth_table.variables) if result.truth_table.variables else '(constant)'}",
        "",
        "Truth table:",
        format_truth_table(result.truth_table),
        "",
        f"SDNF: {result.canonical_forms.sdnf}",
        f"SKNF: {result.canonical_forms.sknf}",
        f"Numeric SDNF: {result.canonical_forms.numeric_sdnf}",
        f"Numeric SKNF: {result.canonical_forms.numeric_sknf}",
        f"Index form: {result.canonical_forms.index_form.notation}",
        "",
        f"Zhegalkin polynomial: {result.zhegalkin.polynomial}",
        (
            "Post classes: "
            f"T0={'yes' if result.post_classes.t0 else 'no'}, "
            f"T1={'yes' if result.post_classes.t1 else 'no'}, "
            f"S={'yes' if result.post_classes.s else 'no'}, "
            f"M={'yes' if result.post_classes.m else 'no'}, "
            f"L={'yes' if result.post_classes.l else 'no'}"
        ),
        "Fictitious variables: "
        + (", ".join(result.derivatives.fictitious_variables) if result.derivatives.fictitious_variables else "none"),
        "",
        "Partial derivatives:",
        format_derivative_block(result.derivatives.partial),
        "",
        "Mixed derivatives:",
        format_derivative_block(result.derivatives.mixed),
        "",
        "Calculation method (DNF):",
        format_calculation_method(result.dnf_calculation, result.truth_table.variables),
        "",
        "Calculation-tabular method (DNF):",
        format_chart_method(result.dnf_table_method, result.truth_table.minterm_indices, result.truth_table.variables),
        "",
        "Calculation method (CNF):",
        format_calculation_method(result.cnf_calculation, result.truth_table.variables),
        "",
        "Calculation-tabular method (CNF):",
        format_chart_method(result.cnf_table_method, result.truth_table.maxterm_indices, result.truth_table.variables),
        "",
        "Karnaugh map:",
        result.karnaugh_map.visualization,
        format_karnaugh_solution("DNF", result.karnaugh_map.dnf_solution),
        format_karnaugh_solution("CNF", result.karnaugh_map.cnf_solution),
    ]
    return "\n".join(line for line in lines if line is not None)


def format_truth_table(table: TruthTable) -> str:
    """Format a truth table as plain text."""

    header = ["j", *table.variables, "f"]
    rows = [header]
    for row in table.rows:
        rows.append([str(row.index), *[str(bit) for bit in row.inputs], str(row.result)])

    widths = [max(len(item) for item in column) for column in zip(*rows, strict=True)]
    return "\n".join(
        " | ".join(value.rjust(width) for value, width in zip(row, widths, strict=True))
        for row in rows
    )


def format_derivative_block(derivatives: tuple[DerivativeResult, ...]) -> str:
    """Format a derivative section."""

    if not derivatives:
        return "none"
    return "\n".join(
        f"d/d{''.join(derivative.variables)} = {derivative.expression}"
        for derivative in derivatives
    )


def format_calculation_method(result: CalculationMethodResult, variables: tuple[str, ...]) -> str:
    """Format Quine-McCluskey gluing stages."""

    lines: list[str] = []
    if not result.rounds:
        lines.append("No gluing required.")
    for round_result in result.rounds:
        lines.append(f"Stage {round_result.stage}:")
        if round_result.groups:
            lines.extend(
                f"  group {group_key}: {', '.join(items)}"
                for group_key, items in round_result.groups
            )
        else:
            lines.append("  no groups")
        if round_result.combinations:
            lines.extend(
                f"  {record.left} + {record.right} -> {record.result}"
                for record in round_result.combinations
            )
        else:
            lines.append("  no combinations")
        if round_result.prime_implicants:
            lines.append(f"  prime implicants: {', '.join(round_result.prime_implicants)}")
    prime_implicants = ", ".join(implicant.pattern_string() for implicant in result.prime_implicants) or "none"
    lines.append(f"Prime implicants: {prime_implicants}")
    lines.append(f"Minimized form: {result.minimized_expression}")
    return "\n".join(lines)


def format_chart_method(
    result: PrimeImplicantChartResult,
    target_indices: tuple[int, ...],
    variables: tuple[str, ...],
) -> str:
    """Format the prime implicant chart method."""

    if not target_indices:
        return f"No target rows. Result: {result.expression}"

    lines = ["pattern | " + " | ".join(str(index) for index in target_indices)]
    for pattern, flags in result.chart:
        cells = " | ".join("x" if flag else "." for flag in flags)
        lines.append(f"{pattern:>7} | {cells}")
    essential = ", ".join(implicant.pattern_string() for implicant in result.essential_implicants) or "none"
    selected = ", ".join(implicant.pattern_string() for implicant in result.selected_implicants) or "none"
    lines.append(f"Essential implicants: {essential}")
    lines.append(f"Selected cover: {selected}")
    lines.append(f"Minimized form: {result.expression}")
    return "\n".join(lines)


def format_karnaugh_solution(label: str, solution: KarnaughSolution | None) -> str:
    """Format a Karnaugh solution section."""

    if solution is None:
        return f"{label}: not available"
    groups = "; ".join(f"{group.term} -> {group.cells}" for group in solution.groups) or "no groups"
    return f"{label}: {solution.expression}\nGroups: {groups}"
