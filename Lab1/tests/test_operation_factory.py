import argparse
import unittest

from src.cli.operation_factory import OperationFactory, OperationSpec


class OperationFactoryTests(unittest.TestCase):
    def test_factory_returns_handlers(self) -> None:
        called: list[str] = []

        def ns_handler(namespace: argparse.Namespace) -> None:
            called.append(str(namespace.value))

        def interactive_handler() -> None:
            called.append("interactive")

        factory = OperationFactory([OperationSpec("demo", "demo op", ns_handler, interactive_handler)])
        handler = factory.namespace_handler("demo")
        self.assertIsNotNone(handler)
        handler(argparse.Namespace(value=123))
        self.assertEqual(["123"], called)

        interactive = factory.interactive_handler("demo")
        self.assertIsNotNone(interactive)
        interactive()
        self.assertEqual(["123", "interactive"], called)

    def test_factory_validation_and_unknown_keys(self) -> None:
        def noop_namespace(_: argparse.Namespace) -> None:
            return None

        def noop_interactive() -> None:
            return None

        with self.assertRaises(ValueError):
            OperationFactory(
                [
                    OperationSpec("dup", "first", noop_namespace, noop_interactive),
                    OperationSpec("dup", "second", noop_namespace, noop_interactive),
                ]
            )

        factory = OperationFactory([OperationSpec("one", "only one", noop_namespace, noop_interactive)])
        self.assertIsNone(factory.namespace_handler("missing"))
        self.assertIsNone(factory.namespace_handler(None))
        self.assertIsNone(factory.interactive_handler("missing"))
        self.assertEqual(1, len(factory.interactive_specs()))


if __name__ == "__main__":
    unittest.main()

