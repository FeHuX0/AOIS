from cli import run_cli
from src.hash_table import HashTable


DEFAULT_TABLE_SIZE = 11


def main() -> None:
    table = HashTable(size=DEFAULT_TABLE_SIZE)
    run_cli(table)


if __name__ == "__main__":
    main()
