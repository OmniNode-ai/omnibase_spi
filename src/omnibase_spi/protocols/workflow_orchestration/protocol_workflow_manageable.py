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
            event_metadata: dict[str, "ContextValue"] | None = None
        ) -> bool:
            # Implementation handles state transition with event sourcing

        async def get_workflow_status(
            self,
            workflow_type: str,
            instance_id: UUID
        ) -> "ProtocolWorkflowSnapshot":
            # Implementation returns current workflow snapshot
    ```

Architecture Integration:
    This protocol integrates with the ONEX event-driven orchestration framework:
    - Works with ProtocolWorkflowEventBus for event publication
    - Integrates with ProtocolWorkflowPersistence for state storage
    - Supports ProtocolWorkflowReducer for FSM state reduction
    - Enables workflow instance isolation and correlation tracking
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ProtocolMetadata
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    LiteralTaskState,
    LiteralWorkflowEventType,
    LiteralWorkflowState,
    ProtocolWorkflowEvent,
    ProtocolWorkflowSnapshot,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


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

    async def create_workflow_instance(
        self,
        workflow_type: str,
        instance_id: UUID,
        initial_context: dict[str, "ContextValue"],
        correlation_metadata: "ProtocolMetadata",
        configuration: dict[str, "ContextValue"] | None = None,
    ) -> "ProtocolWorkflowSnapshot": ...

    async def start_workflow_execution(
        self,
        workflow_type: str,
        instance_id: UUID,
        execution_context: dict[str, "ContextValue"],
    ) -> bool: ...

    async def pause_workflow_execution(
        self, workflow_type: str, instance_id: UUID, reason: str | None = None
    ) -> bool: ...

    async def resume_workflow_execution(
        self, workflow_type: str, instance_id: UUID
    ) -> bool: ...

    async def terminate_workflow_execution(
        self,
        workflow_type: str,
        instance_id: UUID,
        termination_reason: str,
        force: bool | None = None,
    ) -> bool: ...

    async def transition_workflow_state(
        self,
        workflow_type: str,
        instance_id: UUID,
        target_state: "LiteralWorkflowState",
        event_metadata: dict[str, "ContextValue"] | None = None,
        causation_id: UUID | None = None,
    ) -> bool: ...

    async def get_workflow_state(
        self, workflow_type: str, instance_id: UUID
    ) -> "LiteralWorkflowState": ...

    async def get_workflow_snapshot(
        self,
        workflow_type: str,
        instance_id: UUID,
        include_task_details: bool | None = None,
    ) -> "ProtocolWorkflowSnapshot": ...

    async def schedule_workflow_task(
        self,
        workflow_type: str,
        instance_id: UUID,
        task_definition: dict[str, "ContextValue"],
        dependencies: list[UUID] | None = None,
    ) -> UUID: ...

    async def update_task_state(
        self,
        workflow_type: str,
        instance_id: UUID,
        task_id: UUID,
        new_state: "LiteralTaskState",
        result_data: dict[str, "ContextValue"] | None = None,
    ) -> bool: ...

    async def get_task_dependencies_status(
        self, workflow_type: str, instance_id: UUID, task_id: UUID
    ) -> dict[UUID, "LiteralTaskState"]: ...

    async def handle_workflow_event(
        self, workflow_event: "ProtocolWorkflowEvent"
    ) -> bool: ...

    async def publish_workflow_event(
        self,
        workflow_type: str,
        instance_id: UUID,
        event_type: "LiteralWorkflowEventType",
        event_data: dict[str, "ContextValue"],
        causation_id: UUID | None = None,
        correlation_chain: list[UUID] | None = None,
    ) -> UUID: ...

    async def get_workflow_execution_metrics(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]: ...

    async def get_workflow_performance_summary(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]: ...

    async def initiate_compensation(
        self,
        workflow_type: str,
        instance_id: UUID,
        compensation_reason: str,
        failed_task_id: UUID | None = None,
    ) -> bool: ...

    async def check_compensation_status(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]: ...

    async def validate_workflow_consistency(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]: ...

    async def get_workflow_health_status(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, "ContextValue"]: ...
