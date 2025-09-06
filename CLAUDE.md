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
2. **Namespace Isolation**: Complete separation from implementation packages (`omnibase.protocols.*` only)
3. **Event Sourcing Patterns**: Sequence numbers, causation tracking, and replay capabilities
4. **Workflow Isolation**: `{workflowType, instanceId}` isolation with correlation chains
5. **Type Safety**: Strong typing with no `Any` usage in public interfaces

### Domain Organization

```
src/omnibase/protocols/
├── core/                         # System-level contracts
│   ├── protocol_onex_envelope.py    # Message envelope patterns
│   ├── protocol_onex_reply.py       # Request-response contracts
│   ├── protocol_workflow_reducer.py # FSM state reduction
│   └── protocol_node_registry.py    # Node discovery and management
├── workflow_orchestration/      # Event-driven FSM orchestration
│   ├── protocol_workflow_event_bus.py      # Event sourcing patterns
│   ├── protocol_workflow_node_registry.py  # Workflow node coordination
│   └── protocol_workflow_persistence.py    # State persistence contracts
├── mcp/                         # Model Context Protocol integration
│   ├── protocol_mcp_registry.py        # Tool registration and discovery
│   ├── protocol_mcp_tool_proxy.py      # Tool execution proxying
│   ├── protocol_mcp_monitor.py         # Health and metrics monitoring
│   └── protocol_mcp_validator.py       # Request validation
├── event_bus/                   # Event messaging infrastructure
│   ├── protocol_event_bus.py          # Core event bus operations
│   └── protocol_kafka_adapter.py      # Kafka integration contract
├── container/                   # Dependency injection and service location
│   ├── protocol_service_registry.py   # Service discovery contracts
│   └── protocol_artifact_container.py # Artifact management
└── types/                       # Shared type definitions
    ├── workflow_orchestration_types.py # FSM states, events, tasks
    ├── mcp_types.py                   # MCP tool and subsystem types
    ├── core_types.py                  # Base system types
    └── event_bus_types.py             # Event messaging types
```

## Key Protocol Domains

### 1. Workflow Orchestration Protocols

**Event-Driven FSM with Event Sourcing**

```python
from omnibase.protocols.workflow_orchestration import (
    ProtocolWorkflowEventBus,
    ProtocolWorkflowNodeRegistry, 
    ProtocolWorkflowPersistence
)
from omnibase.protocols.types.workflow_orchestration_types import (
    ProtocolWorkflowEvent,
    ProtocolWorkflowSnapshot,
    WorkflowState,
    TaskState,
    WorkflowEventType
)

# Event sourcing with sequence numbers
class MyWorkflowHandler:
    async def handle_event(self, event: ProtocolWorkflowEvent) -> None:
        # Event contains: sequence_number, causation_id, correlation_chain
        # Enables full event sourcing with causation tracking
        pass

# Workflow instance isolation: {workflowType, instanceId}  
workflow_instance = ProtocolWorkflowSnapshot(
    workflow_type="data_processing_pipeline",
    instance_id=UUID("..."),
    sequence_number=42,
    state="running",
    # ... context and task configurations
)
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
from omnibase.protocols.mcp import (
    ProtocolMCPRegistry,
    ProtocolMCPToolProxy,
    ProtocolMCPMonitor
)
from omnibase.protocols.types.mcp_types import (
    ProtocolMCPToolDefinition,
    ProtocolMCPSubsystemRegistration,
    MCPToolType,
    MCPSubsystemType
)

# Register subsystem with tools
async def register_mcp_subsystem(registry: ProtocolMCPRegistry):
    tools = [
        ProtocolMCPToolDefinition(
            name="semantic_search",
            tool_type="query",
            parameters_schema={...},
            # Tool metadata
        )
    ]
    
    registration_id = await registry.register_subsystem(
        subsystem_metadata=subsystem_info,
        tools=tools,
        api_key="secure_key",
        configuration=optional_config
    )
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
from omnibase.protocols.event_bus import (
    ProtocolEventBus,
    ProtocolKafkaAdapter
)
from omnibase.protocols.types.event_bus_types import (
    EventMessage,
    EventMetadata
)

# Event bus with workflow extensions
async def setup_event_handling(event_bus: ProtocolEventBus):
    # Subscribe with consumer groups and filtering
    unsubscribe = await event_bus.subscribe_to_topic(
        topic="workflow.events",
        group_id="orchestrator_group",
        handler=handle_workflow_event
    )
```

### 4. Service Registry and Discovery

**Dynamic Service Coordination**

```python
from omnibase.protocols.container import (
    ProtocolServiceRegistry,
    ProtocolArtifactContainer
)
from omnibase.protocols.core import ProtocolNodeRegistry

# Service registration with capabilities
async def register_workflow_node(registry: ProtocolNodeRegistry):
    await registry.register_node(
        node_metadata=node_info,
        capabilities=["workflow_execution", "event_processing"],
        health_check_config=health_config
    )
```

## Type System Architecture

### Core Type Definitions

**Strong Typing Throughout**

```python
# Workflow data types with union constraints
WorkflowData = Union[
    str, int, float, bool, 
    list[str], 
    dict[str, Union[str, int, float, bool]]
]

# Hierarchical FSM states
WorkflowState = Literal[
    "pending", "initializing", "running", "paused",
    "completed", "failed", "cancelled", "timeout",
    "retrying", "waiting_for_dependency", "compensating", "compensated"
]

# Event sourcing event types
WorkflowEventType = Literal[
    "workflow.created", "workflow.started", "workflow.completed",
    "task.scheduled", "task.completed", "task.failed",
    "dependency.resolved", "state.transitioned", "compensation.started"
]
```

### Protocol Definition Pattern

