"""
Shared test fixtures and helpers for handler protocol tests.

This module provides common mock implementations and factory functions
used across multiple test files in the handlers test suite.
"""

from __future__ import annotations

from typing import Any

from omnibase_core.enums import (
    EnumHandlerRole,
    EnumHandlerType,
    EnumHandlerTypeCategory,
)
from omnibase_core.models.handlers import (
    ModelHandlerDescriptor as CoreModelHandlerDescriptor,
    ModelIdentifier,
)
from omnibase_core.models.primitives import ModelSemVer
from omnibase_spi.protocols.handlers import ProtocolHandler


def _create_mock_descriptor(name: str = "mock-handler") -> CoreModelHandlerDescriptor:
    """Create a mock ModelHandlerDescriptor for testing."""
    return CoreModelHandlerDescriptor(
        handler_name=ModelIdentifier(namespace="test", name=name),
        handler_version=ModelSemVer(major=1, minor=0, patch=0),
        handler_role=EnumHandlerRole.INFRA_HANDLER,
        handler_type=EnumHandlerType.NAMED,
        handler_type_category=EnumHandlerTypeCategory.EFFECT,
    )


class MockProtocolHandler:
    """A minimal mock that satisfies ProtocolHandler protocol for testing."""

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return "mock"

    async def initialize(self, config: Any) -> None:
        """Initialize handler."""
        pass

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Shutdown handler."""
        pass

    async def execute(self, request: Any, operation_config: Any) -> Any:
        """Execute operation."""
        return {}

    def describe(self) -> CoreModelHandlerDescriptor:
        """Describe handler."""
        return _create_mock_descriptor(name="mock-protocol-handler")

    async def health_check(self) -> dict[str, Any]:
        """Check health."""
        return {"healthy": True}


class MockHandlerDescriptor:
    """A class that fully implements the ProtocolHandlerDescriptor protocol.

    This mock provides a complete implementation suitable for testing
    protocol compliance, handler registration, and descriptor-based operations.
    """

    def __init__(
        self,
        handler_type: str = "mock",
        name: str = "mock-handler",
        version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
        priority: int = 10,
    ) -> None:
        """Initialize the mock descriptor.

        Args:
            handler_type: Type identifier for this handler (e.g., "http", "kafka").
            name: Human-readable name for this handler.
            version: Semantic version string (e.g., "1.0.0").
            metadata: Additional key-value metadata. Defaults to basic capabilities.
            priority: Priority for handler selection. Higher values = higher priority.
        """
        self._handler_type = handler_type
        self._name = name
        self._version = version
        self._metadata = (
            metadata
            if metadata is not None
            else {"capabilities": ["read", "write"]}
        )
        self._priority = priority
        self._handler = MockProtocolHandler()

    @property
    def handler_type(self) -> str:
        """Return the type identifier for this handler."""
        return self._handler_type

    @property
    def name(self) -> str:
        """Return human-readable name for this handler."""
        return self._name

    @property
    def version(self) -> str:
        """Return semantic version string."""
        return self._version

    @property
    def metadata(self) -> dict[str, Any]:
        """Return additional key-value metadata."""
        return self._metadata

    @property
    def handler(self) -> ProtocolHandler:
        """Return the actual handler instance."""
        return self._handler

    @property
    def priority(self) -> int:
        """Return priority for handler selection."""
        return self._priority
