"""
    Enhanced Workflow Reducer Protocol for LlamaIndex integration.

    This module provides the enhanced reducer protocol that supports both
    traditional synchronous state transitions and LlamaIndex workflow-based
    asynchronous orchestration with observable state changes.

Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolAction,
    ProtocolNodeResult,
    ProtocolState,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolWorkflow(Protocol):
    """Protocol for workflow objects - replaces LlamaIndex dependency."""

    async def run(self, **kwargs: "ContextValue") -> "ContextValue": ...


@runtime_checkable
class ProtocolWorkflowReducer(Protocol):
    """
            Enhanced reducer protocol with workflow support.

        Extends the basic reducer pattern to support:
            - Asynchronous workflow-based state transitions
        - Observable state changes via ProtocolNodeResult
        - Complex orchestration through workflow patterns
        - Monadic composition with error handling
        - Event emission for monitoring and coordination

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        # UserWorkflowReducer would implement the protocol interface
        # All methods defined in the protocol contract

    # Usage in application
    reducer: "ProtocolWorkflowReducer" = UserWorkflowReducer()

    # Get initial state
        state = reducer.initial_state()

    # Synchronous dispatch
    action = {"type": "INCREMENT_SESSION"}
        new_state = reducer.dispatch(state, action)

    # Asynchronous dispatch
        async_action = {
    "type": "CREATE_USER",
    "payload": {"name": "Alice", "email": "alice@example.com"}
        }
        result = await reducer.dispatch_async(state, async_action)

    if result.is_success:
        final_state = result.value
    print(f"User created, events: {result.events}")
    else:
    print(f"Error: {result.error}")
        ```

    State Management Patterns:
        - Immutable state updates (always return new state objects)
        - Event sourcing support through ProtocolNodeResult.events
        - Error propagation via monadic composition
        - Observable state changes for UI/monitoring integration
    """

    def initial_state(self) -> ProtocolState: ...

    def dispatch(
        self, state: "ProtocolState", action: "ProtocolAction"
    ) -> ProtocolState: ...

    async def dispatch_async(
        self, state: "ProtocolState", action: "ProtocolAction"
    ) -> ProtocolNodeResult: ...

    async def create_workflow(self) -> ProtocolWorkflow | None: ...

    async def validate_state_transition(
        self,
        from_state: "ProtocolState",
        action: "ProtocolAction",
        to_state: "ProtocolState",
    ) -> bool: ...

    async def get_state_schema(self) -> dict[str, ContextValue] | None: ...

    async def get_action_schema(self) -> dict[str, ContextValue] | None: ...
