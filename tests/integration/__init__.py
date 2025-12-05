"""
Integration tests for omnibase_spi protocols.

This package contains integration tests that verify protocols work correctly
with real implementations. Unlike unit tests that test protocol compliance
in isolation, integration tests verify end-to-end behavior.

Run integration tests with:
    poetry run pytest tests/integration/ -v

Skip integration tests in CI:
    poetry run pytest -m "not integration"

Run only integration tests:
    poetry run pytest -m "integration"
"""
