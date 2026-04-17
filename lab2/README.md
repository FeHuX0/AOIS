# AOIS2 Boolean Algebra Lab

Production-ready Python project for AOIS laboratory work on boolean algebra.

The application:

- parses formulas without `eval`
- builds an AST and evaluates expressions through it
- generates a truth table for up to 5 variables: `a`, `b`, `c`, `d`, `e`
- builds `SDNF`, `SKNF`, numeric forms and index form
- checks Post classes `T0`, `T1`, `S`, `M`, `L`
- builds the Zhegalkin polynomial
- finds fictitious variables
- computes partial and mixed boolean derivatives
- minimizes functions with:
  - Quine-McCluskey calculation method
  - prime implicant chart method
  - Karnaugh map with visualization for up to 5 variables

## Supported syntax

- negation: `!a`
- conjunction: `a & b`
- disjunction: `a | b`
- implication: `a -> b`
- equivalence: `a ~ b`
- parentheses: `(a | b) & !c`

Operator priority:

1. `!`
2. `&`
3. `|`
4. `->`
5. `~`

## Project structure

```text
.
|-- .pre-commit-config.yaml
|-- Makefile
|-- README.md
|-- main.py
|-- pyproject.toml
|-- src/
|   |-- boolean_algebra/
|   |   |-- analyzer.py
|   |   |-- derivatives.py
|   |   |-- normal_forms.py
|   |   |-- post_classes.py
|   |   |-- truth_table.py
|   |   |-- zhegalkin.py
|   |   `-- minimization/
|   |       |-- karnaugh_map.py
|   |       |-- quine_mccluskey.py
|   |       `-- table_method.py
|   |-- core/
|   |   |-- ast/
|   |   |   `-- nodes.py
|   |   |-- evaluator/
|   |   |   `-- expression_evaluator.py
|   |   `-- parser/
|   |       |-- parser.py
|   |       `-- tokenizer.py
|   |-- models/
|   |   |-- analysis.py
|   |   |-- derivatives.py
|   |   |-- minimization.py
|   |   |-- normal_forms.py
|   |   |-- post.py
|   |   |-- truth_table.py
|   |   `-- zhegalkin.py
|   |-- utils/
|   |   |-- binary.py
|   |   |-- exceptions.py
|   |   `-- reporting.py
|   `-- cli.py
`-- tests/
    |-- integration/
    `-- unit/
```

## Architecture notes

- `core` contains parsing and evaluation primitives
- `boolean_algebra` contains domain algorithms
- `models` contains immutable DTOs for analysis results
- `utils` contains shared helpers and report formatting
- orchestration is done through `BooleanFunctionAnalyzer`
- dependencies are injected through constructors to keep modules testable

The code follows:

- SOLID
- DRY
- KISS
- YAGNI
- clean `src`-layout packaging

## Installation

```bash
uv sync
```

## Run examples

```bash
uv run python main.py --expr "!(!a -> !b) | c"
uv run logic-lab --expr "a & b | a & !b"
uv run python -m cli --expr "(a | b) -> (!c ~ d)"
```

Interactive mode:

```bash
uv run python main.py
```

Then enter:

```text
> !(!a -> !b) | c
```

## Example output sections

The CLI report includes:

- normalized expression
- truth table
- `SDNF`
- `SKNF`
- numeric forms `Σ(...)` and `Π(...)`
- index form
- Zhegalkin polynomial
- Post classes
- fictitious variables
- partial and mixed derivatives
- Quine-McCluskey gluing stages
- prime implicant chart
- Karnaugh map

## Quality tools

Format:

```bash
make format
```

Lint:

```bash
make lint
```

Run tests:

```bash
make test
```

Coverage:

```bash
make coverage
```

Run pre-commit hooks:

```bash
make pre-commit
```

## Tests

The project includes:

- parser and tokenizer tests
- AST and evaluator checks
- truth table tests
- canonical form tests
- Zhegalkin polynomial tests
- Post class tests
- derivative tests
- minimization tests
- randomized consistency tests
- CLI and end-to-end integration tests

Current target:

- `pytest`
- coverage `>= 90%`

## Randomized validation

`tests/unit/test_randomized_consistency.py` generates deterministic random expressions and verifies that:

- canonical forms remain equivalent to the source expression
- minimized DNF/CNF remain equivalent to the source expression
- Karnaugh-based minimization matches the original function when available

## Notes

- no `eval`
- no `sympy`
- no third-party boolean logic libraries
- Karnaugh map visualization supports 5 variables via two Gray-coded layers
