# Contributing to GitHub Clear

First off, thank you for considering contributing to GitHub Clear! It's people like you that make this tool better for everyone.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct: be respectful, inclusive, and constructive.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Include your environment details** (OS, Python version, browser)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Use a clear and descriptive title**
- **Describe the enhancement in detail**
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install dependencies**: `uv sync`
3. **Make your changes** and ensure the code works
4. **Test your changes** thoroughly
5. **Update documentation** if needed
6. **Submit a pull request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/github-clear.git
cd github-clear

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Start development server
uv run uvicorn main:app --reload --port 8000
```

## Validation

Install the development dependencies with `uv sync`, then run:

```bash
uv run pytest -q
uv run ruff check .
node --check static/js/app.js
node --test tests/*.test.cjs
```

The JavaScript regression tests use Node.js 18+ and require no npm packages.
Python tests isolate configuration in temporary files and block real provider
requests. They cover batch validation and partial failures, token persistence,
provider pagination, page rendering, and responsiveness during slow API calls.

Repository batches accept 1–1000 names, remove exact duplicates, and return a
result for every unique name. Invalid input returns HTTP 422 before any provider
mutation. The UI selects only visible search results and retains failed items
for retry. `/health` is a local liveness check that needs no provider credentials.

## Style Guidelines

### Python

- Follow PEP 8
- Use type hints where possible
- Write docstrings for functions and classes
- Use meaningful variable names

### JavaScript

- Use modern ES6+ syntax
- Use `const` and `let` instead of `var`
- Add comments for complex logic

### HTML/CSS

- Use semantic HTML elements
- Keep CSS organized and commented
- Follow existing naming conventions

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 50 characters
- Reference issues and pull requests when relevant

Examples:
```
Add custom social link feature
Fix profile preview not updating
Update README with Docker instructions
```

## Project Structure

```
github-clear/
├── main.py              # FastAPI routes and app entry
├── core/                # Core business logic
│   ├── github_api.py    # GitHub API wrapper
│   ├── gitee_api.py     # Gitee API wrapper
│   ├── profile_generator.py  # Profile README generator
│   └── token_manager.py # Token management
├── templates/           # Jinja2 HTML templates
├── static/              # CSS, JS, images
│   ├── css/
│   └── js/
└── config/              # Configuration files
```

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🎉
