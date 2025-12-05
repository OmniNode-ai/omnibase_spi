"""
MCP Tool and Event Bus types for ONEX SPI interfaces.

Domain: MCP tool definitions, execution, CLI models, and event bus protocols.
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    ProtocolDateTime,
    ProtocolSemVer,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_mcp_types import (
        ProtocolMCPValidationResult,
    )

LiteralMCPToolType = Literal["function", "resource", "prompt", "sampling", "completion"]
LiteralMCPParameterType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]
LiteralMCPExecutionStatus = Literal[
    "pending", "running", "completed", "failed", "timeout", "cancelled"
]


@runtime_checkable
class ProtocolMCPToolParameter(Protocol):
    """
    Protocol for MCP tool parameter definition.

    Defines the structure for parameters accepted by MCP tools, including
    type information, validation constraints, and documentation. Used for
    tool introspection, validation, and UI generation.

    Attributes:
        name: Parameter name used in tool invocation.
        parameter_type: Data type (string, number, boolean, etc.).
        description: Human-readable parameter description.
        required: Whether the parameter must be provided.
        default_value: Default value if not provided.
        schema: JSON Schema for complex type validation.
        constraints: Additional validation constraints.
        examples: Example values for documentation.

    Example:
        ```python
        class QueryParameter:
            '''Search query parameter for search tool.'''

            name = "query"
            parameter_type = "string"
            description = "Search query string"
            required = True
            default_value = None
            schema = {"minLength": 1, "maxLength": 500}
            constraints = {"pattern": r"^[a-zA-Z0-9\\s]+$"}
            examples = ["python tutorial", "machine learning basics"]

            async def validate_parameter(self) -> bool:
                return self.name and self.parameter_type

            def is_required_parameter(self) -> bool:
                return self.required

        param = QueryParameter()
        assert isinstance(param, ProtocolMCPToolParameter)
        ```
    """

    name: str
    parameter_type: LiteralMCPParameterType
    description: str
    required: bool
    default_value: ContextValue | None
    schema: dict[str, ContextValue] | None
    constraints: dict[str, ContextValue]
    examples: list[ContextValue]

    async def validate_parameter(self) -> bool: ...

    def is_required_parameter(self) -> bool: ...


@runtime_checkable
class ProtocolMCPToolDefinition(Protocol):
    """
    Protocol for MCP tool definition.

    Defines the complete specification for an MCP tool including its
    interface, execution requirements, and metadata. Used for tool
    registration, discovery, and invocation in the MCP ecosystem.

    Attributes:
        name: Unique tool identifier.
        tool_type: Category of tool (function, resource, prompt, etc.).
        description: Human-readable tool description.
        version: Tool version using semantic versioning.
        parameters: List of parameter definitions.
        return_schema: JSON Schema for return value validation.
        execution_endpoint: URL or path for tool execution.
        timeout_seconds: Maximum execution time allowed.
        retry_count: Number of retry attempts on failure.
        requires_auth: Whether authentication is required.
        tags: Categorization tags for discovery.
        metadata: Additional tool properties.

    Example:
        ```python
        class SearchToolDefinition:
            '''Definition for a web search tool.'''

            name = "web_search"
            tool_type = "function"
            description = "Search the web for information"
            version = SemVer(1, 0, 0)
            parameters = [QueryParameter()]  # ProtocolMCPToolParameter
            return_schema = {"type": "object", "properties": {"results": {}}}
            execution_endpoint = "/api/v1/tools/search"
            timeout_seconds = 30
            retry_count = 3
            requires_auth = True
            tags = ["search", "web", "information"]
            metadata = {"rate_limit": 100}

            async def validate_tool_definition(self) -> bool:
                return self.name and self.execution_endpoint

        tool_def = SearchToolDefinition()
        assert isinstance(tool_def, ProtocolMCPToolDefinition)
        ```
    """

    name: str
    tool_type: LiteralMCPToolType
    description: str
    version: ProtocolSemVer
    parameters: list[ProtocolMCPToolParameter]
    return_schema: dict[str, ContextValue] | None
    execution_endpoint: str
    timeout_seconds: int
    retry_count: int
    requires_auth: bool
    tags: list[str]
    metadata: dict[str, ContextValue]

    async def validate_tool_definition(self) -> bool: ...


@runtime_checkable
class ProtocolMCPToolExecution(Protocol):
    """
    Protocol for MCP tool execution tracking.

    Tracks the execution lifecycle of an MCP tool invocation including
    timing, status, results, and correlation information. Used for
    observability, debugging, and execution history.

    Attributes:
        execution_id: Unique execution identifier.
        tool_name: Name of the tool being executed.
        subsystem_id: Identifier of the executing subsystem.
        parameters: Input parameters for the execution.
        execution_status: Current execution state.
        started_at: Execution start timestamp.
        completed_at: Execution completion timestamp.
        duration_ms: Total execution duration in milliseconds.
        result: Execution result data (if completed).
        error_message: Error details (if failed).
        retry_count: Number of retry attempts made.
        correlation_id: UUID for request correlation.
        metadata: Additional execution context.

    Example:
        ```python
        class SearchExecution:
            '''Execution record for a search tool invocation.'''

            execution_id = "exec_abc123"
            tool_name = "web_search"
            subsystem_id = "search-subsystem-01"
            parameters = {"query": "python tutorials"}
            execution_status = "completed"
            started_at = datetime.now() - timedelta(seconds=2)
            completed_at = datetime.now()
            duration_ms = 1850
            result = {"results": [{"title": "Python Tutorial", "url": "..."}]}
            error_message = None
            retry_count = 0
            correlation_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            metadata = {"user_id": "user_123"}

            async def validate_execution(self) -> bool:
                return self.execution_id and self.tool_name

        execution = SearchExecution()
        assert isinstance(execution, ProtocolMCPToolExecution)
        ```
    """

    execution_id: str
    tool_name: str
    subsystem_id: str
    parameters: dict[str, "ContextValue"]
    execution_status: LiteralMCPExecutionStatus
    started_at: ProtocolDateTime
    completed_at: ProtocolDateTime | None
    duration_ms: int | None
    result: dict[str, ContextValue] | None
    error_message: str | None
    retry_count: int
    correlation_id: UUID
    metadata: dict[str, ContextValue]

    async def validate_execution(self) -> bool: ...


@runtime_checkable
class ProtocolToolClass(Protocol):
    """
    Protocol for tool class objects in MCP systems.

    Defines the interface for tool factory classes that can instantiate
    tool instances. Used for dynamic tool loading and registration in
    the MCP subsystem architecture.

    Attributes:
        __name__: Class name for identification.
        __module__: Module path where the class is defined.

    Example:
        ```python
        class SearchToolClass:
            '''Factory class for search tool instances.'''

            __name__ = "SearchTool"
            __module__ = "onex.tools.search"

            async def __call__(self, *args, **kwargs) -> ProtocolToolInstance:
                instance = SearchToolInstance()
                await instance.initialize(*args, **kwargs)
                return instance

        tool_class = SearchToolClass()
        assert isinstance(tool_class, ProtocolToolClass)
        instance = await tool_class(api_key="key123")
        ```
    """

    __name__: str
    __module__: str

    async def __call__(
        self, *args: object, **kwargs: object
    ) -> "ProtocolToolInstance": ...


@runtime_checkable
class ProtocolToolInstance(Protocol):
    """
    Protocol for tool instance objects in MCP systems.

    Represents an initialized, executable tool instance with full lifecycle
    management including execution, validation, and health checking. Used
    by the MCP runtime to invoke tools and manage their state.

    Attributes:
        tool_name: Unique name identifying the tool.
        tool_version: Semantic version of the tool.
        tool_type: Category of tool (function, resource, etc.).
        is_initialized: Whether the instance is ready for execution.

    Example:
        ```python
        class SearchToolInstance:
            '''Initialized search tool ready for execution.'''

            tool_name = "web_search"
            tool_version = SemVer(1, 0, 0)
            tool_type = "function"
            is_initialized = True

            async def execute(self, parameters: dict) -> dict:
                query = parameters.get("query", "")
                # Perform search...
                return {"results": [...], "count": 10}

            async def validate_parameters(self, parameters: dict):
                # Return validation result
                return ValidationResult(is_valid=True, errors=[])

            async def health_check(self) -> dict:
                return {"status": "healthy", "latency_ms": 50}

        instance = SearchToolInstance()
        assert isinstance(instance, ProtocolToolInstance)
        result = await instance.execute({"query": "python"})
        ```
    """

    tool_name: str
    tool_version: ProtocolSemVer
    tool_type: LiteralMCPToolType
    is_initialized: bool

    async def execute(
        self, parameters: dict[str, ContextValue]
    ) -> dict[str, ContextValue]: ...

    async def validate_parameters(
        self, parameters: dict[str, ContextValue]
    ) -> "ProtocolMCPValidationResult": ...

    async def health_check(self) -> dict[str, ContextValue]: ...


# CLI Tool Types for ProtocolTool interface
@runtime_checkable
class ProtocolModelResultCLI(Protocol):
    """
    Protocol for CLI result models.

    Represents the result of a CLI tool execution including exit codes,
    output data, and diagnostic information. Used for command-line tool
    integration within the MCP ecosystem.

    Attributes:
        success: Whether the command succeeded.
        message: Human-readable result message.
        data: Structured output data from the command.
        exit_code: Process exit code (0 for success).
        execution_time_ms: Command execution duration.
        warnings: Non-fatal warning messages.
        errors: Error messages if failed.

    Example:
        ```python
        class LintResult:
            '''Result from a code linting CLI tool.'''

            success = True
            message = "Linting completed with 2 warnings"
            data = {"files_checked": 15, "issues_found": 2}
            exit_code = 0
            execution_time_ms = 1250
            warnings = ["Line too long in main.py:42", "Unused import in utils.py"]
            errors = []

        result = LintResult()
        assert isinstance(result, ProtocolModelResultCLI)
        if result.success:
            print(f"Checked {result.data['files_checked']} files")
        ```
    """

    success: bool
    message: str
    data: dict[str, ContextValue] | None
    exit_code: int
    execution_time_ms: int | None
    warnings: list[str]
    errors: list[str]


@runtime_checkable
class ProtocolModelToolArguments(Protocol):
    """
    Protocol for tool arguments model.

    Defines standard command-line arguments and flags for tool invocation.
    Provides consistent argument handling across CLI and programmatic
    tool execution contexts.

    Attributes:
        tool_name: Name of the tool being invoked.
        apply: Whether to apply changes (vs preview).
        verbose: Enable verbose output.
        dry_run: Simulate execution without changes.
        force: Override safety checks.
        interactive: Enable interactive prompts.
        config_path: Path to configuration file.
        additional_args: Tool-specific additional arguments.

    Example:
        ```python
        class MigrationArgs:
            '''Arguments for database migration tool.'''

            tool_name = "db_migrate"
            apply = True
            verbose = True
            dry_run = False
            force = False
            interactive = False
            config_path = "/etc/onex/db.yaml"
            additional_args = {"target_version": "v2.0.0"}

        args = MigrationArgs()
        assert isinstance(args, ProtocolModelToolArguments)
        if args.dry_run:
            print("Dry run mode - no changes will be applied")
        ```
    """

    tool_name: str
    apply: bool
    verbose: bool
    dry_run: bool
    force: bool
    interactive: bool
    config_path: str | None
    additional_args: dict[str, ContextValue]


@runtime_checkable
class ProtocolModelToolInputData(Protocol):
    """
    Protocol for tool input data model.

    Encapsulates input data for tool execution including payload,
    metadata, and correlation information. Used for structured data
    passing between tools and orchestration systems.

    Attributes:
        tool_name: Target tool for this input.
        input_type: Type classifier for the input data.
        data: Actual input payload as key-value pairs.
        metadata: Additional context about the input.
        timestamp: When the input was created.
        correlation_id: Optional UUID for request tracing.

    Example:
        ```python
        class TransformInput:
            '''Input data for a data transformation tool.'''

            tool_name = "json_transformer"
            input_type = "json_document"
            data = {"source": {"name": "Alice", "age": 30}}
            metadata = {"schema_version": "1.0", "encoding": "utf-8"}
            timestamp = datetime.now()
            correlation_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        input_data = TransformInput()
        assert isinstance(input_data, ProtocolModelToolInputData)
        ```
    """

    tool_name: str
    input_type: str
    data: dict[str, ContextValue]
    metadata: dict[str, ContextValue]
    timestamp: ProtocolDateTime
    correlation_id: UUID | None


@runtime_checkable
class ProtocolModelToolInfo(Protocol):
    """
    Protocol for tool information model.

    Provides comprehensive metadata about a tool including its location,
    dependencies, capabilities, and runtime requirements. Used for tool
    discovery, dependency resolution, and registry management.

    Attributes:
        tool_name: Unique tool identifier.
        tool_path: Filesystem path to tool implementation.
        contract_path: Path to the tool's contract definition.
        description: Human-readable tool description.
        version: Tool version using semantic versioning.
        author: Tool author or maintainer.
        tags: Categorization tags for discovery.
        capabilities: List of capabilities the tool provides.
        dependencies: Required dependency tool names.
        entrypoint: Main entry point for execution.
        runtime_language: Implementation language (python, node, etc.).
        metadata: Additional tool properties.
        is_active: Whether the tool is currently active.
        last_updated: Last modification timestamp.

    Example:
        ```python
        class SearchToolInfo:
            '''Metadata for the web search tool.'''

            tool_name = "web_search"
            tool_path = "/opt/onex/tools/search"
            contract_path = "/opt/onex/contracts/search.yaml"
            description = "Search the web using multiple engines"
            version = SemVer(1, 2, 0)
            author = "ONEX Team"
            tags = ["search", "web", "information-retrieval"]
            capabilities = ["web_search", "image_search"]
            dependencies = ["http_client", "rate_limiter"]
            entrypoint = "main.py"
            runtime_language = "python"
            metadata = {"license": "MIT", "min_python": "3.10"}
            is_active = True
            last_updated = datetime.now()

        info = SearchToolInfo()
        assert isinstance(info, ProtocolModelToolInfo)
        ```
    """

    tool_name: str
    tool_path: str
    contract_path: str
    description: str
    version: ProtocolSemVer
    author: str | None
    tags: list[str]
    capabilities: list[str]
    dependencies: list[str]
    entrypoint: str
    runtime_language: str
    metadata: dict[str, ContextValue]
    is_active: bool
    last_updated: ProtocolDateTime


@runtime_checkable
class ProtocolEventBusConfig(Protocol):
    """
    Protocol for event bus configuration.

    Defines configuration parameters for Kafka/RedPanda event bus
    connections including cluster settings, security, and topic defaults.
    Used for initializing event bus clients and producers.

    Attributes:
        bootstrap_servers: List of broker addresses (host:port).
        topic_prefix: Namespace prefix for topic names.
        replication_factor: Number of replicas for topics.
        partitions: Default partition count for new topics.
        retention_ms: Message retention period in milliseconds.
        compression_type: Compression algorithm (none, gzip, snappy, lz4).
        security_protocol: Protocol for broker communication.
        sasl_mechanism: SASL authentication mechanism.
        sasl_username: SASL username for authentication.
        sasl_password: SASL password for authentication.
        metadata: Additional configuration properties.

    Example:
        ```python
        class ProductionEventBusConfig:
            '''Production Kafka cluster configuration.'''

            bootstrap_servers = ["kafka1:9092", "kafka2:9092", "kafka3:9092"]
            topic_prefix = "onex.production"
            replication_factor = 3
            partitions = 12
            retention_ms = 7 * 24 * 60 * 60 * 1000  # 7 days
            compression_type = "lz4"
            security_protocol = "SASL_SSL"
            sasl_mechanism = "SCRAM-SHA-256"
            sasl_username = "onex-producer"
            sasl_password = "secret"
            metadata = {"acks": "all", "retries": 3}

        config = ProductionEventBusConfig()
        assert isinstance(config, ProtocolEventBusConfig)
        ```
    """

    bootstrap_servers: list[str]
    topic_prefix: str
    replication_factor: int
    partitions: int
    retention_ms: int
    compression_type: str
    security_protocol: str
    sasl_mechanism: str | None
    sasl_username: str | None
    sasl_password: str | None
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolEventBusBootstrapResult(Protocol):
    """
    Protocol for event bus bootstrap result.

    Reports the outcome of event bus initialization including cluster
    discovery, topic creation, and any errors encountered. Used for
    validating event bus readiness and debugging connection issues.

    Attributes:
        success: Whether bootstrap completed successfully.
        cluster_id: Kafka cluster identifier.
        controller_id: ID of the cluster controller broker.
        topics_created: List of topics created during bootstrap.
        errors: Error messages encountered.
        warnings: Non-fatal warning messages.
        execution_time_ms: Total bootstrap duration.
        bootstrap_config: Configuration used for bootstrap.
        metadata: Additional bootstrap information.

    Example:
        ```python
        class SuccessfulBootstrap:
            '''Result of successful event bus initialization.'''

            success = True
            cluster_id = "kafka-cluster-prod-001"
            controller_id = 1
            topics_created = [
                "onex.production.events",
                "onex.production.commands"
            ]
            errors = []
            warnings = ["Topic onex.production.legacy already exists"]
            execution_time_ms = 2500
            bootstrap_config = ProductionEventBusConfig()
            metadata = {"broker_count": 3}

        result = SuccessfulBootstrap()
        assert isinstance(result, ProtocolEventBusBootstrapResult)
        if result.success:
            print(f"Connected to cluster: {result.cluster_id}")
        ```
    """

    success: bool
    cluster_id: str | None
    controller_id: int | None
    topics_created: list[str]
    errors: list[str]
    warnings: list[str]
    execution_time_ms: int
    bootstrap_config: ProtocolEventBusConfig
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolKafkaHealthCheckResult(Protocol):
    """
    Protocol for Kafka health check result.

    Provides comprehensive health status for a Kafka cluster including
    broker health, partition status, and replication state. Used for
    monitoring, alerting, and operational health dashboards.

    Attributes:
        cluster_healthy: Overall cluster health status.
        cluster_id: Kafka cluster identifier.
        controller_id: ID of the current controller broker.
        broker_count: Total number of brokers in cluster.
        healthy_brokers: List of broker IDs that are healthy.
        unhealthy_brokers: List of broker IDs that are unhealthy.
        topic_count: Total number of topics in cluster.
        partition_count: Total number of partitions across all topics.
        under_replicated_partitions: Partitions with insufficient replicas.
        offline_partitions: Partitions that are completely offline.
        response_time_ms: Health check response latency.
        errors: Critical error messages.
        warnings: Warning messages for degraded conditions.
        metadata: Additional health check information.

    Example:
        ```python
        class HealthyClusterCheck:
            '''Health check result for a healthy Kafka cluster.'''

            cluster_healthy = True
            cluster_id = "kafka-cluster-prod-001"
            controller_id = 1
            broker_count = 3
            healthy_brokers = [1, 2, 3]
            unhealthy_brokers = []
            topic_count = 25
            partition_count = 150
            under_replicated_partitions = 0
            offline_partitions = 0
            response_time_ms = 45
            errors = []
            warnings = []
            metadata = {"version": "3.4.0", "zk_connected": True}

        health = HealthyClusterCheck()
        assert isinstance(health, ProtocolKafkaHealthCheckResult)
        if not health.cluster_healthy:
            alert_ops_team(health.errors)
        ```
    """

    cluster_healthy: bool
    cluster_id: str | None
    controller_id: int | None
    broker_count: int
    healthy_brokers: list[int]
    unhealthy_brokers: list[int]
    topic_count: int
    partition_count: int
    under_replicated_partitions: int
    offline_partitions: int
    response_time_ms: int
    errors: list[str]
    warnings: list[str]
    metadata: dict[str, ContextValue]


__all__ = [
    "LiteralMCPExecutionStatus",
    "LiteralMCPParameterType",
    # Literal types
    "LiteralMCPToolType",
    "ProtocolEventBusBootstrapResult",
    # Event bus protocols
    "ProtocolEventBusConfig",
    "ProtocolKafkaHealthCheckResult",
    "ProtocolMCPToolDefinition",
    "ProtocolMCPToolExecution",
    # Tool protocols
    "ProtocolMCPToolParameter",
    # CLI model protocols
    "ProtocolModelResultCLI",
    "ProtocolModelToolArguments",
    "ProtocolModelToolInfo",
    "ProtocolModelToolInputData",
    "ProtocolToolClass",
    "ProtocolToolInstance",
]
