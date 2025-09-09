# MCP (Model Context Protocol) API Reference

## Overview

Comprehensive protocol interfaces for Model Context Protocol integration, enabling distributed tool coordination, subsystem management, and multi-subsystem orchestration across the ONEX ecosystem.

## Core Concepts

### Multi-Subsystem Architecture
- **Subsystem Registry**: Centralized registration and discovery of MCP subsystems
- **Tool Coordination**: Distributed tool execution with load balancing
- **Health Monitoring**: Continuous subsystem health monitoring with TTL cleanup
- **API Management**: Secure API key authentication and request validation

### Tool Execution Patterns
- **Dynamic Discovery**: Runtime tool discovery with type-based filtering
- **Load Balancing**: Distribute execution across multiple tool implementations
- **Execution Tracking**: Correlation IDs and performance metrics
- **Fault Tolerance**: Automatic failover and retry mechanisms

### Security and Validation
- **API Key Authentication**: Secure subsystem authentication
- **Request Validation**: Parameter validation against tool schemas
- **Rate Limiting**: Configurable rate limiting per subsystem
- **Access Control**: Fine-grained permissions and capabilities

## Type Definitions

### Tool Types

#### `MCPToolType`
```python
MCPToolType = Literal[
    "query", "compute", "transform", "validate", 
    "generate", "analyze", "monitor", "control"
]
```

Classification of MCP tools by functionality.

**Types:**
- `query`: Information retrieval and search tools
- `compute`: Computational processing tools  
- `transform`: Data transformation tools
- `validate`: Validation and verification tools
- `generate`: Content generation tools
- `analyze`: Analysis and insight tools
- `monitor`: Monitoring and observability tools
- `control`: System control and management tools

#### `MCPSubsystemType`
```python
MCPSubsystemType = Literal[
    "rag", "search", "code_analysis", "documentation",
    "testing", "deployment", "monitoring", "security"
]
```

Types of MCP subsystems in the ecosystem.

#### `MCPExecutionStatus`
```python
MCPExecutionStatus = Literal[
    "pending", "running", "completed", "failed", 
    "cancelled", "timeout", "retrying"
]
```

Status values for tool execution tracking.

#### `MCPLifecycleState`
```python
MCPLifecycleState = Literal[
    "registering", "active", "degraded", "inactive", 
    "error", "maintenance", "terminating"
]
```

Lifecycle states for subsystem management.

### Parameter Types

#### `MCPParameterType`
```python
MCPParameterType = Literal[
    "string", "integer", "number", "boolean", 
    "array", "object", "null"
]
```

Supported parameter types for tool definitions.

## Protocol Data Structures

### Tool Definition Protocols

#### `ProtocolMCPToolParameter`
```python
class ProtocolMCPToolParameter(Protocol):
    """Tool parameter definition with validation schema."""
    
    name: str
    parameter_type: MCPParameterType
    description: str
    required: bool
    default_value: Optional[ContextValue]
    validation_schema: Optional[dict[str, Any]]
    constraints: Optional[dict[str, Any]]
```

Parameter definition for MCP tools.

**Properties:**
- `name`: Parameter identifier
- `parameter_type`: Type of the parameter
- `description`: Human-readable parameter description
- `required`: Whether parameter is required
- `default_value`: Default value if not provided
- `validation_schema`: JSON schema for validation
- `constraints`: Additional parameter constraints

#### `ProtocolMCPToolDefinition`
```python
class ProtocolMCPToolDefinition(Protocol):
    """Complete tool definition with metadata and capabilities."""
    
    name: str
    tool_type: MCPToolType
    description: str
    parameters: list[ProtocolMCPToolParameter]
    return_schema: Optional[dict[str, Any]]
    capabilities: list[str]
    tags: list[str]
    version: ProtocolSemVer
    timeout_seconds: int
    max_retries: int
    rate_limit: Optional[int]
    subsystem_id: str
    metadata: dict[str, ContextValue]
```

Comprehensive tool definition.

### Subsystem Protocols

