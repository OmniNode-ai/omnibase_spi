# ONEX Service Provider Interface (omnibase-spi)

A pure protocol interface repository defining service contracts for the ONEX distributed orchestration framework. This SPI maintains strict architectural purity with zero implementation dependencies, providing type-safe contracts for workflow orchestration, event sourcing, MCP tool integration, and distributed service coordination.

## Repository Overview

**omnibase-spi** serves as the foundational contract layer for the ONEX ecosystem, defining protocol interfaces that enable:

- **Event-Driven Workflow Orchestration** with FSM states and event sourcing
- **Model Context Protocol (MCP) Integration** for distributed tool coordination  
- **Service Discovery and Registry Management** with health monitoring
- **Strict SPI Purity** using `typing.Protocol` for all contracts
- **Zero Implementation Dependencies** - protocols only, no concrete models

## Architecture Philosophy

### Core Principles

1. **Protocol-First Design**: All services defined through Python `Protocol` interfaces
2. **Namespace Isolation**: Complete separation from implementation packages (`omnibase_spi.protocols.*` only)
3. **Event Sourcing Patterns**: Sequence numbers, causation tracking, and replay capabilities
4. **Workflow Isolation**: `{workflowType, instanceId}` isolation with correlation chains
5. **Type Safety**: Strong typing with no `Any` usage in public interfaces

### Important Protocol Distinctions

**ProtocolOnexInputState vs ProtocolWorkflowInputState**

These protocols serve completely different purposes and should not be consolidated:

- **ProtocolOnexInputState** (defined in `protocol_core_types.py`):
  - **Purpose**: Format conversion and string transformation operations
  - **Domain**: Schema/naming conventions, code generation
  - **Attributes**: `input_string`, `source_format`, `metadata`
  - **Validation Method**: `validate_onex_input()` - validates input format for transformation
  - **Usage**: Used by naming convention utilities, class/file name generators

- **ProtocolWorkflowInputState** (defined in `protocol_workflow_orchestration_types.py`):
  - **Purpose**: Workflow orchestration input data and parameters
  - **Domain**: Workflow orchestration, event-driven FSM
  - **Attributes**: `workflow_type`, `input_data`, `parameters`, `metadata`
  - **Validation Method**: `validate_workflow_input()` - validates workflow orchestration input
  - **Usage**: Used by workflow orchestrator for FSM state management

**Why They Are Distinct**: These protocols represent fundamentally different domain concepts. One handles string/format transformations (ONEX input), while the other handles workflow orchestration data (Workflow input). Consolidating them would violate domain separation and semantic clarity.

### Domain Organization

```
src/omnibase_spi/protocols/
├── core/                         # System-level contracts
│   ├── protocol_onex_envelope.py       # Message envelope patterns
│   ├── protocol_onex_reply.py          # Request-response contracts
│   ├── protocol_workflow_reducer.py    # FSM state reduction
│   ├── protocol_node_registry.py       # Node discovery and management
│   ├── protocol_logger.py              # Logging protocols
│   ├── protocol_health_monitor.py      # Health monitoring
│   └── ... (30+ core protocol files)   # Additional system protocols
├── workflow_orchestration/      # Event-driven FSM orchestration
│   ├── protocol_workflow_event_bus.py      # Event sourcing patterns
│   ├── protocol_workflow_node_registry.py  # Workflow node coordination
│   ├── protocol_workflow_persistence.py    # State persistence contracts
│   └── protocol_work_queue.py              # Work queue management
├── mcp/                         # Model Context Protocol integration
│   ├── protocol_mcp_registry.py            # Tool registration and discovery
│   ├── protocol_mcp_tool_proxy.py          # Tool execution proxying
│   ├── protocol_mcp_monitor.py             # Health and metrics monitoring
│   ├── protocol_mcp_validator.py           # Request validation
│   ├── protocol_mcp_subsystem_client.py    # Subsystem client integration
│   └── protocol_mcp_discovery.py           # MCP service discovery
├── event_bus/                   # Event messaging infrastructure
│   ├── protocol_event_bus.py               # Core event bus operations
│   ├── protocol_kafka_adapter.py           # Kafka integration contract
│   ├── protocol_redpanda_adapter.py        # RedPanda integration
│   └── protocol_event_bus_service.py       # Event bus service protocols
├── container/                   # Dependency injection and service location
│   ├── protocol_service_registry.py        # Service registry contracts
│   ├── protocol_artifact_container.py      # Artifact management
│   └── protocol_container_service.py       # Container service protocols
├── validation/                  # Validation and compliance protocols
│   ├── protocol_validation.py              # General validation protocols
│   ├── protocol_compliance_validator.py    # Compliance validation
│   └── protocol_import_validator.py        # Import validation
├── file_handling/              # File processing protocols
│   ├── protocol_file_reader.py            # File reading protocols
│   └── protocol_file_type_handler.py      # File type handling
├── memory/                     # Memory operation protocols
│   ├── protocol_memory_base.py            # Base memory protocols
│   ├── protocol_memory_operations.py      # Memory operations
│   └── ... (additional memory protocols)   # Extended memory functionality
├── discovery/                  # Service and handler discovery
│   └── protocol_handler_discovery.py      # Handler discovery protocols
└── types/                      # Shared type definitions
    ├── protocol_workflow_orchestration_types.py # FSM states, events, tasks
    ├── protocol_mcp_types.py                   # MCP tool and subsystem types
    ├── protocol_core_types.py                  # Base system types
    ├── protocol_event_bus_types.py             # Event messaging types
    ├── protocol_container_types.py             # Container and DI types
    ├── protocol_file_handling_types.py         # File processing types
    └── protocol_discovery_types.py             # Discovery types
```

