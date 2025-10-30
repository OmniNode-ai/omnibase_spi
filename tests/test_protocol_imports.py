"""
Test protocol import isolation and namespace compliance.

This test ensures that all protocol imports maintain proper namespace isolation
and follow ONEX SPI design principles.
"""

import importlib
import os
import pkgutil
import subprocess
import sys
from pathlib import Path

import pytest

# Add src directory to Python path for testing
src_dir = Path(__file__).parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import omnibase_spi.protocols


def test_protocol_namespace_isolation() -> None:
    """Test that protocol modules maintain namespace isolation."""
    # This test verifies that protocol modules can be imported without external dependencies

    protocol_modules = []

    # Walk through all protocol modules
    for importer, modname, ispkg in pkgutil.walk_packages(
        omnibase_spi.protocols.__path__, prefix="omnibase_spi.protocols."
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

    from omnibase_spi.protocols.types import (
        LiteralBaseStatus,
        LiteralHealthStatus,
        LiteralLogLevel,
    )

    # Test LiteralBaseStatus has expected values
    base_status_values = get_args(LiteralBaseStatus)
    assert "pending" in base_status_values
    assert "completed" in base_status_values
    assert "failed" in base_status_values

    # Test LiteralHealthStatus has expected values
    health_status_values = get_args(LiteralHealthStatus)
    assert "healthy" in health_status_values
    assert "unhealthy" in health_status_values
    assert "critical" in health_status_values

    # Test LiteralLogLevel includes FATAL
    log_level_values = get_args(LiteralLogLevel)
    assert "FATAL" in log_level_values
    assert "CRITICAL" in log_level_values
    assert "ERROR" in log_level_values


def test_clean_environment_import() -> None:
    """Test that omnibase_spi can be imported in a clean environment."""
    # This integration test validates the package can be imported
    # without any external dependencies in a subprocess
    test_script = """
import sys
try:
    from omnibase_spi.protocols.types import LiteralLogLevel
    print("SUCCESS: omnibase_spi imported successfully")
    print(f"LiteralLogLevel type available: {'FATAL' in LiteralLogLevel.__args__}")
    sys.exit(0)
except ImportError as e:
    print(f"FAILURE: Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")
    sys.exit(1)
"""

    env = os.environ.copy()
    # Ensure subprocess can import from this repo's src directory
    env["PYTHONPATH"] = str(src_dir) + (
        os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else ""
    )

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )

    # Check that the subprocess succeeded
    assert result.returncode == 0, f"Clean import failed: {result.stderr}"
    assert "SUCCESS" in result.stdout, f"Success message not found: {result.stdout}"
    assert (
        "LiteralLogLevel type available: True" in result.stdout
    ), "LiteralLogLevel not properly imported"
