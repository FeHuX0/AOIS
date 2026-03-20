"""Run unittest suite and compute line coverage for src/ with stdlib only."""

from __future__ import annotations

import pathlib
import sys
import trace
import unittest
from dataclasses import dataclass


@dataclass
class FileCoverage:
    path: pathlib.Path
    executed: int
    total: int

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 100.0
        return (self.executed / self.total) * 100.0


def executable_lines(path: pathlib.Path) -> set[int]:
    lines = trace._find_executable_linenos(str(path))
    return set(lines.keys())


def collect_python_files(root: pathlib.Path) -> list[pathlib.Path]:
    files = []
    for path in root.rglob("*.py"):
        if path.name.startswith("."):
            continue
        files.append(path.resolve())
    return sorted(files)


def main() -> int:
    project_root = pathlib.Path(__file__).resolve().parents[1]
    src_root = project_root / "src"
    tests_root = project_root / "tests"
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    tracer = trace.Trace(count=True, trace=False)

    def run_tests() -> unittest.TestResult:
        suite = unittest.defaultTestLoader.discover(str(tests_root))
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)

    result = tracer.runfunc(run_tests)

    counts = tracer.results().counts
    report: list[FileCoverage] = []

    for file_path in collect_python_files(src_root):
        total_lines = executable_lines(file_path)
        executed_lines = {
            line
            for (filename, line), count in counts.items()
            if pathlib.Path(filename).resolve() == file_path and count > 0
        }
        covered = len(total_lines & executed_lines)
        report.append(FileCoverage(path=file_path, executed=covered, total=len(total_lines)))

    total_exec = sum(item.executed for item in report)
    total_lines = sum(item.total for item in report)
    total_percent = 100.0 if total_lines == 0 else (total_exec / total_lines) * 100.0

    print("\nCoverage report (src):")
    for item in report:
        rel = item.path.relative_to(project_root)
        print(f"  {rel}: {item.executed}/{item.total} -> {item.percent:.2f}%")
    print(f"TOTAL: {total_exec}/{total_lines} -> {total_percent:.2f}%")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