#### `ProtocolMCPSubsystemMetadata`
```python
class ProtocolMCPSubsystemMetadata(Protocol):
    """Subsystem identification and metadata."""
    
    subsystem_id: str
    subsystem_type: MCPSubsystemType
    name: str
    description: str
    version: ProtocolSemVer
    capabilities: list[str]
    supported_tool_types: list[MCPToolType]
    max_concurrent_executions: int
    api_endpoint: str
    health_check_endpoint: str
    metadata: dict[str, ContextValue]
```

Subsystem metadata and capabilities.

#### `ProtocolMCPSubsystemRegistration`
```python
class ProtocolMCPSubsystemRegistration(Protocol):
    """Complete subsystem registration information."""
    
    registration_id: str
    subsystem_metadata: ProtocolMCPSubsystemMetadata
    tools: list[ProtocolMCPToolDefinition]
    registration_time: ProtocolDateTime
    last_heartbeat: ProtocolDateTime
    ttl_seconds: int
    api_key_hash: str
    status: MCPLifecycleState
    configuration: dict[str, ContextValue]
    health_status: HealthStatus
    metrics: dict[str, float]
```

Complete registration record.

### Execution Protocols

#### `ProtocolMCPToolExecution`
```python
class ProtocolMCPToolExecution(Protocol):
    """Tool execution record with comprehensive tracking."""
    
    execution_id: str
    tool_name: str
    subsystem_id: str
    parameters: dict[str, ContextValue]
    correlation_id: UUID
    status: MCPExecutionStatus
    result: Optional[dict[str, Any]]
    error: Optional[ProtocolErrorInfo]
    start_time: ProtocolDateTime
    end_time: Optional[ProtocolDateTime]
    duration_ms: Optional[int]
    retry_count: int
    resource_usage: dict[str, int]
    metrics: dict[str, float]
```

Comprehensive execution tracking.

## Core Protocol Interfaces

### Registry Protocols

