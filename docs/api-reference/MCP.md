# MCP Integration API Reference

![Version](https://img.shields.io/badge/SPI-v0.3.0-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.3.0-lightgrey)

> **SPI Version**: 0.3.0 | **Status**: Stable | **Since**: v0.3.0

---

## Overview

The ONEX MCP (Model Context Protocol) integration protocols provide comprehensive multi-subsystem tool coordination, dynamic tool discovery, load balancing, and health monitoring across distributed MCP-enabled subsystems. These protocols enable sophisticated tool management and execution coordination in the ONEX ecosystem.

## 🏗️ Protocol Architecture

The MCP integration domain consists of **15 specialized protocols** that provide complete MCP coordination:

### MCP Registry Protocol

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry
from omnibase_spi.protocols.types.protocol_mcp_types import (
    LiteralMCPSubsystemType,
    LiteralMCPToolType,
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
)

@runtime_checkable
class ProtocolMCPRegistry(Protocol):
    """
    Core MCP registry protocol for distributed tool coordination.

    Manages subsystem registration, tool discovery, and execution routing
    across multiple MCP-enabled subsystems in the ONEX ecosystem.

    Key Features:
        - Multi-Subsystem Coordination: Register and coordinate multiple MCP subsystems
        - Dynamic Tool Discovery: Discover and route tools across registered subsystems
        - Load Balancing: Distribute tool execution across multiple implementations
        - Health Monitoring: Monitor subsystem health and handle failures gracefully
        - Execution Tracking: Track tool execution metrics and performance
        - Security: API key authentication and request validation
        - TTL Management: Automatic cleanup of expired registrations
    """

    @property
    def config(self) -> ProtocolMCPRegistryConfig: ...

    async def register_subsystem(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
        api_key: str,
        configuration: dict[str, ContextValue] | None = None,
    ) -> str: ...

    async def unregister_subsystem(self, registration_id: str) -> bool: ...

    async def update_subsystem_heartbeat(
        self,
        registration_id: str,
        health_status: str | None = None,
        metadata: dict[str, ContextValue] | None = None,
    ) -> bool: ...

    async def get_subsystem_registration(
        self, registration_id: str
    ) -> ProtocolMCPSubsystemRegistration | None: ...

    async def get_all_subsystems(
        self,
        subsystem_type: LiteralMCPSubsystemType | None,
        status_filter: LiteralOperationStatus | None,
    ) -> list[ProtocolMCPSubsystemRegistration]: ...

    async def discover_tools(
        self,
        tool_type: LiteralMCPToolType | None,
        tags: list[str] | None,
        subsystem_id: str | None,
    ) -> list[ProtocolMCPToolDefinition]: ...

    async def get_tool_definition(
        self, tool_name: str
    ) -> ProtocolMCPToolDefinition | None: ...

    async def get_all_tool_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]: ...

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        correlation_id: UUID,
        timeout_seconds: int | None,
        preferred_subsystem: str | None,
    ) -> dict[str, ContextValue]: ...

    async def get_tool_execution(
        self, execution_id: str
    ) -> ProtocolMCPToolExecution | None: ...

    async def get_tool_executions(
        self,
        tool_name: str | None,
        subsystem_id: str | None,
        correlation_id: UUID | None,
        limit: int,
    ) -> list[ProtocolMCPToolExecution]: ...

    async def cancel_tool_execution(self, execution_id: str) -> bool: ...

    async def validate_subsystem_registration(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
    ) -> ProtocolMCPValidationResult: ...

    async def validate_tool_parameters(
        self, tool_name: str, parameters: dict[str, ContextValue]
    ) -> ProtocolValidationResult: ...

    async def perform_health_check(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck: ...

    async def get_subsystem_health(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck | None: ...

    async def cleanup_expired_registrations(self) -> int: ...

    async def update_subsystem_configuration(
        self, registration_id: str, configuration: dict[str, ContextValue]
    ) -> bool: ...

    async def get_registry_status(self) -> ProtocolMCPRegistryStatus: ...

    async def get_registry_metrics(self) -> ProtocolMCPRegistryMetrics: ...
```

### MCP Registry Admin Protocol

```python
@runtime_checkable
class ProtocolMCPRegistryAdmin(Protocol):
    """
    Administrative protocol for MCP registry management.

    Provides privileged operations for registry administration,
    configuration management, and system maintenance.
    """

    async def set_maintenance_mode(self, enabled: bool) -> bool: ...

    async def force_subsystem_cleanup(self, registration_id: str) -> bool: ...

    async def update_registry_configuration(
        self, configuration: dict[str, ContextValue]
    ) -> bool: ...

    async def export_registry_state(self) -> dict[str, ContextValue]: ...

    async def import_registry_state(
        self, state_data: dict[str, ContextValue]
    ) -> bool: ...

    async def get_system_diagnostics(self) -> dict[str, ContextValue]: ...
```

### MCP Registry Metrics Operations Protocol

```python
@runtime_checkable
class ProtocolMCPRegistryMetricsOperations(Protocol):
    """
    Protocol for advanced MCP registry metrics and analytics.

    Provides detailed performance metrics, trend analysis,
    and operational insights for the registry system.
    """

    async def get_execution_metrics(
        self, time_range_hours: int, tool_name: str | None, subsystem_id: str | None
    ) -> dict[str, ContextValue]: ...

    async def get_performance_trends(
        self, metric_name: str, time_range_hours: int
    ) -> dict[str, ContextValue]: ...

    async def get_error_analysis(
        self, time_range_hours: int
    ) -> dict[str, ContextValue]: ...

    async def get_capacity_metrics(self) -> dict[str, ContextValue]: ...
```

### MCP Subsystem Client Protocol

```python
@runtime_checkable
class ProtocolMCPSubsystemClient(Protocol):
    """
    Protocol for MCP subsystem client operations.

    Provides communication with individual MCP subsystems,
    tool execution, and health monitoring.

    Key Features:
        - Tool execution coordination
        - Health monitoring and status tracking
        - Configuration management
        - Performance metrics collection
        - Error handling and recovery
    """

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        timeout_seconds: int | None = None,
    ) -> dict[str, ContextValue]: ...

    async def get_available_tools(self) -> list[ProtocolMCPToolDefinition]: ...

    async def get_tool_schema(self, tool_name: str) -> dict[str, Any]: ...

    async def validate_tool_parameters(
        self, tool_name: str, parameters: dict[str, ContextValue]
    ) -> ProtocolValidationResult: ...

    async def get_subsystem_health(self) -> ProtocolMCPHealthCheck: ...

    async def get_subsystem_metrics(self) -> ProtocolMCPSubsystemMetrics: ...

    async def update_configuration(
        self, configuration: dict[str, ContextValue]
    ) -> bool: ...

    async def get_configuration(self) -> dict[str, ContextValue]: ...
```

### MCP Tool Proxy Protocol

```python
@runtime_checkable
class ProtocolMCPToolProxy(Protocol):
    """
    Protocol for MCP tool proxy operations.

    Provides transparent tool execution through proxy patterns,
    load balancing, and failover capabilities.

    Key Features:
        - Transparent tool execution
        - Load balancing across implementations
        - Failover and error handling
        - Performance monitoring
        - Caching and optimization
    """

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        options: ProtocolMCPToolExecutionOptions | None = None,
    ) -> ProtocolMCPToolExecutionResult: ...

    async def get_tool_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]: ...

    async def select_best_implementation(
        self, tool_name: str, parameters: dict[str, ContextValue]
    ) -> ProtocolMCPToolDefinition: ...

    async def get_execution_history(
        self, tool_name: str, limit: int = 100
    ) -> list[ProtocolMCPToolExecution]: ...

    async def get_performance_metrics(
        self, tool_name: str, time_range_hours: int = 24
    ) -> ProtocolMCPToolPerformanceMetrics: ...
