"""
Protocol for workflow-manageable entities in the ONEX orchestration framework.

This protocol defines the contract for entities that can participate in workflow
orchestration, state management, and execution coordination. It supports event-driven
FSM patterns with event sourcing, workflow instance isolation, and distributed
task coordination.

Key Features:
    - Workflow lifecycle management (create, start, pause, resume, terminate)
    - FSM state transitions with event sourcing
    - Execution monitoring and performance metrics
    - Instance isolation using {workflowType, instanceId} pattern
    - Compensation actions for saga pattern support
    - Distributed task coordination and dependency management

Example Usage:
    ```python
    from omnibase_spi.protocols.core import ProtocolWorkflowManageable
    from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import WorkflowState
    from uuid import UUID

    class WorkflowEngine(ProtocolWorkflowManageable):
        async def transition_workflow_state(
            self,
            workflow_type: str,
            instance_id: UUID,
            target_state: WorkflowState,
            event_metadata: dict[str, str] | None = None
        ) -> bool:
            # Implementation handles state transition with event sourcing
            pass

        async def get_workflow_status(
            self,
            workflow_type: str,
            instance_id: UUID
        ) -> ProtocolWorkflowSnapshot:
            # Implementation returns current workflow snapshot
            pass
    ```

Architecture Integration:
    This protocol integrates with the ONEX event-driven orchestration framework:
    - Works with ProtocolWorkflowEventBus for event publication
    - Integrates with ProtocolWorkflowPersistence for state storage
    - Supports ProtocolWorkflowReducer for FSM state reduction
    - Enables workflow instance isolation and correlation tracking
"""

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import (
        ContextValue,
        CorrelationMetadata,
        ExecutionContext,
    )
    from omnibase_spi.protocols.types.workflow_orchestration_types import (
        ProtocolWorkflowEvent,
        ProtocolWorkflowSnapshot,
        ProtocolWorkflowTask,
        TaskState,
        WorkflowEventType,
        WorkflowExecutionMetrics,
        WorkflowState,
    )


