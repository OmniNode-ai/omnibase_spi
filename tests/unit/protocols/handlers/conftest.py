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
from omnibase_core.models.primitives.model_semver import ModelSemVer


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
