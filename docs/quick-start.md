# Quick Start Guide

## Overview

Get up and running with ONEX SPI protocols in minutes. This guide provides immediate hands-on experience with the core protocols.

## Installation

```bash
# Install the package
pip install omnibase-spi

# Or with poetry
poetry add omnibase-spi
```

## Basic Usage

### Service Registration and Resolution

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.core import ProtocolLogger

# Register a service
registry: ProtocolServiceRegistry = get_service_registry()
await registry.register_service(
    interface=ProtocolLogger,
    implementation=ConsoleLogger,
    lifecycle="singleton",
    scope="global"
)

# Resolve the service
logger = await registry.resolve_service(ProtocolLogger)
await logger.log("INFO", "Hello, ONEX SPI!")
```

### Workflow Orchestration

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowOrchestrator

# Start a workflow
orchestrator: ProtocolWorkflowOrchestrator = get_workflow_orchestrator()
workflow = await orchestrator.start_workflow(
    workflow_type="order-processing",
    instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    initial_data={"order_id": "ORD-12345"}
)

print(f"Workflow state: {workflow.current_state}")
```

### MCP Tool Execution

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

# Execute a tool
mcp_registry: ProtocolMCPRegistry = get_mcp_registry()
result = await mcp_registry.execute_tool(
    tool_name="text_generation",
    parameters={"prompt": "Hello world"},
    correlation_id=UUID("req-abc123")
)

print(f"Tool result: {result}")
```

## Next Steps

1. **Explore the API Reference** - [Complete protocol documentation](api-reference/README.md)
2. **Container Protocols** - [Dependency injection patterns](api-reference/container.md)
3. **Workflow Orchestration** - [Event-driven FSM](api-reference/workflow-orchestration.md)
4. **MCP Integration** - [Multi-subsystem coordination](api-reference/mcp.md)

---

*For comprehensive documentation, see the [API Reference](api-reference/README.md).*
