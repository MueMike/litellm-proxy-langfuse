# Contributing to LiteLLM Proxy with LangFuse

Thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/MueMike/litellm-proxy-langfuse/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing feature requests in [Issues](https://github.com/MueMike/litellm-proxy-langfuse/issues)
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes:
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. Run tests and linting:
   ```bash
   make test
   make lint
   make format
   ```

5. Commit your changes:
   ```bash
   git commit -m "Add feature: description"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a Pull Request with:
   - Clear title and description
   - Reference to related issues
   - Summary of changes
   - Testing performed

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/MueMike/litellm-proxy-langfuse.git
cd litellm-proxy-langfuse
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
make dev-install
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your test credentials
```

5. Run tests:
```bash
make test
```

## Code Style

- Follow PEP 8 style guide
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 100 characters
- Add type hints where appropriate
- Write docstrings for functions and classes

### Example:

```python
def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    provider: Optional[str] = None,
) -> float:
    """
    Calculate cost for API call based on token usage.
    
    Args:
        model: Model name
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        provider: Optional provider name
        
    Returns:
        Estimated cost in USD
    """
    # Implementation
    pass
```

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Test both success and error cases

### Running Tests:

```bash
# All tests
make test

# Specific test file
pytest tests/test_proxy.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update configuration examples if needed
- Add examples for new features

## Release Process

1. Update version in `pyproject.toml` and `src/__init__.py`
2. Update CHANGELOG.md
3. Create and tag release
4. Build and publish Docker image

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion in [GitHub Discussions](https://github.com/MueMike/litellm-proxy-langfuse/discussions)
- Contact maintainers

Thank you for contributing! 🎉