#### `ProtocolMCPRegistry`
```python
@runtime_checkable
class ProtocolMCPRegistry(Protocol):
    """
    Core MCP registry protocol for distributed tool coordination.
    
    Manages subsystem registration, tool discovery, and execution routing
    across multiple MCP-enabled subsystems in the ONEX ecosystem.
    
    Key Features:
        - **Multi-Subsystem Coordination**: Register and coordinate multiple MCP subsystems
        - **Dynamic Tool Discovery**: Discover and route tools across registered subsystems  
        - **Load Balancing**: Distribute tool execution across multiple implementations
        - **Health Monitoring**: Monitor subsystem health and handle failures gracefully
        - **Execution Tracking**: Track tool execution metrics and performance
        - **Security**: API key authentication and request validation
        - **TTL Management**: Automatic cleanup of expired registrations
    
    Example:
        ```python
        async def setup_mcp_subsystem(registry: ProtocolMCPRegistry):
            # Define tools
            tools = [
                ProtocolMCPToolDefinition(
                    name="semantic_search",
                    tool_type="query",
                    description="Search documents semantically",
                    parameters=[
                        ProtocolMCPToolParameter(
                            name="query",
                            parameter_type="string", 
                            description="Search query",
                            required=True
                        )
                    ],
                    # ... other fields
                )
            ]
            
            # Register subsystem
            registration_id = await registry.register_subsystem(
                subsystem_metadata=subsystem_info,
                tools=tools,
                api_key="secure_api_key",
                configuration={"max_results": 10}
            )
            
            # Execute tool
            result = await registry.execute_tool(
                tool_name="semantic_search",
                parameters={"query": "ONEX protocols"},
                correlation_id=uuid4()
            )
        ```
    """
    
    @property
    def config(self) -> ProtocolMCPRegistryConfig:
        """Get registry configuration."""
        ...
    
    # Subsystem Management
    async def register_subsystem(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
        api_key: str,
        configuration: Optional[dict[str, ContextValue]] = None,
    ) -> str:
        """
        Register a new subsystem and its tools with the registry.
        
        Args:
            subsystem_metadata: Subsystem identification and metadata
            tools: List of tool definitions provided by the subsystem
            api_key: Authentication key for the subsystem
            configuration: Optional subsystem-specific configuration
            
        Returns:
            Registration ID for the subsystem
            
        Raises:
            ValueError: If registration data is invalid or conflicts exist
        """
        ...
    
    async def unregister_subsystem(self, registration_id: str) -> bool:
        """
        Unregister a subsystem and remove all its tools.
        
        Args:
            registration_id: Subsystem registration ID
            
        Returns:
            True if unregistration successful
        """
        ...
    
    async def update_subsystem_heartbeat(
        self,
        registration_id: str,
        health_status: Optional[HealthStatus] = None,
        metadata: Optional[dict[str, ContextValue]] = None,
    ) -> bool:
        """
        Update subsystem heartbeat and health status.
        
        Args:
            registration_id: Subsystem registration ID
            health_status: Optional health status update
            metadata: Optional metadata update
            
        Returns:
            True if heartbeat update successful
        """
        ...
    
    # Tool Discovery
    async def discover_tools(
        self,
        tool_type: Optional[MCPToolType] = None,
        tags: Optional[list[str]] = None,
        subsystem_id: Optional[str] = None,
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Discover available tools with optional filtering.
        
        Args:
            tool_type: Optional filter by tool type
            tags: Optional filter by tool tags
            subsystem_id: Optional filter by subsystem
            
        Returns:
            List of matching tool definitions
        """
        ...
    
    async def get_tool_definition(
        self, tool_name: str
    ) -> Optional[ProtocolMCPToolDefinition]:
        """
        Get tool definition by name (returns first available implementation).
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool definition or None if not found
        """
        ...
    
    async def get_all_tool_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Get all implementations of a tool across subsystems.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of tool implementations
        """
        ...
    
    # Tool Execution
    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        correlation_id: UUID,
        timeout_seconds: Optional[int] = None,
        preferred_subsystem: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Execute a tool with load balancing and error handling.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool execution parameters
            correlation_id: Request correlation ID for tracing
            timeout_seconds: Optional execution timeout override
            preferred_subsystem: Optional subsystem preference
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found or parameters invalid
            TimeoutError: If execution times out
            RuntimeError: If execution fails
        """
        ...
    
    # Validation
    async def validate_tool_parameters(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
    ) -> ProtocolMCPValidationResult:
        """
        Validate tool execution parameters.
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate
            
        Returns:
            Validation result
        """
        ...
    
    # Health and Monitoring
    async def perform_health_check(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck:
        """
        Perform health check on a registered subsystem.
        
        Args:
            registration_id: Subsystem registration ID
            
        Returns:
            Health check result
        """
        ...
    
    async def get_registry_metrics(self) -> ProtocolMCPRegistryMetrics:
        """
        Get detailed registry metrics and statistics.
        
        Returns:
            Registry metrics
        """
        ...
```

### Tool Proxy Protocols

#### `ProtocolMCPToolProxy`
```python
@runtime_checkable  
class ProtocolMCPToolProxy(Protocol):
    """
    Tool execution proxy for distributed MCP tool calls.
    
    Handles tool execution routing, parameter marshaling, 
    result handling, and error management across subsystems.
    
    Key Features:
        - **Execution Routing**: Route calls to appropriate subsystems
        - **Parameter Marshaling**: Convert parameters to subsystem formats
        - **Result Handling**: Process and normalize tool results
        - **Error Management**: Handle and translate subsystem errors
        - **Retry Logic**: Automatic retry with backoff strategies
    """
    
    async def execute_tool(
        self,
        subsystem_id: str,
        tool_definition: ProtocolMCPToolDefinition,
        parameters: dict[str, ContextValue],
        correlation_id: UUID,
        timeout_seconds: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Execute tool on specific subsystem.
        
        Args:
            subsystem_id: Target subsystem identifier
            tool_definition: Tool definition to execute
            parameters: Tool execution parameters
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout override
            
        Returns:
            Tool execution result
        """
        ...
    
    async def validate_parameters(
        self,
        tool_definition: ProtocolMCPToolDefinition,
        parameters: dict[str, ContextValue],
    ) -> ProtocolMCPValidationResult:
        """
        Validate parameters against tool definition.
        
        Args:
            tool_definition: Tool definition with parameter schema
            parameters: Parameters to validate
            
        Returns:
            Validation result
        """
        ...
    
    async def marshal_parameters(
        self,
        tool_definition: ProtocolMCPToolDefinition,
        parameters: dict[str, ContextValue],
    ) -> dict[str, Any]:
        """
        Marshal parameters to subsystem format.
        
        Args:
            tool_definition: Tool definition
            parameters: Raw parameters
            
        Returns:
            Marshaled parameters
        """
        ...
```

