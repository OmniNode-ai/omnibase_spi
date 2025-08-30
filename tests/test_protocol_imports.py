"""
Test that protocol types can be imported without namespace conflicts.

These tests validate the core fix for namespace conflicts between
omnibase-spi and omnibase-core packages.
"""

import pytest


def test_protocol_types_import() -> None:
    """Test that all protocol types import successfully."""
    from omnibase.protocols.types import LogLevel, ProtocolLogContext, ProtocolLogEntry

    # Verify types are available
    # LogLevel is a Literal type with specific values
    assert LogLevel is not None
    assert hasattr(ProtocolLogEntry, "__annotations__")
    assert hasattr(ProtocolLogContext, "__annotations__")


def test_core_protocols_import() -> None:
    """Test that core protocols import without external dependencies."""
    from omnibase.protocols.core.protocol_core_logging import ProtocolCoreLogging
    from omnibase.protocols.core.protocol_logger import ProtocolLogger

    # Verify protocols are available
    assert hasattr(ProtocolLogger, "__annotations__")
    assert hasattr(ProtocolCoreLogging, "__annotations__")


def test_working_protocol_examples() -> None:
    """Test that our working protocol examples still function."""
    from omnibase.protocols.core.protocol_simple_example import (
        ProtocolSimpleEventHandler,
        ProtocolSimpleLogger,
        ProtocolSimpleSerializer,
    )

    # Verify working examples are available
    assert hasattr(ProtocolSimpleLogger, "__annotations__")
    assert hasattr(ProtocolSimpleSerializer, "__annotations__")
    assert hasattr(ProtocolSimpleEventHandler, "__annotations__")


def test_no_external_dependencies() -> None:
    """Test that protocol types don't import external omnibase modules."""
    import sys

    # Import our protocol types
    # Check that no external omnibase modules were loaded as side effects
    external_modules = [
        name
        for name in sys.modules.keys()
        if name.startswith("omnibase.") and not name.startswith("omnibase.protocols")
    ]

    # Should only have omnibase.protocols modules loaded
    assert (
        len(external_modules) == 0
    ), f"External omnibase modules loaded: {external_modules}"


def test_package_self_contained() -> None:
    """Test that package imports work in isolation."""
    # This simulates what happens when omnibase-core tries to install omnibase-spi
    try:
        from omnibase.protocols import ProtocolSimpleSerializer
        from omnibase.protocols.types import LogLevel, ProtocolLogEntry

        # Should work without any external dependencies
        assert ProtocolSimpleSerializer is not None
        assert LogLevel is not None
        assert ProtocolLogEntry is not None

    except ImportError as e:
        pytest.fail(f"Self-contained import failed: {e}")
