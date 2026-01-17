# Agents.md

This document provides the guidelines for the agents. It outlines the roles, responsibilities, and best practices for agents to work on the repository.

## 1) Tools

### CLI tools

Below are the only tools available (other than shell) that can be used when working on the repository:

- uv (command line tool replacing pip for installing and managing Python packages)
- uv (use `uv run` for running python files and modules as well, cannot use python command directly)
- ty (for type checking)
- mypy (for static type checking. required since ty is still in beta)
- ruff (for formatting and linting)

**Basic commands**

```bash
uv add <package>
uv add --dev <package> # for development dependencies
uv remove <package>
uv sync
uv run <file_or_directory>
uv run -m <module>
ty check <file_or_directory>
uv run mypy check -p <file_or_directory> (if not exists, add using `uv add --dev mypy`)
ruff format <file_or_directory>
ruff check <file_or_directory>

uv --help
ruff --help
uv run mypy --help
ty --help
```

## 2) Comments

Don't add even a single line of comments. The only allowed comments are docstrings for functions and classes.
