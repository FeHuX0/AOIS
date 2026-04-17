"""Application package for the logic algebra laboratory work."""

from app.analysis import AnalysisResult, analyze_expression as build_analysis_result
from app.expression_factory import DefaultExpressionFactory, ExpressionFactory
from app.parser import parse_expression
from app.tokenizer import tokenize


def analyze_expression(expression: str) -> str:
    """Format a full analysis report for the provided expression."""

    from app.cli import analyze_expression as format_expression_report

    return format_expression_report(expression)

__all__ = [
    "AnalysisResult",
    "DefaultExpressionFactory",
    "ExpressionFactory",
    "analyze_expression",
    "build_analysis_result",
    "parse_expression",
    "tokenize",
]
