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
2. **Container Protocols** - [Dependency injection patterns](api-reference/CONTAINER.md)
3. **Workflow Orchestration** - [Event-driven FSM](api-reference/WORKFLOW-ORCHESTRATION.md)
4. **MCP Integration** - [Multi-subsystem coordination](api-reference/MCP.md)

## See Also

- **[Glossary](GLOSSARY.md)** - Definitions of SPI-specific terms (Protocol, Handler, Node, etc.)
- **[Developer Guide](developer-guide/README.md)** - Complete development workflow
- **[Architecture Overview](architecture/README.md)** - Design principles and patterns
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Main README](../README.md)** - Repository overview

### v0.3.0 Core Protocols

- **[Node Protocols](api-reference/NODES.md)** - ONEX 4-node architecture (Compute, Effect, Reducer, Orchestrator)
- **[Handler Protocols](api-reference/HANDLERS.md)** - I/O handler interfaces
- **[Contract Compilers](api-reference/CONTRACTS.md)** - Effect, Workflow, FSM compilers
- **[Registry Protocols](api-reference/REGISTRY.md)** - Handler registry for DI
- **[Exception Hierarchy](api-reference/EXCEPTIONS.md)** - SPIError and subclasses

For term definitions, see the [Glossary](GLOSSARY.md).

---

*For comprehensive documentation, see the [API Reference](api-reference/README.md).*