**Consistent Contract Structure**

```python
from typing import Protocol, runtime_checkable
from uuid import UUID

@runtime_checkable
class ProtocolWorkflowExample(Protocol):
    """
    Protocol description with clear contract definition.
    
    Key Features:
        - Feature 1 description
        - Feature 2 description
    """
    
    # Properties with clear types
    property_name: str
    
    async def method_name(
        self, 
        param: str, 
        optional_param: Optional[int] = None
    ) -> "ForwardReference":
        """
        Method documentation with clear expectations.
        
        Args:
            param: Parameter description
            optional_param: Optional parameter description
            
        Returns:
            Return value description
            
        Raises:
            ValueError: When parameter validation fails
        """
        ...
```

## SPI Purity and Validation

### Namespace Isolation Rules

**Critical: Complete Namespace Isolation**

```python
# ✅ ALLOWED - SPI-only imports
from omnibase.protocols.types.workflow_orchestration_types import WorkflowState
from omnibase.protocols.core.protocol_workflow_reducer import ProtocolWorkflowReducer

# ✅ ALLOWED - Forward references with TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase.protocols.types.core_types import NodeMetadata
    
def process_node(self, node: "NodeMetadata") -> str: ...

# ❌ FORBIDDEN - Implementation imports
from omnibase.model.workflow import WorkflowInstance  # Breaks SPI purity
from omnibase.core.services import ServiceManager     # Creates dependency
```

### Validation Tools

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
# src/omnibase/protocols/domain/protocol_new_service.py
from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase.protocols.types.domain_types import DomainType

@runtime_checkable  
class ProtocolNewService(Protocol):
    """Protocol for new service functionality."""
    
    async def service_method(self, param: str) -> "DomainType":
        """Service method description."""
        ...
```

**2. Add Type Definitions**

```python
# src/omnibase/protocols/types/domain_types.py
from typing import Protocol, Literal

ServiceStatus = Literal["active", "inactive", "pending"]

class ProtocolDomainType(Protocol):
    status: ServiceStatus
    name: str
```

**3. Update Package Imports**

```python
# src/omnibase/protocols/domain/__init__.py
"""Domain protocol interfaces."""

from .protocol_new_service import ProtocolNewService

__all__ = ["ProtocolNewService"]
```

### Testing Protocol Contracts

```python
# tests/test_new_protocol.py
import pytest
from omnibase.protocols.domain import ProtocolNewService

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

### Using in Implementation Packages

```python
# In omnibase-core or other implementation packages
from omnibase.protocols.workflow_orchestration import ProtocolWorkflowEventBus
from omnibase.protocols.types.workflow_orchestration_types import ProtocolWorkflowEvent

class WorkflowEventBusImplementation(ProtocolWorkflowEventBus):
    """Concrete implementation of workflow event bus protocol."""
    
    async def publish_workflow_event(
        self, 
        event: ProtocolWorkflowEvent, 
        target_topic: Optional[str] = None
    ) -> None:
        # Actual implementation using Kafka, Redis, etc.
        pass
```

### Dependency Injection Pattern

```python
# Service registry with protocol contracts
class ServiceContainer:
    def __init__(self):
        self._services: dict[type, Any] = {}
    
    def register(self, protocol: type, implementation: Any) -> None:
        if not isinstance(implementation, protocol):
            raise ValueError(f"Implementation must satisfy {protocol}")
        self._services[protocol] = implementation
    
    def get(self, protocol: type) -> Any:
        return self._services[protocol]

# Usage
container = ServiceContainer()
container.register(ProtocolWorkflowEventBus, EventBusImplementation())
event_bus = container.get(ProtocolWorkflowEventBus)
```

## Advanced Features

### Event Sourcing Patterns

**Complete Event Streams with Causation**

```python
# Event sourcing with full causation tracking
event = ProtocolWorkflowEvent(
    event_id=UUID(...),
    event_type="task.completed",
    workflow_type="data_pipeline", 
    instance_id=UUID(...),
    sequence_number=42,
    causation_id=UUID(...),  # Event that caused this event
    correlation_chain=[UUID(...), UUID(...)]  # Full chain
)

# Replay events for recovery
events = await workflow_event_bus.replay_events(
    workflow_type="data_pipeline",
    instance_id=instance_id,
    from_sequence=1,
    to_sequence=42
)
```

### Workflow Instance Isolation

**`{workflowType, instanceId}` Pattern**

```python
# Isolation ensures workflow instances don't interfere
workflow_context = ProtocolWorkflowContext(
    workflow_type="user_onboarding",  # Workflow type namespace
    instance_id=UUID(...),            # Unique instance within type
    correlation_id=UUID(...),         # Request correlation
    isolation_level="read_committed", # Transaction isolation
    data={"user_id": "12345"},        # Workflow-specific data
    secrets={"api_key": "encrypted"}, # Protected values
    capabilities=["email", "sms"],    # Available capabilities
    resource_limits={"memory": 512}   # Resource constraints
)
```

### MCP Multi-Subsystem Coordination

**Distributed Tool Registry**

```python
# Register multiple subsystems with overlapping tools
subsystem_a_tools = [
    ProtocolMCPToolDefinition(name="search", tool_type="query"),
    ProtocolMCPToolDefinition(name="analyze", tool_type="compute")
]

subsystem_b_tools = [
    ProtocolMCPToolDefinition(name="search", tool_type="query"),  # Same tool, different impl
    ProtocolMCPToolDefinition(name="transform", tool_type="compute")
]

# Registry handles load balancing and failover
result = await mcp_registry.execute_tool(
    tool_name="search", 
    parameters={"query": "find documents"},
    correlation_id=UUID(...),
    preferred_subsystem="subsystem_a"  # Optional preference
)
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