"""
Enhanced Workflow Reducer Protocol for LlamaIndex integration.

This module provides the enhanced reducer protocol that supports both
traditional synchronous state transitions and LlamaIndex workflow-based
asynchronous orchestration with observable state changes.

Author: ONEX Framework Team
"""

import asyncio
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from llama_index.core.workflow import Workflow

from omnibase.protocols.types.core_types import (
    ProtocolAction,
    ProtocolNodeResult,
    ProtocolState,
)


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

    @abstractmethod
    def initial_state(self) -> ProtocolState:
        """
        Returns the initial state for the reducer.

        Returns:
            ProtocolState: The initial state object
        """
        ...

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def create_workflow(self) -> Optional[Workflow]:
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


class SimpleWorkflowReducer(ProtocolWorkflowReducer):
    """
    Base implementation of ProtocolWorkflowReducer for simple cases.

    Provides default implementations that delegate async operations
    to synchronous dispatch, suitable for reducers that don't need
    complex workflow orchestration.
    """

    async def dispatch_async(
        self, state: ProtocolState, action: ProtocolAction
    ) -> ProtocolNodeResult:
        """
        Default async implementation that wraps synchronous dispatch.

        For simple reducers that don't need workflow orchestration,
        this provides async compatibility by wrapping the sync dispatch.
        """
        try:
            new_state = self.dispatch(state, action)

            # Concrete implementations must provide a result factory
            raise NotImplementedError(
                "Concrete implementations must override this method to provide "
                "protocol-compatible result creation. Success case should return "
                "a ProtocolNodeResult instance created by the implementation."
            )

        except Exception as e:
            # Abstract implementations should override this method to provide proper error handling
            raise NotImplementedError(
                f"Synchronous dispatch failed: {str(e)}. "
                "Concrete implementations must override this method to provide "
                "protocol-compatible error handling and result creation."
            )

    def create_workflow(self) -> Optional[Workflow]:
        """
        Default implementation returns None (no workflow needed).

        Override this method in subclasses that need LlamaIndex workflows.
        """
        return None


class WorkflowOrchestrationMixin:
    """
    Mixin providing common workflow orchestration patterns.

    This mixin can be used by reducers that need to coordinate
    multiple workflow steps or handle complex async operations.
    """

    async def run_workflow_step(
        self,
        workflow: Workflow,
        step_name: str,
        input_data: Any,
        timeout: Optional[float] = None,
    ) -> ProtocolNodeResult:
        """
        Run a single workflow step with error handling and observability.

        Args:
            workflow: LlamaIndex workflow instance
            step_name: Name of the step for logging/tracing
            input_data: Input data for the workflow step
            timeout: Optional timeout for the step

        Returns:
            ProtocolNodeResult: Result with context, events, and error handling
        """
        from datetime import datetime

        from omnibase.protocols.types.core_types import (
            ProtocolErrorInfo,
            ProtocolSystemEvent,
        )

        start_time = datetime.now()

        try:
            # Run workflow step with optional timeout
            if timeout:
                result = await asyncio.wait_for(
                    workflow.run(**input_data), timeout=timeout
                )
            else:
                result = await workflow.run(**input_data)

            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Concrete implementations must provide result factory
            raise NotImplementedError(
                "Concrete implementations must override this method to provide "
                "protocol-compatible result and event creation."
            )

        except asyncio.TimeoutError:
            raise NotImplementedError(
                f"Workflow step '{step_name}' timed out after {timeout}s. "
                "Concrete implementations must override this method to provide "
                "protocol-compatible timeout error handling."
            )

        except Exception as e:
            raise NotImplementedError(
                f"Workflow step '{step_name}' failed: {str(e)}. "
                "Concrete implementations must override this method to provide "
                "protocol-compatible error handling."
            )

    async def coordinate_workflow_sequence(
        self, workflow_steps: List[Any], initial_data: Any
    ) -> ProtocolNodeResult:
        """
        Coordinate a sequence of workflow steps with data flow.

        Args:
            workflow_steps: List of (workflow, step_name, transform_fn) tuples
            initial_data: Initial input data

        Returns:
            ProtocolNodeResult: Final result after all steps complete
        """
        current_data = initial_data
        all_events: List[Any] = []
        combined_provenance: List[str] = []
        combined_metadata: Dict[str, Any] = {}

        for workflow, step_name, transform_fn in workflow_steps:
            # Run workflow step
            step_result = await self.run_workflow_step(
                workflow, step_name, current_data
            )

            if step_result.is_failure:
                # Propagate failure with accumulated context
                # Note: Since these are protocols, concrete implementations
                # must handle context accumulation properly
                return step_result

            # Transform data for next step
            if transform_fn:
                current_data = transform_fn(step_result.value)
            else:
                current_data = step_result.value

            # Accumulate context
            all_events.extend(step_result.events)
            combined_provenance.extend(step_result.provenance)
            combined_metadata.update(step_result.metadata)

        # Concrete implementations must provide result factory
        raise NotImplementedError(
            "Concrete implementations must override this method to provide "
            "protocol-compatible result creation for workflow sequence coordination."
        )