```

### MCP Tool Router Protocol

```python
@runtime_checkable
class ProtocolMCPToolRouter(Protocol):
    """
    Protocol for MCP tool routing and load balancing.

    Provides intelligent tool routing, load balancing strategies,
    and failover capabilities across MCP subsystems.

    Key Features:
        - Intelligent tool routing
        - Load balancing strategies
        - Failover and recovery
        - Performance-based routing
        - Health-aware routing
    """

    async def route_tool_execution(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        routing_options: ProtocolMCPRoutingOptions | None = None,
    ) -> ProtocolMCPRoutingDecision: ...

    async def get_routing_strategy(
        self, tool_name: str
    ) -> LiteralMCPRoutingStrategy: ...

    async def update_routing_strategy(
        self, tool_name: str, strategy: LiteralMCPRoutingStrategy
    ) -> bool: ...

    async def get_load_balancing_weights(
        self, tool_name: str
    ) -> dict[str, float]: ...

    async def update_load_balancing_weights(
        self, tool_name: str, weights: dict[str, float]
    ) -> bool: ...

    async def get_routing_metrics(
        self, tool_name: str | None = None
    ) -> ProtocolMCPRoutingMetrics: ...
```

### MCP Monitor Protocol

```python
@runtime_checkable
class ProtocolMCPMonitor(Protocol):
    """
    Protocol for MCP system monitoring and observability.

    Provides comprehensive monitoring, alerting, and diagnostics
    for MCP subsystems and tool execution.

    Key Features:
        - System health monitoring
        - Performance metrics collection
        - Alert management
        - Diagnostic capabilities
        - Trend analysis
    """

    async def monitor_subsystem_health(
        self, subsystem_id: str
    ) -> ProtocolMCPHealthStatus: ...

    async def monitor_tool_performance(
        self, tool_name: str, time_range_hours: int = 24
    ) -> ProtocolMCPToolPerformanceStatus: ...

    async def get_system_overview(self) -> ProtocolMCPSystemOverview: ...

    async def get_alert_summary(self) -> ProtocolMCPAlertSummary: ...

    async def create_alert_rule(
        self, rule: ProtocolMCPAlertRule
    ) -> str: ...

    async def update_alert_rule(
        self, rule_id: str, rule: ProtocolMCPAlertRule
    ) -> bool: ...

    async def delete_alert_rule(self, rule_id: str) -> bool: ...

    async def get_alert_rules(self) -> list[ProtocolMCPAlertRule]: ...

    async def get_diagnostics(
        self, subsystem_id: str | None = None
    ) -> ProtocolMCPDiagnostics: ...
