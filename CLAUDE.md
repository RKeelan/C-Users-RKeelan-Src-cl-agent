# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands
- Activate virtual environment: `source .venv/bin/activate`
- Install dev dependencies: `uv pip install -e '.[test]'`
- Run all tests: `pytest .`
- Run a single test: `pytest tests/test_cl_agent.py::test_function_name`
- Run tests in a class: `pytest tests/test_cl_agent.py::TestClassName`
- Format code: `black cl_agent tests`
- Type check: `mypy cl_agent`

## Code Style Guidelines
- **Naming**: Use snake_case for variables, functions, and methods; PascalCase for classes
- **Imports**: Group imports in this order: standard library, third-party, local; sort alphabetically within groups
- **Formatting**: Follow PEP 8; line length max 120 characters
- **Typing**: Use type annotations for all function parameters and return values
- **Error Handling**: Use specific exception types, add context to exceptions when re-raising
- **Documentation**: Use docstrings for all public modules, classes, and functions (follow Google style)
- **Testing**: Write pytest unit tests for all new functionality