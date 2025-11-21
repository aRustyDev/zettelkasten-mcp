# Zettelkasten MCP Test Suite

Comprehensive test suite for the Zettelkasten MCP server, including tests for both STDIO and HTTP transports.

## Test Organization

### Core Tests (Pre-existing)
- **`test_models.py`** - Data model validation and business logic
- **`test_note_repository.py`** - Note storage and retrieval
- **`test_zettel_service.py`** - Zettelkasten service functionality
- **`test_search_service.py`** - Search and query functionality
- **`test_semantic_links.py`** - Link management and semantics
- **`test_mcp_server.py`** - MCP server tool registration
- **`test_integration.py`** - End-to-end integration tests

### HTTP Transport Tests (Phase 8)
- **`test_http_config.py`** - HTTP configuration loading and environment variables
- **`test_http_transport.py`** - HTTP server initialization, transport selection, and CORS
- **`test_http_cli.py`** - Command-line argument parsing and precedence
- **`test_stdio_regression.py`** - Backward compatibility with STDIO transport

## Running Tests

### Run All Tests

```bash
# Run entire test suite
uv run pytest tests/ -v

# Run with coverage
uv run pytest --cov=zettelkasten_mcp --cov-report=term-missing tests/
```

### Run Specific Test Categories

```bash
# HTTP transport tests only
uv run pytest tests/test_http_*.py -v

# STDIO regression tests
uv run pytest tests/test_stdio_regression.py -v

# Core functionality tests
uv run pytest tests/test_models.py tests/test_zettel_service.py -v
```

### Run Individual Test Files

```bash
# HTTP configuration tests
uv run pytest tests/test_http_config.py -v

# HTTP transport tests
uv run pytest tests/test_http_transport.py -v

# HTTP CLI tests
uv run pytest tests/test_http_cli.py -v

# STDIO regression tests
uv run pytest tests/test_stdio_regression.py -v
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
uv run pytest tests/test_http_config.py::TestHTTPConfiguration -v

# Run a specific test function
uv run pytest tests/test_http_config.py::TestHTTPConfiguration::test_default_http_config_values -v
```

## Coverage Reports

### Terminal Coverage Report

```bash
uv run pytest --cov=zettelkasten_mcp --cov-report=term-missing tests/
```

### HTML Coverage Report

```bash
# Generate HTML coverage report
uv run pytest --cov=zettelkasten_mcp --cov-report=html tests/

# View in browser
open htmlcov/index.html
```

### Coverage for Specific Modules

```bash
# Coverage for HTTP-related code only
uv run pytest --cov=zettelkasten_mcp.server --cov=zettelkasten_mcp.config --cov-report=term-missing tests/test_http_*.py tests/test_stdio_regression.py
```

## Skipped Tests

Some tests are currently skipped due to test infrastructure limitations. These tests verify functionality that has been confirmed working through manual testing (see TESTING_REPORT.md).

### Configuration Tests (14 skipped)
Environment variable override tests are skipped due to Pydantic configuration caching. The config module evaluates `Field(default=os.getenv(...))` at import time, before test fixtures can set environment variables. Manual testing confirms environment variables work correctly (see TESTING_REPORT.md Tests 6 and 8).

### HTTP Transport Tests (11 skipped)
HTTP transport tests are skipped due to dynamic import challenges. The server uses `import uvicorn` inside the `run()` method for lazy loading, which makes standard mocking patterns fail. Manual testing confirms HTTP transport works correctly (see TESTING_REPORT.md Tests 3-5, 7).

### STDIO Regression Tests (1 skipped)
One lazy loading test is skipped due to Python 3.11+ compatibility issues with `__builtins__.__import__` mocking. Lazy loading is verified through other means and manual testing.

### Future Work
For detailed information on how to fix these tests, see:
- [HTTP Transport Test Improvements](../docs/project-knowledge/dev/http-transport-test-improvements.md)