```

## 🔧 Type Definitions

### MCP Subsystem Types

```python
LiteralMCPSubsystemType = Literal[
    "llm", "code_analysis", "data_processing", "web_scraping", "file_handling", "custom"
]
"""
MCP subsystem types for categorization.

Values:
    llm: Large Language Model subsystems
    code_analysis: Code analysis and processing subsystems
    data_processing: Data processing and transformation subsystems
    web_scraping: Web scraping and data extraction subsystems
    file_handling: File processing and management subsystems
    custom: Custom subsystem implementations
"""

LiteralMCPToolType = Literal[
    "function", "query", "analysis", "transformation", "extraction", "validation"
]
"""
MCP tool types for categorization.

Values:
    function: General purpose function tools
    query: Data query and retrieval tools
    analysis: Analysis and processing tools
    transformation: Data transformation tools
    extraction: Data extraction tools
    validation: Data validation tools
"""

LiteralMCPRoutingStrategy = Literal[
    "round_robin", "least_connections", "weighted", "health_based", "performance_based"
]
"""
MCP routing strategies for load balancing.

Values:
    round_robin: Round-robin distribution
    least_connections: Route to subsystem with least active connections
    weighted: Weighted distribution based on capacity
    health_based: Route based on subsystem health
    performance_based: Route based on performance metrics
"""
```

## 🚀 Usage Examples

### Subsystem Registration

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

# Initialize MCP registry
mcp_registry: ProtocolMCPRegistry = get_mcp_registry()

# Register subsystem
registration_id = await mcp_registry.register_subsystem(
    subsystem_metadata=ProtocolMCPSubsystemMetadata(
        subsystem_id="llm-subsystem-1",
        subsystem_type="llm",
        host="192.168.1.100",
        port=8080,
        version="1.2.3"
    ),
    tools=[
        ProtocolMCPToolDefinition(
            tool_name="text_generation",
            tool_type="function",
            description="Generate text using LLM",
            parameters={
                "prompt": {"type": "string", "required": True},
                "max_tokens": {"type": "integer", "required": False}
            }
        ),
        ProtocolMCPToolDefinition(
            tool_name="text_analysis",
            tool_type="analysis",
            description="Analyze text content",
            parameters={
                "text": {"type": "string", "required": True},
                "analysis_type": {"type": "string", "required": True}
            }
        )
    ],
    api_key="mcp-api-key-12345",
    configuration={
        "model": "gpt-4",
        "max_concurrent_requests": 10,
        "timeout_seconds": 30
    }
)
```