## Key Protocol Domains

### 1. Workflow Orchestration Protocols

**Event-Driven FSM with Event Sourcing**

```python
# Import protocols from workflow orchestration module
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolWorkflowEventBus,
    ProtocolWorkflowNodeRegistry,
    ProtocolEventStore
)

# Import types from the types module
from omnibase_spi.protocols.types import (
    ProtocolWorkflowEvent,
    ProtocolWorkflowSnapshot,
    LiteralWorkflowState,
    LiteralTaskState,
    LiteralWorkflowEventType
)

# Import additional workflow types directly
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    ProtocolWorkflowContext,
    ProtocolTaskConfiguration
)

# Protocol usage example - Event handler following protocol contract
async def handle_workflow_event(
    event: ProtocolWorkflowEvent,
    context: dict[str, "ContextValue"]
) -> None:
    """
    Example of protocol-compliant event handler.
    Event contains: sequence_number, causation_id, correlation_chain
    Enables full event sourcing with causation tracking.
    """
    # Protocol contract ensures these fields exist
    event_type: LiteralWorkflowEventType = event.event_type
    workflow_type: str = event.workflow_type
    instance_id: UUID = event.instance_id
    sequence_number: int = event.sequence_number

    # Process according to event type
    if event_type == "workflow.started":
        # Handle workflow start
        pass
    elif event_type == "task.completed":
        # Handle task completion
        pass

# Protocol-based workflow snapshot structure
def create_workflow_snapshot(
    workflow_type: str,
    instance_id: UUID,
    state: LiteralWorkflowState,
    context: "ProtocolWorkflowContext"
) -> "ProtocolWorkflowSnapshot":
    """
    Example showing protocol-compliant snapshot creation.
    Workflow instance isolation: {workflowType, instanceId} pattern
    """
    # Note: This would be implemented by concrete implementations,
    # not defined in the SPI. This shows the expected structure.
    pass
```

**Key Features**:
- **Event Sourcing**: Full event streams with sequence numbers and causation tracking
- **FSM States**: Hierarchical workflow and task states (`pending` → `running` → `completed`)
- **Isolation Pattern**: `{workflowType, instanceId}` ensures workflow instance separation
- **Task Coordination**: Distributed task execution with dependency management
- **Compensation Actions**: Saga pattern support for failure recovery

### 2. MCP (Model Context Protocol) Integration

**Distributed Tool Coordination**

