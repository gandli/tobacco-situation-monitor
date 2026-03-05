# Contributing to Tobacco Situation Monitor

Thank you for considering contributing to TSM! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Prioritize security and privacy
- Follow legal and ethical guidelines

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/tobacco-situation-monitor.git
cd tobacco-situation-monitor
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Run Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_classifier.py -v

# Run with coverage
pytest --cov=src/tsm --cov-report=html
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-123
```

### 2. Make Changes

- Follow existing code style
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Run Pre-commit Checks

```bash
# Pre-commit will run automatically on git commit
# Or run manually:
pre-commit run --all-files
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature

- Description of what was added
- Related issue numbers"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub.

## Code Style

### Python

- Follow PEP 8
- Use Black for formatting
- Use isort for imports
- Use type hints
- Write docstrings (Google style)

Example:

```python
def process_data(data: list[str], threshold: float = 0.5) -> dict[str, float]:
    """Process input data and calculate metrics.

    Args:
        data: List of input strings to process.
        threshold: Cutoff threshold for filtering.

    Returns:
        Dictionary with calculated metrics.
    """
    result = {}
    # Implementation...
    return result
```

### Testing

- Write tests for all new features
- Use descriptive test names
- Test edge cases and error conditions
- Keep tests independent and isolated

Example:

```python
def test_extract_monetary_amount_yuan():
    """Test extracting monetary amounts in yuan."""
    text = "涉案金额 50 万元"
    raw, value = extract_monetary_amount(text)

    assert raw == "50 万元"
    assert value == 500000.0
```

## Project Structure

```
tobacco-situation-monitor/
├── src/tsm/              # Main source code
│   ├── api/              # FastAPI endpoints
│   ├── intel/            # Intelligence processing
│   ├── services/         # Business logic
│   ├── crawler/          # Web crawling
│   └── parser/           # Content parsing
├── tests/                # Test files
├── db/migrations/        # Database migrations
├── docs/                 # Documentation
└── frontend/             # Vue.js frontend
```

## Architecture

### Backend

- **Framework**: FastAPI
- **Database**: SQLite (Cloudflare D1 in production)
- **Scheduler**: APScheduler
- **HTTP Client**: httpx

### Frontend

- **Framework**: Vue 3 + TypeScript
- **UI**: Tailwind CSS + DaisyUI
- **Charts**: ECharts
- **Maps**: Leaflet

## Common Tasks

### Adding a New API Endpoint

1. Create route in `src/tsm/api/`
2. Add request/response models
3. Implement business logic in `src/tsm/services/`
4. Write tests in `tests/test_*_api.py`
5. Update API documentation

### Adding a New Data Source

1. Add source to database via API or admin
2. Implement parser in `src/tsm/parser/`
3. Add extraction rules in `src/tsm/intel/`
4. Write tests for parser and extraction

### Fixing a Bug

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify test passes
4. Run all tests to ensure no regressions

## Questions?

- Check existing issues on GitHub
- Read the documentation in `docs/`
- Review `CODE_QUALITY_ANALYSIS.md` for improvement roadmap

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
