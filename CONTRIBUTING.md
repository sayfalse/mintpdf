# Contributing to Mint PDF

Thank you for your interest in contributing to **Mint PDF**! We welcome bug reports, design feedback, and code contributions.

---

## Development Environment Setup

To set up a local development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/sayfalse/mintpdf.git
   cd mintpdf
   ```

2. Install the package in editable mode with development dependencies:
   ```bash
   pip install -e .[test,lint]
   ```

---

## Quality Checklist

Before submitting a pull request, ensure your code passes formatting, linting, typing, and unit tests.

### 1. Code Formatting (Black)
We format all code using Black with a 100-character line length:
```bash
# Verify formatting
black --check src/ tests/

# Automatically format code
black src/ tests/
```

### 2. Code Linting (Ruff)
We check code quality and import formatting using Ruff:
```bash
# Run lint check
ruff check src/ tests/

# Automatically resolve issues
ruff check src/ tests/ --fix
```

### 3. Static Type Checking (MyPy)
We verify static types using MyPy:
```bash
mypy src/
```

### 4. Unit Testing (PyTest)
Ensure all test suites pass successfully:
```bash
pytest
```

---

## Contribution Guidelines

- **Keep it Offline**: Mint PDF must run 100% offline. Do not introduce dependencies on external clouds, APIs, or AI web tools.
- **Maintain Immutability**: Prefer creating new object models and collections instead of mutating existing state records.
- **Add Tests**: Every new feature or bug fix should be accompanied by clear unit tests inside the `tests/` directory.
- **Conventional Commits**: Use clear conventional commits syntax:
  - `feat: ...` for new features
  - `fix: ...` for bug fixes
  - `docs: ...` for documentation changes
  - `test: ...` for test suite additions
  - `style: ...` for styling or formatting changes
