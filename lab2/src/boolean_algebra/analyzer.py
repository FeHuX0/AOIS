"""High-level boolean function analysis orchestration."""

from __future__ import annotations

from boolean_algebra.derivatives import BooleanDerivativeAnalyzer
from boolean_algebra.minimization import (
    KarnaughMapBuilder,
    PrimeImplicantChartSolver,
    QuineMcCluskeyMinimizer,
)
from boolean_algebra.normal_forms import CanonicalFormBuilder
from boolean_algebra.post_classes import PostClassAnalyzer
from boolean_algebra.truth_table import TruthTableGenerator
from boolean_algebra.zhegalkin import ZhegalkinPolynomialBuilder
from core.evaluator import ExpressionEvaluator
from core.parser import ExpressionParser, Tokenizer
from models.analysis import AnalysisResult
from models.minimization import CalculationMethodResult


class BooleanFunctionAnalyzer:
    """Facade that produces the full lab report data."""

    def __init__(
        self,
        parser: ExpressionParser | None = None,
        truth_table_generator: TruthTableGenerator | None = None,
        canonical_form_builder: CanonicalFormBuilder | None = None,
        zhegalkin_builder: ZhegalkinPolynomialBuilder | None = None,
        post_class_analyzer: PostClassAnalyzer | None = None,
        derivative_analyzer: BooleanDerivativeAnalyzer | None = None,
        quine_mccluskey: QuineMcCluskeyMinimizer | None = None,
        chart_solver: PrimeImplicantChartSolver | None = None,
        karnaugh_builder: KarnaughMapBuilder | None = None,
    ) -> None:
        evaluator = ExpressionEvaluator()
        self._parser = parser or ExpressionParser(Tokenizer())
        self._truth_table_generator = truth_table_generator or TruthTableGenerator(evaluator)
        self._canonical_form_builder = canonical_form_builder or CanonicalFormBuilder()
        self._zhegalkin_builder = zhegalkin_builder or ZhegalkinPolynomialBuilder()
        self._post_class_analyzer = post_class_analyzer or PostClassAnalyzer()
        self._derivative_analyzer = derivative_analyzer or BooleanDerivativeAnalyzer(self._canonical_form_builder)
        self._quine_mccluskey = quine_mccluskey or QuineMcCluskeyMinimizer()
        self._chart_solver = chart_solver or PrimeImplicantChartSolver()
        self._karnaugh_builder = karnaugh_builder or KarnaughMapBuilder()

    def analyze(self, expression_text: str) -> AnalysisResult:
        """Run the full boolean function analysis pipeline."""

        expression = self._parser.parse(expression_text)
        truth_table = self._truth_table_generator.generate(expression)
        canonical_forms = self._canonical_form_builder.build(truth_table)
        zhegalkin = self._zhegalkin_builder.build(truth_table)
        post_classes = self._post_class_analyzer.analyze(truth_table, zhegalkin)
        derivatives = self._derivative_analyzer.analyze(truth_table)

        dnf_prime_implicants, dnf_rounds = self._quine_mccluskey.generate_prime_implicants(
            truth_table.minterm_indices,
            len(truth_table.variables),
        )
        dnf_table_method = self._chart_solver.solve(
            dnf_prime_implicants,
            truth_table.minterm_indices,
            truth_table.variables,
            target_value=1,
        )
        dnf_calculation = CalculationMethodResult(
            target_value=1,
            rounds=dnf_rounds,
            prime_implicants=dnf_prime_implicants,
            minimized_expression=dnf_table_method.expression,
        )

        cnf_prime_implicants, cnf_rounds = self._quine_mccluskey.generate_prime_implicants(
            truth_table.maxterm_indices,
            len(truth_table.variables),
        )
        cnf_table_method = self._chart_solver.solve(
            cnf_prime_implicants,
            truth_table.maxterm_indices,
            truth_table.variables,
            target_value=0,
        )
        cnf_calculation = CalculationMethodResult(
            target_value=0,
            rounds=cnf_rounds,
            prime_implicants=cnf_prime_implicants,
            minimized_expression=cnf_table_method.expression,
        )

        karnaugh_map = self._karnaugh_builder.build(truth_table)
        return AnalysisResult(
            source_expression=expression_text,
            normalized_expression=expression.to_infix(),
            truth_table=truth_table,
            canonical_forms=canonical_forms,
            zhegalkin=zhegalkin,
            post_classes=post_classes,
            derivatives=derivatives,
            dnf_calculation=dnf_calculation,
            cnf_calculation=cnf_calculation,
            dnf_table_method=dnf_table_method,
            cnf_table_method=cnf_table_method,
            karnaugh_map=karnaugh_map,
        )