```python
# Import MCP protocols
from omnibase_spi.protocols.mcp import (
    ProtocolMCPRegistry,
    ProtocolMCPToolProxy,
    ProtocolMCPMonitor,
    ProtocolMCPSubsystemClient
)

# Import MCP types from the types module
from omnibase_spi.protocols.types import (
    ProtocolMCPToolDefinition,
    ProtocolMCPSubsystemRegistration,
    LiteralMCPToolType,
    LiteralMCPSubsystemType
)

# Import specific MCP types
from omnibase_spi.protocols.types.protocol_mcp_types import (
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPToolParameter
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Protocol usage example - MCP subsystem registration
async def register_mcp_subsystem(
    client: ProtocolMCPSubsystemClient,
    subsystem_metadata: "ProtocolMCPSubsystemMetadata",
    tools: list["ProtocolMCPToolDefinition"]
) -> str:
    """
    Example of protocol-compliant MCP subsystem registration.
    Returns registration_id for tracking and management.
    """
    registration_id = await client.register_subsystem(
        subsystem_metadata=subsystem_metadata,
        tools=tools,
        api_key="secure_key",
        configuration={}
    )
    return registration_id

# Protocol-based tool definition
def create_tool_definition(
    tool_name: str,
    tool_type: LiteralMCPToolType,
    parameters: list["ProtocolMCPToolParameter"]
) -> "ProtocolMCPToolDefinition":
    """
    Example showing protocol-compliant tool definition structure.
    """
    # Note: This would be implemented by concrete implementations
    # This shows the expected protocol structure.
    pass

# Protocol usage example - Tool execution through registry
async def execute_tool_via_registry(
    registry: ProtocolMCPRegistry,
    tool_name: str,
    parameters: dict[str, "ContextValue"],
    correlation_id: UUID
) -> dict[str, "ContextValue"]:
    """Example of protocol-compliant tool execution."""
    result = await registry.execute_tool(
        tool_name=tool_name,
        parameters=parameters,
        correlation_id=correlation_id
    )
    return result
```

**Key Features**:
- **Multi-Subsystem Coordination**: Register and discover tools across MCP subsystems
- **Dynamic Tool Discovery**: Runtime tool discovery with type-based filtering
- **Load Balancing**: Distribute execution across multiple tool implementations
- **Health Monitoring**: Subsystem health checks with TTL-based cleanup
- **Execution Tracking**: Correlation IDs and performance metrics

### 3. Event Bus and Messaging

**Distributed Event Patterns**

```python
# Import event bus protocols
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBus,
    ProtocolKafkaAdapter,
    ProtocolEventBusService
)

# Import event bus types
from omnibase_spi.protocols.types import (
    ProtocolEventMessage,
    ProtocolEventSubscription,
    ProtocolEventHeaders
)

# Import specific event bus types
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    ProtocolEvent,
    ProtocolEventData
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Protocol usage example - Event subscription
async def setup_event_handling(event_bus: ProtocolEventBus) -> str:
    """
    Example of protocol-compliant event bus subscription.
    Returns subscription ID for management.
    """
    async def handle_event(message: ProtocolEventMessage) -> None:
        """Protocol-compliant event handler."""
        # Access message properties defined by protocol
        topic: str = message.topic
        headers: dict[str, "ContextValue"] = message.headers
        # Process message according to protocol contract
        await message.ack()

    # Subscribe with consumer groups and filtering
    subscription_id = await event_bus.subscribe_to_topic(
        topic="workflow.events",
        group_id="orchestrator_group",
        handler=handle_event
    )
    return subscription_id

# Protocol usage example - Event publishing
async def publish_workflow_event(
    event_bus: ProtocolEventBus,
    event_data: "ProtocolEventData",
    topic: str = "workflow.events"
) -> None:
    """Example of protocol-compliant event publishing."""
    await event_bus.publish(
        topic=topic,
        data=event_data,
        headers={"source": "workflow_orchestrator"}
    )
```

### 4. Service Registry and Discovery

**Dynamic Service Coordination**

