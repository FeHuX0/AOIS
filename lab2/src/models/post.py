"""Post class membership model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PostClassMembership:
    """Membership flags for Post classes."""

    t0: bool
    t1: bool
    s: bool
    m: bool
    l: bool
