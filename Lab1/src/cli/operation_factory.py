"""Factory objects for CLI operation handlers."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

NamespaceHandler = Callable[[argparse.Namespace], None]
InteractiveHandler = Callable[[], None]


@dataclass(frozen=True)
class OperationSpec:
    """One operation description and its handlers."""

    key: str
    title: str
    namespace_handler: NamespaceHandler
    interactive_handler: InteractiveHandler


class OperationFactory:
    """Build and serve operation handlers by command key."""

    def __init__(self, specs: Iterable[OperationSpec]) -> None:
        self._specs: dict[str, OperationSpec] = {}
        for spec in specs:
            if spec.key in self._specs:
                raise ValueError(f"duplicated operation key: {spec.key}")
            self._specs[spec.key] = spec

    def namespace_handler(self, key: str | None) -> NamespaceHandler | None:
        if key is None:
            return None
        spec = self._specs.get(key)
        if spec is None:
            return None
        return spec.namespace_handler

    def interactive_handler(self, key: str) -> InteractiveHandler | None:
        spec = self._specs.get(key)
        if spec is None:
            return None
        return spec.interactive_handler

    def interactive_specs(self) -> Sequence[OperationSpec]:
        return tuple(self._specs.values())

