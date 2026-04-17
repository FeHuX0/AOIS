from .errors import InvalidKeyError, InvalidTableSizeError

RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
ALPHABET_SIZE = len(RUSSIAN_ALPHABET)


def validate_table_size(table_size: int) -> None:
    if isinstance(table_size, bool) or not isinstance(table_size, int):
        raise InvalidTableSizeError("Table size must be an integer.")
    if table_size <= 0:
        raise InvalidTableSizeError("Table size must be greater than zero.")


def normalize_key(key: str) -> str:
    if not isinstance(key, str):
        raise InvalidKeyError("Key must be a string.")

    normalized_key = key.strip().upper()
    if len(normalized_key) < 2:
        raise InvalidKeyError("Key must contain at least two Russian letters.")

    invalid_letters = [letter for letter in normalized_key if letter not in RUSSIAN_ALPHABET]
    if invalid_letters:
        raise InvalidKeyError("Key must contain only Russian letters.")

    return normalized_key


def get_letter_index(letter: str) -> int:
    if len(letter) != 1 or letter not in RUSSIAN_ALPHABET:
        raise InvalidKeyError(f"Unsupported letter: {letter!r}.")
    return RUSSIAN_ALPHABET.index(letter)


def calculate_v(key: str) -> int:
    normalized_key = normalize_key(key)
    first_letter_index = get_letter_index(normalized_key[0])
    second_letter_index = get_letter_index(normalized_key[1])
    return first_letter_index * ALPHABET_SIZE + second_letter_index


def calculate_hash(value: int, table_size: int, base: int = 0) -> int:
    validate_table_size(table_size)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Hash input value must be an integer.")
    if isinstance(base, bool) or not isinstance(base, int):
        raise ValueError("Base value must be an integer.")
    return (value % table_size + base) % table_size