### Monitoring Protocols

#### `ProtocolMCPMonitor`
```python
@runtime_checkable
class ProtocolMCPMonitor(Protocol):
    """
    MCP subsystem monitoring and health management.
    
    Provides comprehensive monitoring capabilities for MCP subsystems
    including health checks, performance metrics, and alerting.
    
    Key Features:
        - **Health Monitoring**: Continuous health status tracking
        - **Performance Metrics**: Execution metrics and statistics
        - **Alerting**: Configurable alerts for health issues
        - **Diagnostics**: Detailed diagnostic information
    """
    
    async def monitor_subsystem_health(
        self,
        registration_id: str,
        check_interval_seconds: int = 30,
    ) -> None:
        """
        Start monitoring subsystem health.
        
        Args:
            registration_id: Subsystem to monitor
            check_interval_seconds: Health check interval
        """
        ...
    
    async def get_subsystem_metrics(
        self,
        registration_id: str,
        time_window_seconds: int = 3600,
    ) -> dict[str, Any]:
        """
        Get subsystem performance metrics.
        
        Args:
            registration_id: Subsystem identifier
            time_window_seconds: Metrics time window
            
        Returns:
            Performance metrics
        """
        ...
    
    async def get_tool_execution_metrics(
        self,
        tool_name: Optional[str] = None,
        subsystem_id: Optional[str] = None,
        time_window_seconds: int = 3600,
    ) -> dict[str, Any]:
        """
        Get tool execution metrics.
        
        Args:
            tool_name: Optional tool name filter
            subsystem_id: Optional subsystem filter
            time_window_seconds: Metrics time window
            
        Returns:
            Execution metrics
        """
        ...
```

## Usage Examples

### Subsystem Registration

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry
from omnibase_spi.protocols.types.mcp_types import (
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolParameter
)

async def register_search_subsystem(registry: ProtocolMCPRegistry) -> str:
    """Register a search subsystem with tools."""
    
    # Define subsystem metadata
    subsystem_metadata = ProtocolMCPSubsystemMetadata(
        subsystem_id="semantic-search-v1",
        subsystem_type="search",
        name="Semantic Search Service",
        description="Provides semantic search capabilities",
        version=ProtocolSemVer(major=1, minor=0, patch=0),
        capabilities=["vector_search", "semantic_similarity"],
        supported_tool_types=["query"],
        max_concurrent_executions=10,
        api_endpoint="https://search.example.com/api",
        health_check_endpoint="https://search.example.com/health",
        metadata={"region": "us-east-1", "tier": "production"}
    )
    
    # Define tools
    tools = [
        ProtocolMCPToolDefinition(
            name="semantic_search",
            tool_type="query",
            description="Search documents using semantic similarity",
            parameters=[
                ProtocolMCPToolParameter(
                    name="query",
                    parameter_type="string",
                    description="Search query text",
                    required=True
                ),
                ProtocolMCPToolParameter(
                    name="limit",
                    parameter_type="integer", 
                    description="Maximum results to return",
                    required=False,
                    default_value=10,
                    constraints={"minimum": 1, "maximum": 100}
                )
            ],
            return_schema={
                "type": "object",
                "properties": {
                    "results": {"type": "array"},
                    "total_count": {"type": "integer"}
                }
            },
            capabilities=["vector_search"],
            tags=["search", "semantic", "nlp"],
            version=ProtocolSemVer(major=1, minor=0, patch=0),
            timeout_seconds=30,
            max_retries=3,
            subsystem_id="semantic-search-v1",
            metadata={"cost_per_query": 0.001}
        )
    ]
    
    # Register subsystem
    registration_id = await registry.register_subsystem(
        subsystem_metadata=subsystem_metadata,
        tools=tools,
        api_key="secure-api-key-123",
        configuration={
            "embedding_model": "sentence-transformers/all-mpnet-base-v2",
            "vector_dimension": 768
        }
    )
    
    print(f"Registered subsystem: {registration_id}")
    return registration_id
