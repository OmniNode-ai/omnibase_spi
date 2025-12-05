"""
    Enhanced Workflow Reducer Protocol for LlamaIndex integration.

    This module provides the enhanced reducer protocol that supports both
    traditional synchronous state transitions and LlamaIndex workflow-based
    asynchronous orchestration with observable state changes.

Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

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

    def initial_state(self) -> ProtocolState:
        """Get the initial state for workflow FSM.

        Returns:
            Initial state object for workflow execution

        Example:
            ```python
            # Initialize workflow with FSM starting state
            reducer: ProtocolWorkflowReducer = get_reducer()
            state = reducer.initial_state()

            # State typically includes FSM status
            assert state.status == "pending"  # Initial FSM state
            assert state.sequence_number == 0
            ```

        See Also:
            - dispatch: Synchronous state transitions
            - dispatch_async: Asynchronous state transitions with event sourcing
        """
        ...

    def dispatch(
        self, state: "ProtocolState", action: "ProtocolAction"
    ) -> ProtocolState:
        """Dispatch action synchronously for immediate FSM state transition.

        Args:
            state: Current workflow FSM state
            action: Action to apply for state transition

        Returns:
            New immutable state after FSM transition

        Example:
            ```python
            # FSM state transition pattern
            current_state = reducer.initial_state()  # status: "pending"

            # Transition: pending → running
            action = ProtocolAction(type="START_WORKFLOW")
            new_state = reducer.dispatch(current_state, action)
            assert new_state.status == "running"

            # Immutable - original state unchanged
            assert current_state.status == "pending"
            ```

        See Also:
            - dispatch_async: Async dispatch with event sourcing
            - validate_state_transition: FSM transition validation
        """
        ...

    async def dispatch_async(
        self, state: "ProtocolState", action: "ProtocolAction"
    ) -> ProtocolNodeResult:
        """Dispatch action asynchronously with event sourcing and FSM tracking.

        Args:
            state: Current workflow FSM state
            action: Action triggering FSM state transition

        Returns:
            Result with new state, event sourcing data, and FSM metadata

        Raises:
            ValidationError: If FSM transition is invalid
            WorkflowError: If async execution fails

        Example:
            ```python
            # Event-sourced FSM workflow with causation tracking
            state = reducer.initial_state()  # FSM: pending

            # Async transition with event sourcing
            action = ProtocolAction(
                type="START_WORKFLOW",
                correlation_id=correlation_id,
                causation_id=parent_event_id
            )

            result = await reducer.dispatch_async(state, action)

            if result.is_success:
                # FSM state advanced: pending → running
                new_state = result.value
                assert new_state.status == "running"

                # Event sourcing - causation chain preserved
                for event in result.events:
                    print(f"Event: {event.type}")
                    print(f"Sequence: {event.sequence_number}")
                    print(f"Causation: {event.causation_id}")
            ```

        See Also:
            - dispatch: Synchronous FSM transitions
            - ProtocolNodeResult: Result with event sourcing
            - ProtocolWorkflowEvent: Event structure with causation
        """
        ...

    async def create_workflow(self) -> ProtocolWorkflow | None:
        """Create workflow instance for complex orchestration patterns.

        Returns:
            Workflow instance for async orchestration, or None if not supported

        Example:
            ```python
            # Complex workflow orchestration beyond simple FSM
            reducer: ProtocolWorkflowReducer = get_reducer()
            workflow = await reducer.create_workflow()

            if workflow:
                # Run workflow with multi-step FSM coordination
                result = await workflow.run(
                    input_data=context_data,
                    correlation_id=correlation_id
                )

                # Workflow internally manages FSM transitions
                # and event sourcing across multiple steps
            ```

        See Also:
            - ProtocolWorkflow: Workflow execution protocol
            - dispatch_async: Direct FSM state transitions
        """
        ...

    async def validate_state_transition(
        self,
        from_state: "ProtocolState",
        action: "ProtocolAction",
        to_state: "ProtocolState",
    ) -> bool:
        """Validate FSM state transition is legal.

        Args:
            from_state: Source FSM state
            action: Action causing transition
            to_state: Target FSM state

        Returns:
            True if FSM transition is valid, False otherwise

        Example:
            ```python
            # FSM validation for state machine correctness
            from_state = ProtocolState(status="pending")
            to_state = ProtocolState(status="running")
            action = ProtocolAction(type="START_WORKFLOW")

            # Valid FSM transition
            is_valid = await reducer.validate_state_transition(
                from_state, action, to_state
            )
            assert is_valid  # pending → running is valid

            # Invalid FSM transition check
            invalid_to = ProtocolState(status="completed")
            is_valid = await reducer.validate_state_transition(
                from_state, action, invalid_to
            )
            assert not is_valid  # pending → completed invalid without running
            ```

        See Also:
            - dispatch: FSM state transitions
            - LiteralWorkflowState: Valid FSM states
        """
        ...

    async def get_state_schema(self) -> dict[str, "ContextValue"] | None:
        """Get JSON schema for FSM state structure.

        Returns:
            JSON schema dict defining valid state structure, or None

        Example:
            ```python
            # Introspect FSM state schema for validation
            schema = await reducer.get_state_schema()

            if schema:
                # Schema defines FSM state structure
                required_fields = schema.get("required", [])
                assert "status" in required_fields
                assert "sequence_number" in required_fields

                # Use for runtime validation
                validate_against_schema(current_state, schema)
            ```
        """
        ...

    async def get_action_schema(self) -> dict[str, "ContextValue"] | None:
        """Get JSON schema for action structure.

        Returns:
            JSON schema dict defining valid action structure, or None

        Example:
            ```python
            # Introspect action schema for FSM validation
            schema = await reducer.get_action_schema()

            if schema:
                # Schema defines valid FSM actions
                action_types = schema.get("properties", {}).get("type", {})
                print(f"Valid actions: {action_types.get('enum', [])}")

                # Validate action before dispatch
                validate_action_schema(action, schema)
            ```
        """
        ...
