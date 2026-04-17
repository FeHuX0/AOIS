from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .errors import DuplicateKeyError, KeyNotFoundError, TableFullError
from .hash_entry import HashEntry
from .hash_status import HashStatus
from .hash_utils import calculate_hash, calculate_v, normalize_key, validate_table_size


class HashTable:
    def __init__(self, size: int, base: int = 0) -> None:
        validate_table_size(size)
        self._size = size
        self._base = base
        self._count = 0
        self._table = [HashEntry() for _ in range(size)]

    @property
    def size(self) -> int:
        return self._size

    @property
    def count(self) -> int:
        return self._count

    def __len__(self) -> int:
        return self._count

    def get_entry(self, index: int) -> HashEntry:
        return self._table[index]

    def _initial_index(self, key: str) -> int:
        return calculate_hash(calculate_v(key), self._size, self._base)

    def _probe_index(self, initial_index: int, attempt: int) -> int:
        return (initial_index + attempt * attempt) % self._size

    def _probe_sequence(self, initial_index: int) -> Iterator[int]:
        yielded_indexes: set[int] = set()

        for attempt in range(self._size):
            index = self._probe_index(initial_index, attempt)
            if index not in yielded_indexes:
                yielded_indexes.add(index)
                yield index

        # Quadratic probing can revisit the same cells and leave a part of the
        # table unchecked. The linear fallback guarantees a full scan.
        for offset in range(self._size):
            index = (initial_index + offset) % self._size
            if index not in yielded_indexes:
                yield index

    def _find_existing_index(self, key: str) -> int:
        normalized_key = normalize_key(key)
        initial_index = self._initial_index(normalized_key)

        for index in self._probe_sequence(initial_index):
            entry = self._table[index]

            if entry.status is HashStatus.EMPTY:
                break

            if entry.status is HashStatus.OCCUPIED and entry.key == normalized_key:
                return index

        raise KeyNotFoundError(f"Key '{normalized_key}' was not found.")

    def insert(self, key: str, value: Any) -> int:
        normalized_key = normalize_key(key)
        initial_index = self._initial_index(normalized_key)
        first_deleted_index: int | None = None

        for index in self._probe_sequence(initial_index):
            entry = self._table[index]

            if entry.status is HashStatus.OCCUPIED:
                if entry.key == normalized_key:
                    raise DuplicateKeyError(f"Key '{normalized_key}' already exists.")
                continue

            if entry.status is HashStatus.DELETED:
                if first_deleted_index is None:
                    first_deleted_index = index
                continue

            target_index = first_deleted_index if first_deleted_index is not None else index
            collision_happened = target_index != initial_index
            self._table[target_index].occupy(normalized_key, value, collision_happened)
            self._count += 1
            return target_index

        if first_deleted_index is not None:
            collision_happened = first_deleted_index != initial_index
            self._table[first_deleted_index].occupy(normalized_key, value, collision_happened)
            self._count += 1
            return first_deleted_index

        raise TableFullError("Hash table is full. Insert operation cannot be completed.")

    def search(self, key: str) -> Any:
        index = self._find_existing_index(key)
        return self._table[index].value

    def update(self, key: str, value: Any) -> int:
        index = self._find_existing_index(key)
        self._table[index].value = value
        return index

    def delete(self, key: str) -> Any:
        index = self._find_existing_index(key)
        removed_value = self._table[index].value
        self._table[index].mark_deleted()
        self._count -= 1
        return removed_value

    def get_load_factor(self) -> float:
        return self._count / self._size

    def display(self) -> str:
        lines = [
            f"HashTable(size={self._size}, count={self._count}, load_factor={self.get_load_factor():.2f})"
        ]
        lines.append("idx | ID | C | U | T | L | D | P0 | Pi")

        for index, entry in enumerate(self._table):
            lines.append(
                f"{index:>3} | {self._format_value(entry.id_word):<10} | "
                f"{entry.c} | {entry.u} | {entry.t} | {entry.l} | {entry.d} | "
                f"{self._format_value(entry.p0):<4} | {self._format_value(entry.pi)}"
            )

        return "\n".join(lines)

    def display_table(self) -> str:
        return self.display()

    @staticmethod
    def _format_value(value: Any) -> str:
        if value is None:
            return "None"
        return str(value)

    def __str__(self) -> str:
        return self.display()