### Tool Discovery and Execution

```python
# Discover tools
tools = await mcp_registry.discover_tools(
    tool_type="function",
    tags=["llm", "text_generation"],
    subsystem_id="llm-subsystem-1"
)

# Execute tool
result = await mcp_registry.execute_tool(
    tool_name="text_generation",
    parameters={
        "prompt": "Write a short story about a robot",
        "max_tokens": 500
    },
    correlation_id=UUID("req-abc123"),
    timeout_seconds=30,
    preferred_subsystem="llm-subsystem-1"
)

print(f"Generated text: {result['text']}")
```

### Load Balancing and Routing

```python
from omnibase_spi.protocols.mcp import ProtocolMCPToolRouter

# Initialize tool router
tool_router: ProtocolMCPToolRouter = get_mcp_tool_router()

# Route tool execution
routing_decision = await tool_router.route_tool_execution(
    tool_name="text_generation",
    parameters={"prompt": "Hello world"},
    routing_options=ProtocolMCPRoutingOptions(
        preferred_subsystem=None,
        load_balancing_strategy="health_based",
        failover_enabled=True
    )
)

print(f"Selected subsystem: {routing_decision.selected_subsystem}")
print(f"Routing reason: {routing_decision.routing_reason}")
```

### Health Monitoring

```python
from omnibase_spi.protocols.mcp import ProtocolMCPMonitor

# Initialize MCP monitor
mcp_monitor: ProtocolMCPMonitor = get_mcp_monitor()

# Monitor subsystem health
health_status = await mcp_monitor.monitor_subsystem_health("llm-subsystem-1")
print(f"Subsystem health: {health_status.overall_status}")
print(f"Active tools: {health_status.active_tools}")
print(f"Response time: {health_status.avg_response_time_ms}ms")

# Monitor tool performance
tool_performance = await mcp_monitor.monitor_tool_performance(
    "text_generation",
    time_range_hours=24
)
print(f"Success rate: {tool_performance.success_rate}%")
print(f"Average execution time: {tool_performance.avg_execution_time_ms}ms")
```

### Tool Proxy Usage

```python
from omnibase_spi.protocols.mcp import ProtocolMCPToolProxy

# Initialize tool proxy
tool_proxy: ProtocolMCPToolProxy = get_mcp_tool_proxy()

# Execute tool through proxy
execution_result = await tool_proxy.execute_tool(
    tool_name="text_analysis",
    parameters={
        "text": "This is a sample text for analysis",
        "analysis_type": "sentiment"
    },
    options=ProtocolMCPToolExecutionOptions(
        timeout_seconds=30,
        retry_count=3,
        failover_enabled=True
    )
)

print(f"Analysis result: {execution_result.result}")
print(f"Execution time: {execution_result.execution_time_ms}ms")
print(f"Subsystem used: {execution_result.subsystem_id}")
```

