# Contributing to fastapi-health-check

First off, thank you for considering contributing to `fastapi-health-check`! It's people like you that make the open-source community such an amazing place to learn, inspire, and create.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Use welcoming and inclusive language.
- Be respectful of differing viewpoints and experiences.
- Gracefully accept constructive criticism.
- Focus on what is best for the community.
- Show empathy towards other community members.

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please open an issue and include:
- A clear description of the problem.
- Steps to reproduce the issue.
- Your Python and FastAPI versions.
- Any relevant logs or error messages.

### Suggesting Enhancements
We welcome ideas for new features or improvements. Please open an issue to discuss your proposal before starting implementation.

## Local Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

1.  **Fork and Clone** the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/fastapi-health-check.git
    cd fastapi-health-check
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Activate the environment**:
    ```bash
    source .venv/bin/activate
    ```

## Development Workflow

### Branching
Create a descriptive branch name:
- `feature/new-health-check`
- `fix/database-timeout-issue`
- `docs/update-installation-guide`

### Coding Standards
We use `ruff` for linting and formatting, and `mypy` for static type checking.

1.  **Check linting and formatting**:
    ```bash
    uv run ruff check .
    uv run ruff format .
    ```

2.  **Check types**:
    ```bash
    uv run mypy src/
    ```

Ensure all these checks pass before submitting your PR.

## Testing

We use `pytest` for testing. Every new feature or bug fix should include tests.

1.  **Run all tests**:
    ```bash
    uv run pytest
    ```

2.  **Run specific test file**:
    ```bash
    uv run pytest tests/test_registry.py
    ```

## Documentation

If your changes affect the API or add new features, please update the documentation in the `docs/` folder.

1.  **Run documentation server locally**:
    ```bash
    uv run mkdocs serve
    ```

## Pull Request Process

1.  Update the `CONTRIBUTING.md` if your change requires updates to the contribution process.
2.  Ensure tests pass and documentation is updated.
3.  Submit the PR and describe your changes clearly.
4.  Wait for feedback and address any requested changes.
