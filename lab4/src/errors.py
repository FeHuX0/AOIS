class HashTableError(Exception):
    """Base exception for hash table errors."""


class InvalidTableSizeError(HashTableError):
    """Raised when the table size is invalid."""


class InvalidKeyError(HashTableError):
    """Raised when the key does not satisfy validation rules."""


class DuplicateKeyError(HashTableError):
    """Raised when an insertion with an existing key is attempted."""


class KeyNotFoundError(HashTableError):
    """Raised when a key cannot be found in the table."""


class TableFullError(HashTableError):
    """Raised when there is no free position for insertion."""
