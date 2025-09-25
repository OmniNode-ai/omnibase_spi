"""
Enhanced Workflow Reducer Protocol for LlamaIndex integration.

This module provides the enhanced reducer protocol that supports both
traditional synchronous state transitions and LlamaIndex workflow-based
asynchronous orchestration with observable state changes.

Author: ONEX Framework Team
"""

from typing import Any, Optional, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolAction,
    ProtocolNodeResult,
    ProtocolState,
)


@runtime_checkable
class ProtocolWorkflow(Protocol):
    """Protocol for workflow objects - replaces LlamaIndex dependency."""

    async def run(self, **kwargs: Any) -> Any:
        """Execute the workflow with given parameters."""
        ...


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
        class UserWorkflowReducer:
            def initial_state(self) -> ProtocolState:
                return {
                    "users": {},
                    "session_count": 0,
                    "last_activity": None
                }

            def dispatch(self, state: ProtocolState, action: ProtocolAction) -> ProtocolState:
                # Synchronous state transitions
                if action["type"] == "INCREMENT_SESSION":
                    return {**state, "session_count": state["session_count"] + 1}
                return state

            async def dispatch_async(self, state: ProtocolState,
                                   action: ProtocolAction) -> ProtocolNodeResult:
                # Asynchronous workflow-based transitions
                if action["type"] == "CREATE_USER":
                    try:
                        # Complex workflow: validate, create, notify
                        user_data = await self._validate_user(action["payload"])
                        user_id = await self._create_user_in_db(user_data)
                        await self._send_welcome_email(user_id)

                        new_state = {
                            **state,
                            "users": {**state["users"], user_id: user_data}
                        }

                        return ProtocolNodeResult(
                            value=new_state,
                            is_success=True,
                            events=[{"type": "user_created", "user_id": user_id}]
                        )
                    except Exception as e:
                        return ProtocolNodeResult(
                            is_failure=True,
                            error={"message": str(e), "retryable": True}
                        )

        # Usage in application
        reducer: ProtocolWorkflowReducer = UserWorkflowReducer()

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

    def initial_state(self) -> ProtocolState:
        """
        Returns the initial state for the reducer.

        Returns:
            ProtocolState: The initial state object
        """
        ...

    def dispatch(self, state: ProtocolState, action: ProtocolAction) -> ProtocolState:
        """
        Synchronous state transition for basic operations.

        Args:
            state: Current state
            action: Action to process

        Returns:
            ProtocolState: New state after applying action
        """
        ...

    async def dispatch_async(
        self, state: ProtocolState, action: ProtocolAction
    ) -> ProtocolNodeResult:
        """
        Asynchronous workflow-based state transition.

        This method enables complex state transitions that may involve:
        - Multiple async operations
        - External service calls
        - Error recovery and retry logic
        - Observable state change events
        - Integration with LlamaIndex workflows

        Args:
            state: Current state
            action: Action to process

        Returns:
            ProtocolNodeResult: Monadic result with new state,
                                  context, events, and error handling
        """
        ...

    def create_workflow(self) -> Optional[ProtocolWorkflow]:
        """
        Factory method for creating LlamaIndex workflow instances.

        Returns:
            Optional[Workflow]: Workflow instance for complex orchestration,
                              or None if using synchronous dispatch only
        """
        ...

    def validate_state_transition(
        self, from_state: ProtocolState, action: ProtocolAction, to_state: ProtocolState
    ) -> bool:
        """
        Validate that a state transition is legal.

        Args:
            from_state: Source state
            action: Action being applied
            to_state: Target state

        Returns:
            bool: True if transition is valid, False otherwise
        """
        # Default implementation allows all transitions
        return True

    def get_state_schema(self) -> Optional[dict[str, Any]]:
        """
        Get the schema definition for this reducer's state.

        Returns:
            Optional[dict[str, Any]]: JSON schema for state validation,
                                    or None if not available
        """
        return None

    def get_action_schema(self) -> Optional[dict[str, Any]]:
        """
        Get the schema definition for actions this reducer handles.

        Returns:
            Optional[dict[str, Any]]: JSON schema for action validation,
                                    or None if not available
        """
        return None
