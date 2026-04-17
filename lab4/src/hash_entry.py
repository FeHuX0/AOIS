from dataclasses import dataclass
from typing import Any

from .hash_status import HashStatus


@dataclass(slots=True)
class HashEntry:
    id_word: str | None = None
    c: int = 0
    u: int = 0
    t: int = 0
    l: int = 0
    d: int = 0
    p0: int | None = None
    pi: Any = None

    @property
    def key(self) -> str | None:
        return self.id_word

    @property
    def value(self) -> Any:
        return self.pi

    @value.setter
    def value(self, new_value: Any) -> None:
        self.pi = new_value

    @property
    def status(self) -> HashStatus:
        if self.d == 1:
            return HashStatus.DELETED
        if self.u == 1:
            return HashStatus.OCCUPIED
        return HashStatus.EMPTY

    def occupy(self, key: str, value: Any, collision: bool) -> None:
        self.id_word = key
        self.c = 1 if collision else 0
        self.u = 1
        self.t = 1
        self.l = 0
        self.d = 0
        self.p0 = None
        self.pi = value

    def mark_deleted(self) -> None:
        self.u = 0
        self.t = 0
        self.d = 1
        self.l = 0
        self.p0 = None

    def __str__(self) -> str:
        return (
            f"ID={self.id_word}, C={self.c}, U={self.u}, T={self.t}, "
            f"L={self.l}, D={self.d}, P0={self.p0}, Pi={self.pi}"
        )