```

### Tool Discovery and Execution

```python
async def search_and_execute_tools(registry: ProtocolMCPRegistry):
    """Discover and execute MCP tools."""
    
    # Discover available query tools
    query_tools = await registry.discover_tools(
        tool_type="query",
        tags=["search"]
    )
    
    print(f"Found {len(query_tools)} query tools")
    
    # Execute semantic search
    if query_tools:
        correlation_id = uuid4()
        
        try:
            result = await registry.execute_tool(
                tool_name="semantic_search",
                parameters={
                    "query": "ONEX protocol architecture",
                    "limit": 5
                },
                correlation_id=correlation_id,
                timeout_seconds=30
            )
            
            print(f"Search results: {result}")
            
        except ValueError as e:
            print(f"Invalid parameters: {e}")
        except TimeoutError:
            print("Search timed out")
        except RuntimeError as e:
            print(f"Execution failed: {e}")
```

### Health Monitoring

```python
async def monitor_mcp_subsystems(
    registry: ProtocolMCPRegistry,
    monitor: ProtocolMCPMonitor
):
    """Monitor MCP subsystem health."""
    
    # Get all registered subsystems
    subsystems = await registry.get_all_subsystems()
    
    for subsystem in subsystems:
        registration_id = subsystem.registration_id
        
        # Perform health check
        health_check = await registry.perform_health_check(registration_id)
        print(f"Health check for {registration_id}: {health_check}")
        
        # Get performance metrics
        metrics = await monitor.get_subsystem_metrics(
            registration_id=registration_id,
            time_window_seconds=3600
        )
        print(f"Metrics for {registration_id}: {metrics}")
        
        # Start continuous monitoring
        await monitor.monitor_subsystem_health(
            registration_id=registration_id,
            check_interval_seconds=60
        )
```

### Load Balancing Example

```python
class MCPLoadBalancer:
    """Example MCP load balancer implementation."""
    
    def __init__(self, registry: ProtocolMCPRegistry):
        self.registry = registry
        self.execution_counts: dict[str, int] = {}
    
    async def execute_with_load_balancing(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        correlation_id: UUID
    ) -> dict[str, Any]:
        """Execute tool with load balancing across implementations."""
        
        # Get all implementations
        implementations = await self.registry.get_all_tool_implementations(tool_name)
        
        if not implementations:
            raise ValueError(f"No implementations found for tool: {tool_name}")
        
        # Select implementation with least executions
        selected_impl = min(
            implementations,
            key=lambda impl: self.execution_counts.get(impl.subsystem_id, 0)
        )
        
        # Update execution count
        self.execution_counts[selected_impl.subsystem_id] = (
            self.execution_counts.get(selected_impl.subsystem_id, 0) + 1
        )
        
        # Execute on selected subsystem
        return await self.registry.execute_tool(
            tool_name=tool_name,
            parameters=parameters,
            correlation_id=correlation_id,
            preferred_subsystem=selected_impl.subsystem_id
        )
```

## Integration Notes

### Multi-Subsystem Coordination

```python
class MCPOrchestrator:
    """Example MCP orchestrator for multi-subsystem workflows."""
    
    def __init__(self, registry: ProtocolMCPRegistry):
        self.registry = registry
    
    async def execute_workflow(self, workflow_steps: list[dict]) -> list[dict]:
        """Execute multi-step workflow across subsystems."""
        results = []
        
        for step in workflow_steps:
            tool_name = step["tool"]
            parameters = step["parameters"]
            
            # Add previous results to context if needed
            if results and step.get("use_previous_result"):
                parameters["context"] = results[-1]
            
            # Execute step
            result = await self.registry.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                correlation_id=uuid4()
            )
            
            results.append(result)
        
        return results
