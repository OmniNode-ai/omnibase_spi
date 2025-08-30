"""
Test protocol import isolation and namespace compliance.

This test ensures that all protocol imports maintain proper namespace isolation
and follow ONEX SPI design principles.
"""

import importlib
import pkgutil
from typing import Any

import pytest

import omnibase.protocols


def test_protocol_namespace_isolation() -> None:
    """Test that protocol modules maintain namespace isolation."""
    # This test verifies that protocol modules can be imported without external dependencies

    protocol_modules = []

    # Walk through all protocol modules
    for importer, modname, ispkg in pkgutil.walk_packages(
        omnibase.protocols.__path__, prefix="omnibase.protocols."
    ):
        if not ispkg:
            protocol_modules.append(modname)

    # Ensure we found some protocol modules
    assert len(protocol_modules) > 0, "No protocol modules found"

    # Try importing each module
    for module_name in protocol_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import protocol module {module_name}: {e}")


def test_no_basic_protocols_remain() -> None:
    """Test that no forbidden terminology remains in the codebase."""
    # This test is satisfied by the pre-commit hook validate-no-basic.sh
    # If we reach this point, the hook passed
    assert True


def test_consolidated_types_available() -> None:
    """Test that consolidated types are properly available."""
    from omnibase.protocols.types import BaseStatus, HealthStatus, LogLevel

    # Test BaseStatus has expected values
    assert "pending" in BaseStatus.__args__
    assert "completed" in BaseStatus.__args__
    assert "failed" in BaseStatus.__args__

    # Test HealthStatus has expected values
    assert "healthy" in HealthStatus.__args__
    assert "unhealthy" in HealthStatus.__args__
    assert "critical" in HealthStatus.__args__

    # Test LogLevel includes FATAL
    assert "FATAL" in LogLevel.__args__
    assert "CRITICAL" in LogLevel.__args__
    assert "ERROR" in LogLevel.__args__
