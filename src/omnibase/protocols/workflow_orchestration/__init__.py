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
from omnibase.protocols.workflow_orchestration.protocol_workflow_event_bus import (
    ProtocolWorkflowEventBus,
    ProtocolWorkflowEventHandler,
    ProtocolWorkflowEventMessage,
    ProtocolWorkflowStateProjection,
)

# Node registry protocols
from omnibase.protocols.workflow_orchestration.protocol_workflow_node_registry import (
    ProtocolNodeSchedulingResult,
    ProtocolTaskSchedulingCriteria,
    ProtocolWorkflowNodeCapability,
    ProtocolWorkflowNodeInfo,
    ProtocolWorkflowNodeRegistry,
)

# Persistence protocols
from omnibase.protocols.workflow_orchestration.protocol_workflow_persistence import (
    ProtocolEventQueryOptions,
    ProtocolEventStore,
    ProtocolEventStoreResult,
    ProtocolEventStoreTransaction,
    ProtocolSnapshotStore,
    ProtocolWorkflowStateStore,
)

__all__ = [
    # Event bus protocols
    "ProtocolWorkflowEventBus",
    "ProtocolWorkflowEventHandler",
    "ProtocolWorkflowEventMessage",
    "ProtocolWorkflowStateProjection",
    # Node registry protocols
    "ProtocolNodeSchedulingResult",
    "ProtocolTaskSchedulingCriteria",
    "ProtocolWorkflowNodeCapability",
    "ProtocolWorkflowNodeInfo",
    "ProtocolWorkflowNodeRegistry",
    # Persistence protocols
    "ProtocolEventQueryOptions",
    "ProtocolEventStore",
    "ProtocolEventStoreResult",
    "ProtocolEventStoreTransaction",
    "ProtocolSnapshotStore",
    "ProtocolWorkflowStateStore",
]