```python
# Import service registry and container protocols
from omnibase_spi.protocols.container import (
    ProtocolServiceRegistry,
    ProtocolArtifactContainer
)

# Import node registry from core
from omnibase_spi.protocols.core import (
    ProtocolNodeRegistry,
    ProtocolServiceDiscovery
)

# Import relevant types
from omnibase_spi.protocols.types import (
    ProtocolNodeMetadata,
    ProtocolServiceInstance,
    LiteralNodeType
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Protocol usage example - Node registration
async def register_workflow_node(
    registry: ProtocolNodeRegistry,
    node_metadata: "ProtocolNodeMetadata",
    capabilities: list[str],
    health_check_config: dict[str, "ContextValue"]
) -> str:
    """
    Example of protocol-compliant node registration.
    Returns node_id for tracking and management.
    """
    node_id = await registry.register_node(
        node_metadata=node_metadata,
        capabilities=capabilities,
        health_check_config=health_check_config
    )
    return node_id

# Protocol usage example - Service registration in DI container
async def register_service_in_container(
    service_registry: ProtocolServiceRegistry,
    service_name: str,
    service_factory: callable,
    lifecycle: str = "singleton"
) -> str:
    """Example of protocol-compliant service registration."""
    registration_id = await service_registry.register_service(
        service_name=service_name,
        service_factory=service_factory,
        lifecycle=lifecycle
    )
    return registration_id

# Protocol usage example - Service discovery
async def discover_services(
    discovery: ProtocolServiceDiscovery,
    service_type: str
) -> list["ProtocolServiceInstance"]:
    """Example of protocol-compliant service discovery."""
    services = await discovery.discover_services(
        service_type=service_type,
        criteria={"status": "active"}
    )
    return services
```

## Type System Architecture

### Core Type Definitions

**Strong Typing Throughout**

```python
# Import the actual types from the SPI
from omnibase_spi.protocols.types import (
    ContextValue,  # Union type for workflow data values
    LiteralWorkflowState,
    LiteralWorkflowEventType,
    LiteralTaskState,
    LiteralNodeType,
    LiteralHealthStatus
)

# Core context value type - actual workflow data constraint
# ContextValue = Union[str, int, float, bool, list[str], dict[str, Union[str, int, float, bool]]]

# Hierarchical FSM states (actual definition from protocol_workflow_orchestration_types.py)
# LiteralWorkflowState = Literal[
#     "pending", "initializing", "running", "paused",
#     "completed", "failed", "cancelled", "timeout",
#     "retrying", "waiting_for_dependency", "compensating", "compensated"
# ]

# Event sourcing event types (actual definition from protocol_workflow_orchestration_types.py)
# LiteralWorkflowEventType = Literal[
#     "workflow.created", "workflow.started", "workflow.paused", "workflow.resumed",
#     "workflow.completed", "workflow.failed", "workflow.cancelled", "workflow.timeout",
#     "task.scheduled", "task.started", "task.completed", "task.failed", "task.retry",
#     "dependency.resolved", "dependency.failed", "state.transitioned",
#     "compensation.started", "compensation.completed"
# ]

# Task states for workflow coordination
# LiteralTaskState = Literal[
#     "pending", "scheduled", "running", "completed", "failed",
#     "cancelled", "timeout", "retrying", "skipped", "waiting_for_input", "blocked"
# ]

# Node types in ONEX architecture
# LiteralNodeType = Literal["compute", "effect", "orchestrator", "reducer"]

# Example protocol usage with proper types
def process_workflow_state(state: LiteralWorkflowState) -> bool:
    """Example showing proper literal type usage."""
    if state in ("completed", "failed", "cancelled"):
        return True  # Terminal states
    return False  # Active states

def handle_event_type(event_type: LiteralWorkflowEventType) -> str:
    """Example showing event type processing."""
    if event_type.startswith("workflow."):
        return "workflow_event"
    elif event_type.startswith("task."):
        return "task_event"
    else:
        return "system_event"
```

### Protocol Definition Pattern

**Consistent Contract Structure**

