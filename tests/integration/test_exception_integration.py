"""
Integration tests demonstrating SPI exception usage across multiple components.

This module provides integration tests that show how exceptions flow
between multiple protocol implementations. These tests validate that
exception handling works correctly when components interact.

Key Integration Patterns Demonstrated:
    1. Handler fallback patterns (multiple handlers)
    2. Registry lookup to handler execution flows
    3. Idempotency check to projection update flows
    4. Error propagation through protocol layers

For single-component unit tests, see:
    tests/unit/test_exceptions.py (exception hierarchy tests)
    tests/unit/test_exception_handlers.py (handler pattern tests)
"""

from __future__ import annotations

import pytest

from omnibase_spi.exceptions import (
    HandlerInitializationError,
    ProtocolHandlerError,
    RegistryError,
)

# Import shared mock classes from tests/conftest.py
from tests.conftest import (
    MockConnectionConfig,
    MockOperationConfig,
    MockProtocolRequest,
    RealisticHandlerRegistry,
    RealisticIdempotencyStore,
    RealisticProjector,
    RealisticProtocolHandler,
)

# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.integration
class TestExceptionRecoveryPatterns:
    """
    Integration tests demonstrating exception recovery patterns with multiple components.

    These tests show fallback patterns when multiple handlers interact.
    For single-component recovery patterns (retry, logging), see:
        tests/unit/test_exception_handlers.py::TestExceptionRecoveryPatterns
    """

    @pytest.mark.asyncio
    async def test_fallback_handler_on_failure(self) -> None:
        """
        Demonstrate fallback pattern using multiple handlers.

        Pattern: Try primary handler, fall back to secondary on failure.
        This is an integration test because it coordinates between two
        independent handler instances.
        """
        primary = RealisticProtocolHandler(
            handler_id="primary",
            simulate_init_failure=True,
        )
        fallback = RealisticProtocolHandler(handler_id="fallback")

        config = MockConnectionConfig()
        active_handler: RealisticProtocolHandler | None = None

        # Try primary, fall back to secondary
        try:
            await primary.initialize(config)
            active_handler = primary
        except HandlerInitializationError:
            await fallback.initialize(config)
            active_handler = fallback

        assert active_handler is fallback
        assert active_handler._handler_id == "fallback"


@pytest.mark.integration
class TestCrossProtocolExceptionHandling:
    """
    Integration tests demonstrating exception handling across multiple protocols.

    These tests show how exceptions should be handled when multiple
    protocol implementations interact.
    """

    @pytest.mark.asyncio
    async def test_registry_and_handler_exception_flow(self) -> None:
        """
        Demonstrate exception flow from registry lookup through handler execution.

        Pattern: Catch different exception types at appropriate layers.
        Registry errors should be caught during setup, handler errors
        during execution.

        This is an integration test because it coordinates:
        1. Registry lookup (first component)
        2. Handler initialization and execution (second component)
        """
        registry = RealisticHandlerRegistry()
        registry.register("http", RealisticProtocolHandler)

        errors_caught: list[str] = []

        # Attempt to get and use handler
        handler: RealisticProtocolHandler
        try:
            # This should fail - kafka not registered
            _ = registry.get("kafka")
            # Code below won't execute due to RegistryError
            handler = RealisticProtocolHandler()
            await handler.initialize(MockConnectionConfig())
        except RegistryError:
            errors_caught.append("RegistryError")
            # Fall back to http handler - we know it's RealisticProtocolHandler
            handler = RealisticProtocolHandler(simulate_execute_failure=True)

        # Now try to use the fallback handler
        await handler.initialize(MockConnectionConfig())

        try:
            await handler.execute(MockProtocolRequest(), MockOperationConfig())
        except ProtocolHandlerError:
            errors_caught.append("ProtocolHandlerError")

        assert errors_caught == ["RegistryError", "ProtocolHandlerError"]

    @pytest.mark.asyncio
    async def test_idempotency_check_before_projection(self) -> None:
        """
        Demonstrate idempotency check followed by projection update.

        Pattern: Check idempotency first, only project if not duplicate.
        Handle both store and projector errors appropriately.

        This is an integration test because it coordinates:
        1. Idempotency store (first component)
        2. Projector (second component)
        """
        store = RealisticIdempotencyStore()
        projector = RealisticProjector()

        event_id = "evt-001"
        idempotency_key = f"order-created:{event_id}"

        # First processing - should succeed
        if store.record_event(event_id, idempotency_key):
            await projector.persist(
                entity_id="order-123",
                domain="orders",
                state={"status": "created"},
                sequence=1,
            )

        # Second processing - should be skipped (duplicate)
        was_duplicate = not store.record_event(event_id, idempotency_key)
        assert was_duplicate

        # Verify state was projected only once
        state = await projector.get_entity_state("order-123", "orders")
        assert state == {"status": "created"}
