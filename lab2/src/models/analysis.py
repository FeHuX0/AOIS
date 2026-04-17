"""High-level analysis result model."""

from __future__ import annotations

from dataclasses import dataclass

from models.derivatives import DerivativesSummary
from models.minimization import CalculationMethodResult, KarnaughMapResult, PrimeImplicantChartResult
from models.normal_forms import CanonicalForms
from models.post import PostClassMembership
from models.truth_table import TruthTable
from models.zhegalkin import ZhegalkinPolynomial


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Complete boolean function analysis."""

    source_expression: str
    normalized_expression: str
    truth_table: TruthTable
    canonical_forms: CanonicalForms
    zhegalkin: ZhegalkinPolynomial
    post_classes: PostClassMembership
    derivatives: DerivativesSummary
    dnf_calculation: CalculationMethodResult
    cnf_calculation: CalculationMethodResult
    dnf_table_method: PrimeImplicantChartResult
    cnf_table_method: PrimeImplicantChartResult
    karnaugh_map: KarnaughMapResult