```python
# Import protocols to show the actual pattern used in the SPI
from omnibase_spi.protocols.core import ProtocolLogger
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus
from omnibase_spi.protocols.types import ProtocolWorkflowEvent

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Example showing how to use existing protocols (not define new ones)
def use_logger_protocol(logger: ProtocolLogger, message: str) -> None:
    """Example of using an existing protocol contract."""
    # Protocol guarantees these methods exist
    logger.info(message)
    logger.debug(f"Debug: {message}")

# Example showing protocol composition
async def workflow_event_processor(
    event_bus: ProtocolWorkflowEventBus,
    event: ProtocolWorkflowEvent
) -> None:
    """Example of using protocol composition."""
    # Protocol contracts ensure these methods and properties exist
    await event_bus.publish_workflow_event(event)

    # Access protocol-defined properties
    event_type = event.event_type
    workflow_type = event.workflow_type
    instance_id = event.instance_id

# Protocol usage example - Runtime checking
def validate_protocol_implementation(obj: object) -> bool:
    """Example showing runtime protocol validation."""
    # Check if object implements protocol
    if isinstance(obj, ProtocolLogger):
        return True
    return False

# Example protocol interface pattern (for reference - from actual SPI code)
"""
Typical SPI protocol structure:

@runtime_checkable
class ProtocolExample(Protocol):
    \"\"\"
    Protocol description with clear contract definition.

    Key Features:
        - Contract-based interface definition
        - Runtime checkable for isinstance() support
        - Strong typing throughout
        - Forward references for circular dependencies
    \"\"\"

    # Properties defined with type annotations
    property_name: str

    async def method_name(
        self,
        param: str,
        optional_param: int | None = None
    ) -> "ForwardReference":
        \"\"\"
        Method contract with clear expectations.

        Args:
            param: Required parameter description
            optional_param: Optional parameter description

        Returns:
            Return value description

        Raises:
            ValueError: When parameter validation fails
        \"\"\"
        ...
"""
```

## SPI Purity and Validation

### Namespace Isolation Rules

**Critical: Complete Namespace Isolation**

```python
# ✅ ALLOWED - SPI-only imports
from omnibase_spi.protocols.types.workflow_orchestration_types import WorkflowState
from omnibase_spi.protocols.core.protocol_workflow_reducer import ProtocolWorkflowReducer

# ✅ ALLOWED - Forward references with TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import NodeMetadata

def process_node(self, node: "NodeMetadata") -> str: ...

# ❌ FORBIDDEN - Implementation imports
from omnibase_spi.model.workflow import WorkflowInstance  # Breaks SPI purity
from omnibase_spi.core.services import ServiceManager     # Creates dependency
```

### Validation Tools

#### Comprehensive SPI Protocol Validation Framework

The repository includes a comprehensive validation framework with 16 configurable rules:

```bash
# Run comprehensive validation with default configuration
python scripts/validation/comprehensive_spi_validator.py src/

# Run with custom configuration file
python scripts/validation/comprehensive_spi_validator.py src/ --config validation_config.yaml

# Apply automatic fixes for supported violations
python scripts/validation/comprehensive_spi_validator.py src/ --fix

# Generate JSON report for CI/CD integration
python scripts/validation/comprehensive_spi_validator.py src/ --json-report

# Pre-commit integration mode (faster)
python scripts/validation/comprehensive_spi_validator.py --pre-commit
```

**Validation Rules** (16 comprehensive rules):
- **SPI001**: No Protocol `__init__` methods
- **SPI002**: Protocol naming conventions
- **SPI003**: `@runtime_checkable` decorator enforcement
- **SPI004**: Protocol method bodies (ellipsis only)
- **SPI005**: Async I/O operations
- **SPI006**: Proper Callable types
- **SPI007**: No concrete classes in SPI
- **SPI008**: No standalone functions
- **SPI009**: ContextValue usage patterns
- **SPI010**: Duplicate protocol detection
- **SPI011**: Protocol name conflicts
- **SPI012**: Namespace isolation
- **SPI013**: Forward reference typing
- **SPI014**: Protocol documentation
- **SPI015**: Method type annotations
- **SPI016**: SPI implementation purity

**Configuration File** (`validation_config.yaml`):
```yaml
# Environment-specific overrides
environments:
  pre_commit:
    global_settings:
      timeout_seconds: 60
      max_violations_per_file: 20
    disable_rules:
      - "SPI014" # Documentation checks (slow)

  ci_cd:
    global_settings:
      timeout_seconds: 180
      enable_caching: false
    rule_overrides:
      "SPI008":
        severity: "error"

  production:
    rule_overrides:
      "SPI002":
        severity: "error"
      "SPI014":
        severity: "error"
```

#### Legacy Validation Tools

```bash
# Namespace isolation validation
./scripts/validate-namespace-isolation.sh

# Protocol compliance checking  
poetry run python scripts/ast_spi_validator.py

# Type checking with strict settings
poetry run mypy src/ --strict

# Run all validation
poetry run pytest && poetry build
```

## Development Workflow

### Setting Up Development Environment

