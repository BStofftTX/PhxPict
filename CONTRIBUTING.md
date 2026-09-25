# Contributing to PhxPict

PhxPict welcomes focused bug reports and proposals that improve local photo search, privacy, reliability, accessibility, or cross-platform support.

## Before contributing

1. Search existing issues before opening a new one.
2. Open or reference an issue for substantial changes.
3. Do not submit private photographs, personal indexes, credentials, model weights without redistribution rights, or other sensitive data.
4. Note that the project is currently all rights reserved pending final license selection. Discuss code contributions with the maintainers before investing substantial effort.

## Development setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Run the same quality gates used in CI:

```bash
python -m unittest discover -s tests -v
ruff check .
mypy src
pip-audit --skip-editable
```

## Pull requests

- Use a focused branch such as `feat/description`, `fix/description`, or `docs/description`.
- Explain the user need, implementation, tests, and privacy implications.
- Include screenshots for visible interface changes using synthetic or non-sensitive images only.
- Keep image processing local unless an explicitly opt-in design has been approved and documented.

Prefer small, meaningful commits. Do not manufacture activity, backdate work, or split trivial changes for contribution counts.
