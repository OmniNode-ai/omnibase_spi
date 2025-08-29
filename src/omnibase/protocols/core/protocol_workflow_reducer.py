"""
Enhanced Workflow Reducer Protocol for LlamaIndex integration.

This module provides the enhanced reducer protocol that supports both
traditional synchronous state transitions and LlamaIndex workflow-based
asynchronous orchestration with observable state changes.

Author: ONEX Framework Team
"""

from typing import Any, Dict, Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import (
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
    Enhanced reducer protocol with LlamaIndex workflow support.

    Extends the basic reducer pattern to support:
    - Asynchronous workflow-based state transitions
    - Observable state changes via ProtocolNodeResult
    - Complex orchestration through LlamaIndex workflows
    - Monadic composition with error handling
    - Event emission for monitoring and coordination
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
        Synchronous state transition for simple operations.

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

    def get_state_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get the schema definition for this reducer's state.

        Returns:
            Optional[Dict[str, Any]]: JSON schema for state validation,
                                    or None if not available
        """
        return None

    def get_action_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get the schema definition for actions this reducer handles.

        Returns:
            Optional[Dict[str, Any]]: JSON schema for action validation,
                                    or None if not available
        """
        return None
