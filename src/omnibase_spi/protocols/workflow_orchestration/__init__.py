"""
ONEX SPI workflow orchestration contracts.

This module provides comprehensive SPI contracts for event-driven workflow
orchestration including state management, event bus protocols,
node discovery, and persistence layer contracts.

All contracts follow ONEX SPI purity principles:
- Protocol interfaces for behavior contracts
- Type definitions for data structures
- No implementations, only pure contracts
- Strong typing throughout
- Event sourcing support
- ONEX naming conventions (Protocol*)

Author: ONEX Framework Team
"""

# Event bus protocols
from omnibase_spi.protocols.workflow_orchestration.protocol_workflow_event_bus import (
    ProtocolLiteralWorkflowStateProjection,
    ProtocolWorkflowEventBus,
    ProtocolWorkflowEventHandler,
    ProtocolWorkflowEventMessage,
)

# Node registry protocols
from omnibase_spi.protocols.workflow_orchestration.protocol_workflow_node_registry import (
    ProtocolNodeSchedulingResult,
    ProtocolTaskSchedulingCriteria,
    ProtocolWorkflowNodeCapability,
    ProtocolWorkflowNodeInfo,
    ProtocolWorkflowNodeRegistry,
)

# Persistence protocols
from omnibase_spi.protocols.workflow_orchestration.protocol_workflow_persistence import (
    ProtocolEventQueryOptions,
    ProtocolEventStore,
    ProtocolEventStoreResult,
    ProtocolEventStoreTransaction,
    ProtocolLiteralWorkflowStateStore,
    ProtocolSnapshotStore,
)

# Additional workflow protocols moved from core
from .protocol_workflow_reducer import ProtocolWorkflowReducer

# Type alias for backward compatibility
ProtocolReducer = ProtocolWorkflowReducer

# Work queue protocols
from .protocol_work_queue import (
    LiteralAssignmentStrategy,
    LiteralWorkQueuePriority,
    ProtocolWorkQueue,
)
from .protocol_workflow_manageable import ProtocolWorkflowManageable

__all__ = [
    "LiteralAssignmentStrategy",
    "LiteralWorkQueuePriority",
    "ProtocolEventQueryOptions",
    "ProtocolEventStore",
    "ProtocolEventStoreResult",
    "ProtocolEventStoreTransaction",
    "ProtocolLiteralWorkflowStateProjection",
    "ProtocolLiteralWorkflowStateStore",
    "ProtocolNodeSchedulingResult",
    # Type alias for backward compatibility
    "ProtocolReducer",
    "ProtocolSnapshotStore",
    "ProtocolTaskSchedulingCriteria",
    "ProtocolWorkQueue",
    "ProtocolWorkflowEventBus",
    "ProtocolWorkflowEventHandler",
    "ProtocolWorkflowEventMessage",
    "ProtocolWorkflowManageable",
    "ProtocolWorkflowNodeCapability",
    "ProtocolWorkflowNodeInfo",
    "ProtocolWorkflowNodeRegistry",
    "ProtocolWorkflowReducer",
]