```bash
# Clone and setup
git clone <repository>
cd omnibase-spi

# Install with Poetry
poetry install

# Setup pre-commit hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push -c .pre-commit-config-push.yaml

# Validate setup
poetry run pytest tests/test_protocol_imports.py -v
```

### Creating New Protocols

**1. Define Protocol Interface**

```python
# src/omnibase_spi/protocols/domain/protocol_new_service.py
from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.domain_types import DomainType

@runtime_checkable  
class ProtocolNewService(Protocol):
    """Protocol for new service functionality."""

    async def service_method(self, param: str) -> "DomainType":
        """Service method description."""
        ...
```

**2. Add Type Definitions**

```python
# src/omnibase_spi/protocols/types/domain_types.py
from typing import Protocol, Literal

ServiceStatus = Literal["active", "inactive", "pending"]

class ProtocolDomainType(Protocol):
    status: ServiceStatus
    name: str
```

**3. Update Package Imports**

```python
# src/omnibase_spi/protocols/domain/__init__.py
"""Domain protocol interfaces."""

from .protocol_new_service import ProtocolNewService

__all__ = ["ProtocolNewService"]
```

### Testing Protocol Contracts

```python
# tests/test_new_protocol.py
import pytest
from omnibase_spi.protocols.domain import ProtocolNewService

class MockServiceImplementation:
    """Test implementation of protocol."""

    async def service_method(self, param: str) -> dict:
        return {"status": "active", "name": param}

def test_protocol_compliance():
    """Test that mock implementation satisfies protocol."""
    mock = MockServiceImplementation()
    assert isinstance(mock, ProtocolNewService)
```

## Integration Patterns

### Using SPI in Implementation Packages

```python
# In omnibase-core or other implementation packages - Protocol Usage Only
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus
from omnibase_spi.protocols.types import ProtocolWorkflowEvent

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Example: Protocol-based service interface (not implementation)
def create_event_bus_service(config: dict[str, "ContextValue"]) -> ProtocolWorkflowEventBus:
    """
    Factory function returning protocol-compliant event bus.

    Note: Actual implementation would be in omnibase-core,
    this SPI only defines the contract.
    """
    # Implementation packages would provide concrete implementations
    # that satisfy the ProtocolWorkflowEventBus contract
    pass

# Example: Protocol validation in implementation packages
def validate_event_bus_implementation(
    implementation: object
) -> ProtocolWorkflowEventBus:
    """
    Validate that an object implements the required protocol.

    Implementation packages use this for runtime validation.
    """
    if not isinstance(implementation, ProtocolWorkflowEventBus):
        raise TypeError("Object does not implement ProtocolWorkflowEventBus")

    return implementation  # Type narrowing for static analysis
```

### Dependency Injection Integration

```python
# Protocol-based dependency injection pattern
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

from typing import TYPE_CHECKING, TypeVar
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

T = TypeVar('T')

# Protocol-based service resolution interface
async def resolve_service(
    registry: ProtocolServiceRegistry,
    protocol_type: type[T]
) -> T:
    """
    Example of protocol-based service resolution.

    Implementation packages provide the registry implementation,
    SPI defines the contract.
    """
    service = await registry.resolve_service(protocol_type)
    return service

# Example usage in implementation packages
async def setup_workflow_services(registry: ProtocolServiceRegistry) -> None:
    """Example showing protocol-based service composition."""
    # Resolve services by protocol contracts
    event_bus = await resolve_service(registry, ProtocolWorkflowEventBus)
    mcp_registry = await resolve_service(registry, ProtocolMCPRegistry)

    # Use protocol contracts for service coordination
    # (Implementation details handled by concrete implementations)
```

## Advanced Features

### Event Sourcing Patterns

**Complete Event Streams with Causation**

