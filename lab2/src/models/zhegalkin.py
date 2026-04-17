"""Zhegalkin polynomial model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ZhegalkinPolynomial:
    """Algebraic normal form of a boolean function."""

    coefficients: tuple[int, ...]
    monomials: tuple[str, ...]
    polynomial: str