```

### Error Handling and Resilience

```python
class ResilientMCPClient:
    """Example resilient MCP client with error handling."""
    
    def __init__(self, registry: ProtocolMCPRegistry):
        self.registry = registry
    
    async def execute_with_retry(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> dict[str, Any]:
        """Execute tool with exponential backoff retry."""
        
        for attempt in range(max_retries + 1):
            try:
                return await self.registry.execute_tool(
                    tool_name=tool_name,
                    parameters=parameters,
                    correlation_id=uuid4()
                )
            except (TimeoutError, RuntimeError) as e:
                if attempt == max_retries:
                    raise
                
                # Calculate backoff delay
                delay = (backoff_factor ** attempt) * 1.0
                await asyncio.sleep(delay)
                
                print(f"Retrying {tool_name} after {delay}s (attempt {attempt + 1})")
        
        raise RuntimeError("Max retries exceeded")
```

## Best Practices

### Tool Definition Design

```python
# Good - Comprehensive tool definition
tool_definition = ProtocolMCPToolDefinition(
    name="document_analyzer",
    tool_type="analyze",
    description="Analyze document content for insights and metadata",
    parameters=[
        ProtocolMCPToolParameter(
            name="content",
            parameter_type="string",
            description="Document content to analyze",
            required=True,
            validation_schema={
                "minLength": 1,
                "maxLength": 100000
            }
        ),
        ProtocolMCPToolParameter(
            name="analysis_type",
            parameter_type="string", 
            description="Type of analysis to perform",
            required=False,
            default_value="comprehensive",
            constraints={
                "enum": ["basic", "comprehensive", "sentiment", "entities"]
            }
        )
    ],
    return_schema={
        "type": "object",
        "required": ["summary", "metadata"],
        "properties": {
            "summary": {"type": "string"},
            "metadata": {"type": "object"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        }
    },
    capabilities=["nlp", "analysis"],
    tags=["document", "analysis", "nlp"],
    version=ProtocolSemVer(major=1, minor=2, patch=0),
    timeout_seconds=60,
    max_retries=2,
    subsystem_id="document-analysis-service",
    metadata={"cost_model": "per_token", "supported_formats": ["text", "markdown"]}
)

# Avoid - Minimal tool definition lacking validation
bad_tool_definition = ProtocolMCPToolDefinition(
    name="analyzer",
    tool_type="analyze",
    description="Analyzes things",  # Too vague
    parameters=[],  # Missing parameter definitions
    # Missing return schema, validation, etc.
)
```

### Parameter Validation

```python
async def validate_tool_request(
    registry: ProtocolMCPRegistry,
    tool_name: str,
    parameters: dict[str, ContextValue]
) -> None:
    """Validate tool request before execution."""
    
    # Get tool definition
    tool_def = await registry.get_tool_definition(tool_name)
    if not tool_def:
        raise ValueError(f"Tool not found: {tool_name}")
    
    # Validate parameters
    validation_result = await registry.validate_tool_parameters(
        tool_name=tool_name,
        parameters=parameters
    )
    
    if not validation_result.is_valid:
        errors = ", ".join(validation_result.errors)
        raise ValueError(f"Parameter validation failed: {errors}")
```

### Subsystem Health Management

```python
class SubsystemHealthManager:
    """Example subsystem health management."""
    
    def __init__(self, registry: ProtocolMCPRegistry):
        self.registry = registry
        self.unhealthy_subsystems: set[str] = set()
    
    async def health_check_loop(self, check_interval: int = 60):
        """Continuous health checking loop."""
        while True:
            subsystems = await self.registry.get_all_subsystems()
            
            for subsystem in subsystems:
                try:
                    health_check = await self.registry.perform_health_check(
                        subsystem.registration_id
                    )
                    
                    if health_check.status == "healthy":
                        # Remove from unhealthy set if recovered
                        self.unhealthy_subsystems.discard(subsystem.registration_id)
                    else:
                        # Add to unhealthy set
                        self.unhealthy_subsystems.add(subsystem.registration_id)
                        print(f"Unhealthy subsystem: {subsystem.registration_id}")
                
                except Exception as e:
                    print(f"Health check failed for {subsystem.registration_id}: {e}")
                    self.unhealthy_subsystems.add(subsystem.registration_id)
            
            await asyncio.sleep(check_interval)
    
    def is_subsystem_healthy(self, registration_id: str) -> bool:
        """Check if subsystem is healthy."""
        return registration_id not in self.unhealthy_subsystems
```

---

*This documentation covers the complete MCP integration protocol suite. For integration with other domains, see the respective API reference sections.*