```python
# Import required protocols and types
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolWorkflowEventBus,
    ProtocolEventStore
)
from omnibase_spi.protocols.types import (
    ProtocolWorkflowEvent,
    LiteralWorkflowEventType
)

from uuid import UUID
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Protocol-based event processing
async def process_workflow_event(
    event: ProtocolWorkflowEvent,
    event_bus: ProtocolWorkflowEventBus
) -> None:
    """
    Example showing protocol-compliant event sourcing usage.

    Event sourcing with full causation tracking requires:
    - event_id: Unique identifier
    - event_type: Type from LiteralWorkflowEventType
    - workflow_type: Workflow type identifier
    - instance_id: Workflow instance identifier
    - sequence_number: Event ordering
    - causation_id: Event that caused this event
    - correlation_chain: Full causation chain
    """
    # Access protocol-guaranteed properties
    event_id: UUID = event.event_id
    event_type: LiteralWorkflowEventType = event.event_type
    workflow_type: str = event.workflow_type
    instance_id: UUID = event.instance_id
    sequence_number: int = event.sequence_number

    # Optional causation tracking
    causation_id: UUID | None = event.causation_id
    correlation_chain: list[UUID] = event.correlation_chain

    # Publish event using protocol contract
    await event_bus.publish_workflow_event(event)

# Protocol-based event replay
async def replay_workflow_events(
    event_bus: ProtocolWorkflowEventBus,
    workflow_type: str,
    instance_id: UUID,
    from_sequence: int = 1,
    to_sequence: int | None = None
) -> list[ProtocolWorkflowEvent]:
    """
    Example showing protocol-compliant event replay.

    Uses protocol contracts for event sourcing replay.
    """
    events = await event_bus.replay_workflow_events(
        workflow_type=workflow_type,
        instance_id=instance_id,
        from_sequence=from_sequence,
        to_sequence=to_sequence
    )
    return events
```

### Workflow Instance Isolation

**`{workflowType, instanceId}` Pattern**

```python
# Import required protocols and types for workflow isolation
from omnibase_spi.protocols.types import (
    ProtocolWorkflowContext,
    LiteralIsolationLevel
)

from uuid import UUID
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import (
        ContextValue,
        ProtocolWorkflowValue
    )

# Protocol-based workflow isolation pattern
def process_isolated_workflow_context(
    context: ProtocolWorkflowContext
) -> dict[str, "ContextValue"]:
    """
    Example showing protocol-compliant workflow isolation usage.

    The {workflowType, instanceId} pattern ensures workflow instances don't interfere.
    Protocol guarantees these properties exist:
    """
    # Core isolation identifiers
    workflow_type: str = context.workflow_type  # Workflow type namespace
    instance_id: UUID = context.instance_id     # Unique instance within type
    correlation_id: UUID = context.correlation_id  # Request correlation

    # Isolation configuration
    isolation_level: LiteralIsolationLevel = context.isolation_level

    # Workflow data (protocol-typed)
    workflow_data: dict[str, "ProtocolWorkflowValue"] = context.data
    secrets: dict[str, "ContextValue"] = context.secrets
    capabilities: list[str] = context.capabilities
    resource_limits: dict[str, int] = context.resource_limits

    return {
        "workflow_type": workflow_type,
        "instance_id": str(instance_id),
        "isolation_level": isolation_level,
        "capability_count": len(capabilities)
    }

# Protocol validation for workflow context
async def validate_workflow_isolation(context: ProtocolWorkflowContext) -> bool:
    """
    Example showing protocol-based validation of workflow isolation.

    Protocol contracts ensure validation methods exist.
    """
    # Use protocol-guaranteed validation methods
    is_valid = await context.validate_context()
    has_required = context.has_required_data()

    return is_valid and has_required
```

### MCP Multi-Subsystem Coordination

**Distributed Tool Registry**