@runtime_checkable
class ProtocolWorkflowManageable(Protocol):
    """
    Protocol for entities that can be managed within workflow orchestration.

    This protocol defines the contract for workflow lifecycle management,
    state transitions, execution monitoring, and event coordination within
    the ONEX distributed orchestration framework.

    Key Capabilities:
        - Complete workflow lifecycle management
        - Event-driven state transitions with FSM support
        - Real-time execution monitoring and metrics
        - Workflow instance isolation and correlation
        - Compensation action support for saga patterns
        - Distributed task coordination and dependency resolution
    """

    # Workflow Lifecycle Management

    async def create_workflow_instance(
        self,
        workflow_type: str,
        instance_id: UUID,
        initial_context: dict[str, str],
        correlation_metadata: "CorrelationMetadata",
        configuration: Optional[dict[str, str]] = None,
    ) -> "ProtocolWorkflowSnapshot":
        """
        Create a new workflow instance with initial configuration.

        Creates a new workflow instance following the {workflowType, instanceId}
        isolation pattern. The instance starts in 'pending' state and requires
        explicit start_workflow_execution call to begin processing.

        Args:
            workflow_type: Type identifier for the workflow class
            instance_id: Unique identifier for this workflow instance
            initial_context: Initial workflow context data
            correlation_metadata: Correlation tracking metadata
            configuration: Optional workflow configuration parameters

        Returns:
            Initial workflow snapshot with 'pending' state

        Raises:
            ValueError: If workflow_type is invalid or instance_id conflicts
            RuntimeError: If workflow creation fails due to system constraints
        """
        ...

    async def start_workflow_execution(
        self,
        workflow_type: str,
        instance_id: UUID,
        execution_context: "ExecutionContext",
    ) -> bool:
        """
        Start execution of a pending workflow instance.

        Transitions workflow from 'pending' to 'initializing' state and
        begins the workflow execution process. Publishes workflow.started
        event to the event bus.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            execution_context: Context for workflow execution

        Returns:
            True if workflow execution started successfully

        Raises:
            ValueError: If workflow instance doesn't exist or not in 'pending' state
            RuntimeError: If execution startup fails
        """
        ...

    async def pause_workflow_execution(
        self, workflow_type: str, instance_id: UUID, reason: Optional[str] = None
    ) -> bool:
        """
        Pause a running workflow instance.

        Transitions workflow to 'paused' state and stops processing new tasks
        while preserving current state. Running tasks continue to completion.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            reason: Optional reason for pausing

        Returns:
            True if workflow was successfully paused

        Raises:
            ValueError: If workflow instance doesn't exist or cannot be paused
        """
        ...

    async def resume_workflow_execution(
        self, workflow_type: str, instance_id: UUID
    ) -> bool:
        """
        Resume a paused workflow instance.

        Transitions workflow from 'paused' to 'running' state and resumes
        normal task processing from the current state.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier

        Returns:
            True if workflow was successfully resumed

        Raises:
            ValueError: If workflow instance doesn't exist or not in 'paused' state
        """
        ...

    async def terminate_workflow_execution(
        self,
        workflow_type: str,
        instance_id: UUID,
        termination_reason: str,
        force: bool = False,
    ) -> bool:
        """
        Terminate a workflow instance.

        Stops workflow execution and transitions to 'cancelled' or 'failed' state
        depending on termination reason. Can optionally force immediate termination.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            termination_reason: Reason for termination
            force: If True, immediately terminate without graceful shutdown

        Returns:
            True if workflow was successfully terminated

        Raises:
            RuntimeError: If termination fails or workflow cannot be stopped
        """
        ...

    # State Management and Transitions

    async def transition_workflow_state(
        self,
        workflow_type: str,
        instance_id: UUID,
        target_state: "WorkflowState",
        event_metadata: Optional[dict[str, str]] = None,
        causation_id: Optional[UUID] = None,
    ) -> bool:
        """
        Transition workflow to a new state with event sourcing.

        Performs FSM state transition and publishes state.transitioned event
        with full causation tracking. Validates state transition rules before
        applying changes.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            target_state: Desired workflow state
            event_metadata: Additional metadata for the transition event
            causation_id: ID of the event that caused this transition

        Returns:
            True if state transition was successful

        Raises:
            ValueError: If target_state transition is not allowed from current state
            RuntimeError: If state transition fails due to system error
        """
        ...

    async def get_workflow_state(
        self, workflow_type: str, instance_id: UUID
    ) -> "WorkflowState":
        """
        Get current state of a workflow instance.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier

        Returns:
            Current workflow state

        Raises:
            ValueError: If workflow instance doesn't exist
        """
        ...

    async def get_workflow_snapshot(
        self, workflow_type: str, instance_id: UUID, include_task_details: bool = True
    ) -> "ProtocolWorkflowSnapshot":
        """
        Get complete snapshot of workflow instance state.

        Returns comprehensive workflow snapshot including current state,
        task status, context data, and execution metrics.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            include_task_details: Whether to include detailed task information

        Returns:
            Complete workflow snapshot

        Raises:
            ValueError: If workflow instance doesn't exist
        """
        ...

    # Task Coordination and Management

    async def schedule_workflow_task(
        self,
        workflow_type: str,
        instance_id: UUID,
        task_definition: "ProtocolWorkflowTask",
        dependencies: Optional[list[UUID]] = None,
    ) -> UUID:
        """
        Schedule a new task within the workflow instance.

        Creates and schedules a task with optional dependencies. Task will
        not execute until all dependencies are resolved.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            task_definition: Task configuration and requirements
            dependencies: Optional list of task IDs this task depends on

        Returns:
            Unique task identifier

        Raises:
            ValueError: If workflow instance doesn't exist or task definition is invalid
            RuntimeError: If task scheduling fails
        """
        ...

    async def update_task_state(
        self,
        workflow_type: str,
        instance_id: UUID,
        task_id: UUID,
        new_state: "TaskState",
        result_data: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Update the state of a workflow task.

        Updates task state and optionally stores result data. Automatically
        checks for dependency resolution and schedules waiting tasks.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            task_id: Unique task identifier
            new_state: New task state
            result_data: Optional task result data

        Returns:
            True if task state was successfully updated

        Raises:
            ValueError: If workflow, task doesn't exist, or state transition invalid
        """
        ...

    async def get_task_dependencies_status(
        self, workflow_type: str, instance_id: UUID, task_id: UUID
    ) -> dict[UUID, "TaskState"]:
        """
        Get status of all dependencies for a specific task.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            task_id: Unique task identifier

        Returns:
            Dictionary mapping dependency task IDs to their current states

        Raises:
            ValueError: If workflow or task doesn't exist
        """
        ...

    # Event Handling and Coordination

    async def handle_workflow_event(
        self, workflow_event: "ProtocolWorkflowEvent"
    ) -> bool:
        """
        Handle an incoming workflow event.

        Processes workflow events according to event type and current workflow
        state. Supports event sourcing patterns with sequence number tracking.

        Args:
            workflow_event: Workflow event to process

        Returns:
            True if event was successfully processed

        Raises:
            ValueError: If event format is invalid
            RuntimeError: If event processing fails
        """
        ...

    async def publish_workflow_event(
        self,
        workflow_type: str,
        instance_id: UUID,
        event_type: "WorkflowEventType",
        event_data: dict[str, str],
        causation_id: Optional[UUID] = None,
        correlation_chain: Optional[list[UUID]] = None,
    ) -> UUID:
        """
        Publish a workflow event to the event bus.

        Creates and publishes workflow event with proper sequence numbering
        and causation tracking for event sourcing.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            event_type: Type of event being published
            event_data: Event payload data
            causation_id: ID of the event that caused this event
            correlation_chain: Full correlation chain for tracking

        Returns:
            Unique event identifier

        Raises:
            RuntimeError: If event publication fails
        """
        ...

    # Execution Monitoring and Metrics

    async def get_workflow_execution_metrics(
        self, workflow_type: str, instance_id: UUID
    ) -> "WorkflowExecutionMetrics":
        """
        Get execution metrics for a workflow instance.

        Returns comprehensive metrics including execution time, task counts,
        resource usage, and performance statistics.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier

        Returns:
            Workflow execution metrics

        Raises:
            ValueError: If workflow instance doesn't exist
        """
        ...

    async def get_workflow_performance_summary(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]:
        """
        Get performance summary for a workflow instance.

        Returns key performance indicators and summary statistics
        for workflow execution monitoring.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier

        Returns:
            Dictionary containing performance summary data

        Raises:
            ValueError: If workflow instance doesn't exist
        """
        ...

    # Compensation and Recovery

    async def initiate_compensation(
        self,
        workflow_type: str,
        instance_id: UUID,
        compensation_reason: str,
        failed_task_id: Optional[UUID] = None,
    ) -> bool:
        """
        Initiate compensation actions for workflow failure recovery.

        Starts saga pattern compensation by executing compensation actions
        for completed tasks in reverse order. Transitions workflow to
        'compensating' state during the process.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier
            compensation_reason: Reason for initiating compensation
            failed_task_id: Optional ID of the task that triggered compensation

        Returns:
            True if compensation was successfully initiated

        Raises:
            ValueError: If workflow instance doesn't exist
            RuntimeError: If compensation initiation fails
        """
        ...

    async def check_compensation_status(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]:
        """
        Check status of ongoing compensation actions.

        Returns status information about compensation progress including
        completed, pending, and failed compensation actions.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier

        Returns:
            Dictionary containing compensation status information

        Raises:
            ValueError: If workflow instance doesn't exist or not compensating
        """
        ...

    # Health and Diagnostics

    async def validate_workflow_consistency(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]:
        """
        Validate internal consistency of workflow state.

        Performs consistency checks on workflow state, task dependencies,
        event sequencing, and data integrity.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier

        Returns:
            Dictionary containing validation results and any issues found

        Raises:
            ValueError: If workflow instance doesn't exist
        """
        ...

    async def get_workflow_health_status(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]:
        """
        Get health status of a workflow instance.

        Returns health indicators including resource usage, execution progress,
        error counts, and system health metrics.

        Args:
            workflow_type: Type identifier for the workflow
            instance_id: Unique workflow instance identifier

        Returns:
            Dictionary containing workflow health metrics

        Raises:
            ValueError: If workflow instance doesn't exist
        """
        ...