### Advanced Metrics and Analytics

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistryMetricsOperations

# Initialize metrics operations
metrics_ops: ProtocolMCPRegistryMetricsOperations = get_mcp_metrics_operations()

# Get execution metrics
execution_metrics = await metrics_ops.get_execution_metrics(
    time_range_hours=24,
    tool_name="text_generation",
    subsystem_id="llm-subsystem-1"
)
print(f"Total executions: {execution_metrics['total_executions']}")
print(f"Success rate: {execution_metrics['success_rate']}%")
print(f"Average response time: {execution_metrics['avg_response_time_ms']}ms")

# Get performance trends
performance_trends = await metrics_ops.get_performance_trends(
    metric_name="response_time",
    time_range_hours=168  # 1 week
)
print(f"Performance trend: {performance_trends['trend_direction']}")

# Get error analysis
error_analysis = await metrics_ops.get_error_analysis(time_range_hours=24)
print(f"Error rate: {error_analysis['error_rate']}%")
print(f"Top errors: {error_analysis['top_errors']}")
```

## 🔍 Implementation Notes

### Multi-Subsystem Coordination

The MCP protocols support sophisticated multi-subsystem coordination:

```python
# Register multiple subsystems
llm_subsystem = await mcp_registry.register_subsystem(llm_metadata, llm_tools, api_key)
data_subsystem = await mcp_registry.register_subsystem(data_metadata, data_tools, api_key)

# Discover tools across all subsystems
all_tools = await mcp_registry.discover_tools(tool_type="function")
print(f"Found {len(all_tools)} tools across {len(set(t.subsystem_id for t in all_tools))} subsystems")
```

### Load Balancing Strategies

Advanced load balancing and routing:

```python
# Configure routing strategy
await tool_router.update_routing_strategy("text_generation", "performance_based")

# Set load balancing weights
await tool_router.update_load_balancing_weights(
    "text_generation",
    {
        "llm-subsystem-1": 0.6,
        "llm-subsystem-2": 0.4
    }
)
```

### Health Monitoring and Alerting

Comprehensive monitoring capabilities:

```python
# Create alert rule
alert_rule = await mcp_monitor.create_alert_rule(
    ProtocolMCPAlertRule(
        name="High Error Rate",
        condition="error_rate > 0.1",
        severity="warning",
        enabled=True
    )
)

# Get system overview
overview = await mcp_monitor.get_system_overview()
print(f"Total subsystems: {overview.total_subsystems}")
print(f"Healthy subsystems: {overview.healthy_subsystems}")
print(f"Total tools: {overview.total_tools}")
```

## 📊 Protocol Statistics

- **Total Protocols**: 15 MCP integration protocols
- **Multi-Subsystem Coordination**: Dynamic subsystem registration and discovery
- **Tool Management**: Comprehensive tool definition and execution tracking
- **Load Balancing**: Advanced routing strategies and failover capabilities
- **Health Monitoring**: Real-time health tracking and alerting
- **Performance Analytics**: Detailed metrics and trend analysis
- **Security**: API key authentication and request validation
- **TTL Management**: Automatic cleanup of expired registrations

---

## See Also

- **[HANDLERS.md](./HANDLERS.md)** - Handler protocols for MCP tool execution
- **[REGISTRY.md](./REGISTRY.md)** - Handler registry patterns applicable to MCP subsystem registration
- **[CORE.md](./CORE.md)** - Core protocols including health monitoring
- **[EXCEPTIONS.md](./EXCEPTIONS.md)** - Exception hierarchy for MCP error handling
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*