```python
# Import required MCP protocols and types
from omnibase_spi.protocols.mcp import (
    ProtocolMCPRegistry,
    ProtocolMCPSubsystemClient
)
from omnibase_spi.protocols.types import (
    ProtocolMCPToolDefinition,
    ProtocolMCPSubsystemRegistration,
    LiteralMCPToolType
)

from uuid import UUID, uuid4
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue

# Protocol-based multi-subsystem tool coordination
async def coordinate_multi_subsystem_tools(
    registry: ProtocolMCPRegistry,
    tool_name: str,
    parameters: dict[str, "ContextValue"],
    preferred_subsystem: str | None = None
) -> dict[str, "ContextValue"]:
    """
    Example showing protocol-compliant multi-subsystem tool execution.

    Registry handles load balancing and failover according to protocol contract.
    """
    # Execute tool through registry protocol
    result = await registry.execute_tool(
        tool_name=tool_name,
        parameters=parameters,
        correlation_id=uuid4(),
        preferred_subsystem=preferred_subsystem
    )
    return result

# Protocol-based tool discovery across subsystems
async def discover_overlapping_tools(
    registry: ProtocolMCPRegistry,
    tool_type: LiteralMCPToolType
) -> list[ProtocolMCPToolDefinition]:
    """
    Example showing protocol-compliant tool discovery.

    Finds tools of a specific type across all registered subsystems.
    """
    # Use registry protocol to discover tools
    available_tools = await registry.discover_tools(
        tool_type=tool_type,
        include_all_subsystems=True
    )
    return available_tools

# Protocol-based subsystem health monitoring
async def monitor_subsystem_health(
    registry: ProtocolMCPRegistry
) -> dict[str, "ContextValue"]:
    """
    Example showing protocol-compliant subsystem monitoring.

    Registry protocol provides health status for all subsystems.
    """
    health_status = await registry.get_subsystem_health()

    # Access protocol-guaranteed properties
    active_subsystems = health_status.get("active_count", 0)
    failed_subsystems = health_status.get("failed_count", 0)

    return {
        "active": active_subsystems,
        "failed": failed_subsystems,
        "total": active_subsystems + failed_subsystems
    }
```

## Quality Assurance

### Type Safety Validation

```bash
# Strict mypy checking
poetry run mypy src/ --strict --no-any-expr

# Protocol validation  
poetry run python scripts/ast_spi_validator.py --check-protocols

# Namespace isolation testing
poetry run pytest tests/test_protocol_imports.py -v
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: namespace-validation
        name: Validate SPI namespace isolation
        entry: ./scripts/validate-namespace-isolation.sh
        language: system
        pass_filenames: false
```

## Best Practices

### Protocol Design Guidelines

1. **Single Responsibility**: Each protocol should have one clear purpose
2. **Async by Default**: Use `async def` for all I/O operations
3. **Strong Typing**: No `Any` types in public interfaces
4. **Forward References**: Use `TYPE_CHECKING` imports for model types
5. **Clear Documentation**: Comprehensive docstrings with examples
6. **Runtime Checkable**: Use `@runtime_checkable` for isinstance checks

### Error Handling Patterns

```python
@runtime_checkable
class ProtocolServiceExample(Protocol):
    """Example service protocol with proper error handling."""

    async def process_request(self, request: str) -> str:
        """
        Process service request.

        Args:
            request: Request data to process

        Returns:
            Processed response

        Raises:
            ValueError: If request format is invalid
            TimeoutError: If processing exceeds timeout
            RuntimeError: If service is unavailable
        """
        ...
```

### Testing Strategy

1. **Protocol Compliance Tests**: Verify implementations satisfy protocols
2. **Type Checking Tests**: Ensure type safety across boundaries  
3. **Import Isolation Tests**: Validate namespace separation
4. **Documentation Tests**: Verify protocol contracts are clear

## Dependencies

**Zero Runtime Dependencies by Design**

```toml
# pyproject.toml - runtime dependencies
dependencies = [
    "typing-extensions>=4.5.0",  # Modern typing features
    "pydantic>=2.11.7",          # Type validation only
]

# Development dependencies for quality assurance
[tool.poetry.group.dev.dependencies]
mypy = "^1.13.0"      # Type checking
black = "^24.10.0"    # Code formatting  
isort = "^5.13.0"     # Import sorting
pytest = "^8.4.1"     # Testing framework
ruff = "^0.8.0"       # Fast linting
```

## Conclusion

The **omnibase-spi** repository provides a robust, type-safe foundation for distributed workflow orchestration and service coordination. Its strict architectural purity, comprehensive event sourcing patterns, and advanced MCP integration make it an ideal contract layer for complex distributed systems.

**Key Strengths**:
- **Architectural Purity**: Zero implementation dependencies ensure clean boundaries
- **Event Sourcing**: Complete event streams with causation tracking and replay
- **Workflow Isolation**: Robust `{workflowType, instanceId}` isolation patterns  
- **MCP Integration**: Advanced multi-subsystem tool coordination
- **Type Safety**: Strong typing throughout with runtime protocol checking
- **Extensibility**: Clean extension points for new domains and capabilities

This SPI serves as the foundational contract layer enabling the entire ONEX ecosystem's distributed orchestration capabilities while maintaining strict architectural discipline and type safety.
