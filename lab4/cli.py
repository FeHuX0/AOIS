from __future__ import annotations

from collections.abc import Callable

from src.errors import DuplicateKeyError, HashTableError, KeyNotFoundError, TableFullError
from src.hash_status import HashStatus
from src.hash_table import HashTable

EMPTY_CELL_MARK = "-"


def print_menu() -> None:
    print("\nМеню:")
    print("1. Добавить элемент")
    print("2. Найти элемент")
    print("3. Обновить элемент")
    print("4. Удалить элемент")
    print("5. Показать таблицу")
    print("6. Показать коэффициент заполнения")
    print("0. Выход")


def format_public_table(table: HashTable) -> str:
    lines = ["Индекс | Ключ | Значение"]

    for index in range(table.size):
        entry = table.get_entry(index)
        if entry.status is HashStatus.OCCUPIED:
            key = entry.key
            value = entry.value
        else:
            key = EMPTY_CELL_MARK
            value = EMPTY_CELL_MARK

        lines.append(f"{index} | {key} | {value}")

    return "\n".join(lines)


def _handle_insert(table: HashTable) -> bool:
    key = input("Введите ключ: ").strip()
    value = input("Введите значение: ").strip()

    try:
        index = table.insert(key, value)
    except DuplicateKeyError:
        print("Ошибка: такой ключ уже существует.")
    except TableFullError:
        print("Ошибка: таблица заполнена.")
    except HashTableError as error:
        print(f"Ошибка: {error}")
    else:
        print(f"Элемент успешно добавлен. Индекс: {index}.")

    return True


def _handle_search(table: HashTable) -> bool:
    key = input("Введите ключ для поиска: ").strip()

    try:
        value = table.search(key)
    except KeyNotFoundError:
        print("Элемент не найден.")
    except HashTableError as error:
        print(f"Ошибка: {error}")
    else:
        print(f"Найдено значение: {value}")

    return True


def _handle_update(table: HashTable) -> bool:
    key = input("Введите ключ для обновления: ").strip()
    value = input("Введите новое значение: ").strip()

    try:
        index = table.update(key, value)
    except KeyNotFoundError:
        print("Ошибка: ключ не найден.")
    except HashTableError as error:
        print(f"Ошибка: {error}")
    else:
        print(f"Элемент обновлен. Индекс: {index}.")

    return True


def _handle_delete(table: HashTable) -> bool:
    key = input("Введите ключ для удаления: ").strip()

    try:
        value = table.delete(key)
    except KeyNotFoundError:
        print("Ошибка: ключ не найден.")
    except HashTableError as error:
        print(f"Ошибка: {error}")
    else:
        print(f"Элемент удален. Удаленное значение: {value}")

    return True


def _handle_show(table: HashTable) -> bool:
    print(format_public_table(table))
    return True


def _handle_load_factor(table: HashTable) -> bool:
    print(f"Коэффициент заполнения: {table.get_load_factor():.2f}")
    return True


def _handle_exit(_: HashTable) -> bool:
    print("Завершение работы.")
    return False


def _handle_unknown(_: HashTable) -> bool:
    print("Некорректная команда. Введите число от 0 до 6.")
    return True


def handle_command(table: HashTable, command: str) -> bool:
    handlers: dict[str, Callable[[HashTable], bool]] = {
        "1": _handle_insert,
        "2": _handle_search,
        "3": _handle_update,
        "4": _handle_delete,
        "5": _handle_show,
        "6": _handle_load_factor,
        "0": _handle_exit,
    }

    handler = handlers.get(command.strip(), _handle_unknown)
    return handler(table)


def run_cli(table: HashTable) -> None:
    print("Консольный интерфейс для работы с хеш-таблицей.")
    print(f"Размер таблицы: {table.size}")

    while True:
        print_menu()
        command = input("Выберите пункт меню: ").strip()
        should_continue = handle_command(table, command)
        if not should_continue:
            break
