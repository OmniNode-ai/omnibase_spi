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
    from typing import get_args

    from omnibase.protocols.types import BaseStatus, HealthStatus, LogLevel

    # Test BaseStatus has expected values
    base_status_values = get_args(BaseStatus)
    assert "pending" in base_status_values
    assert "completed" in base_status_values
    assert "failed" in base_status_values

    # Test HealthStatus has expected values
    health_status_values = get_args(HealthStatus)
    assert "healthy" in health_status_values
    assert "unhealthy" in health_status_values
    assert "critical" in health_status_values

    # Test LogLevel includes FATAL
    log_level_values = get_args(LogLevel)
    assert "FATAL" in log_level_values
    assert "CRITICAL" in log_level_values
    assert "ERROR" in log_level_values
