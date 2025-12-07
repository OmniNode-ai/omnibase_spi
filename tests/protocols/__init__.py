"""Tests for omnibase-spi protocol modules.

This package contains tests for all protocol definitions in omnibase_spi.
Test modules are organized by protocol domain:

- effects: Tests for primitive effect executor protocols
- event_bus: Tests for event bus provider protocols
- handlers: Tests for protocol handler interfaces
- nodes: Tests for node type protocols (compute, effect, reducer, orchestrator)
- registry: Tests for handler registry protocols
"""

# Re-export test modules for package discovery
from tests.protocols import effects, event_bus, handlers, nodes, registry

__all__ = [
    "effects",
    "event_bus",
    "handlers",
    "nodes",
    "registry",
]