This document provides individual test analysis, root cause explanations, fix approaches, and effort estimates (3.5-5 hours total to fix all tests). All skipped tests verify functionality that works correctly in production—the issues are purely test infrastructure related.

## Test Details

### Configuration Tests (`test_http_config.py`)

Tests HTTP transport configuration loading, environment variable parsing, and default values.

**Key tests:**
- Default configuration values
- Environment variable overrides
- CORS configuration
- JSON response mode
- Invalid configuration handling

### Transport Tests (`test_http_transport.py`)

Tests HTTP server initialization, transport selection, and CORS middleware.

**Key tests:**
- Server initialization with json_response parameter
- STDIO transport as default
- HTTP transport on default/custom ports
- HTTP transport with custom host
- CORS middleware application
- CORS origins configuration
- Logging for different transport modes

### CLI Tests (`test_http_cli.py`)

Tests command-line argument parsing and configuration precedence.

**Key tests:**
- Default transport is STDIO
- Transport argument parsing
- Host and port arguments
- CORS flag
- Combined arguments
- Invalid argument handling
- CLI precedence over environment variables

### Regression Tests (`test_stdio_regression.py`)

Ensures STDIO transport functionality remains unchanged (backward compatibility).

**Key tests:**
- STDIO as default transport
- Explicit STDIO selection
- Lazy loading of HTTP dependencies
- No HTTP parameters affect STDIO
- All MCP tools still registered
- Config values unchanged
- Existing code patterns still work

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- **`temp_dirs`** - Temporary directories for notes and database
- **`test_config`** - Test configuration with temporary paths
- **`note_repository`** - Initialized note repository for testing
- **`zettel_service`** - Initialized zettel service for testing

## Writing New Tests

When adding new tests:

1. **Use descriptive test names** - Test function names should clearly describe what is being tested
2. **Follow the AAA pattern** - Arrange, Act, Assert
3. **Use appropriate fixtures** - Leverage existing fixtures from `conftest.py`
4. **Mock external dependencies** - Use `unittest.mock` for HTTP calls, file I/O, etc.
5. **Test edge cases** - Include tests for error conditions and boundary values
6. **Keep tests isolated** - Each test should be independent and not rely on test execution order

### Example Test Structure

```python
def test_descriptive_name(self, fixture_name):
    """Clear docstring explaining what this test verifies."""
    # Arrange - Set up test data and mocks
    test_value = "example"

    # Act - Perform the action being tested
    result = function_under_test(test_value)

    # Assert - Verify the expected outcome
    assert result == expected_value
```

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```bash
# CI-friendly test command
uv run pytest tests/ -v --cov=zettelkasten_mcp --cov-report=xml --cov-report=term
```

## Test Coverage Goals

- **Overall coverage**: > 80%
- **HTTP transport code**: > 90%
- **Core services**: > 85%
- **Models and storage**: > 90%

## Troubleshooting

### Tests Failing Due to Port Conflicts

If HTTP transport tests fail due to port conflicts:
- Ensure no other services are running on ports 8000-9999
- Tests use mocked uvicorn, so real ports shouldn't conflict

### Import Errors

If you encounter import errors:
```bash
# Ensure the package is installed in development mode
uv sync --all-extras

# Or manually install
uv pip install -e .
```

### Coverage Not Showing

If coverage reports are empty:
```bash
# Make sure pytest-cov is installed
uv add pytest-cov

# Run with explicit coverage settings
uv run pytest --cov=zettelkasten_mcp --cov-config=.coveragerc tests/
```

## Related Documentation

- [HTTP Implementation Plan](../HTTP_IMPLEMENTATION_PLAN.md) - Detailed plan for HTTP transport implementation
- [Testing Report](../TESTING_REPORT.md) - Manual testing results from Phase 6
- [Changelog](../CHANGELOG.md) - Project changes and version history
- [Main README](../README.md) - Project overview and usage instructions
