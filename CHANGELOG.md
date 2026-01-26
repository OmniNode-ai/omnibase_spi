# Changelog

All notable changes to the ONEX Service Provider Interface (omnibase_spi) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes

#### Handler Protocol `describe()` Method Now Async (OMN-710)

The `describe()` method in specialized handler protocols has been changed from synchronous to asynchronous:

**Affected Protocols:**
- `ProtocolGraphDatabaseHandler.describe()` - now returns `Coroutine[Any, Any, ModelGraphHandlerMetadata]`
- `ProtocolVectorStoreHandler.describe()` - now returns `Coroutine[Any, Any, ModelVectorHandlerMetadata]`

**Migration Required:**

```python
# Before (v0.4.x and earlier):
metadata = handler.describe()

# After (v0.5.0+):
metadata = await handler.describe()
```

**Rationale:**
Implementations may need to perform I/O operations to provide accurate metadata, such as:
- Checking connection status to the backing database
- Querying database version information
- Retrieving index/collection statistics
- Validating credentials before reporting capabilities

Making `describe()` async allows implementations to gather this runtime information without blocking.

**Note:** The base `ProtocolHandler.describe()` remains synchronous and returns `dict[str, Any]`. Only the specialized storage handlers (`ProtocolGraphDatabaseHandler`, `ProtocolVectorStoreHandler`) have been updated to async with typed return models. See the "Handler Protocol Typed Model Introduction" section below for the complete list of signature changes affecting both input parameters and return types.

#### Handler Protocol Typed Model Introduction (OMN-710)

Specialized handler protocols now use typed Pydantic models from `omnibase_core` instead of untyped `dict[str, Any]` for both input parameters and return values. This provides compile-time type safety and runtime validation.

**Return Type Changes:**

| Protocol | Method | Old Return Type | New Return Type |
|----------|--------|-----------------|-----------------|
| `ProtocolGraphDatabaseHandler` | `health_check()` | `dict[str, Any]` | `ModelGraphHealthStatus` |
| `ProtocolGraphDatabaseHandler` | `describe()` | `dict[str, Any]` | `ModelGraphHandlerMetadata` |
| `ProtocolGraphDatabaseHandler` | `execute_query()` | `dict[str, Any]` | `ModelGraphQueryResult` |
| `ProtocolGraphDatabaseHandler` | `execute_query_batch()` | `list[dict]` | `ModelGraphBatchResult` |
| `ProtocolGraphDatabaseHandler` | `create_node()` | `dict[str, Any]` | `ModelGraphDatabaseNode` |
| `ProtocolGraphDatabaseHandler` | `create_relationship()` | `dict[str, Any]` | `ModelGraphRelationship` |
| `ProtocolGraphDatabaseHandler` | `delete_node()` | `bool` | `ModelGraphDeleteResult` |
| `ProtocolGraphDatabaseHandler` | `delete_relationship()` | `bool` | `ModelGraphDeleteResult` |
| `ProtocolGraphDatabaseHandler` | `traverse()` | `dict[str, Any]` | `ModelGraphTraversalResult` |
| `ProtocolVectorStoreHandler` | `health_check()` | `dict[str, Any]` | `ModelVectorHealthStatus` |
| `ProtocolVectorStoreHandler` | `describe()` | `dict[str, Any]` | `ModelVectorHandlerMetadata` |
| `ProtocolVectorStoreHandler` | `store_embedding()` | `str` | `ModelVectorStoreResult` |
| `ProtocolVectorStoreHandler` | `store_embeddings_batch()` | `int` | `ModelVectorBatchStoreResult` |
| `ProtocolVectorStoreHandler` | `query_similar()` | `list[dict]` | `ModelVectorSearchResults` |
| `ProtocolVectorStoreHandler` | `delete_embedding()` | `bool` | `ModelVectorDeleteResult` |
| `ProtocolVectorStoreHandler` | `create_index()` | `None` | `ModelVectorIndexResult` |
| `ProtocolVectorStoreHandler` | `delete_index()` | `bool` | `ModelVectorIndexResult` |
| `ProtocolEventBusProducerHandler` | `health_check()` | `dict[str, Any]` | `ModelProducerHealthStatus` |

**Input Parameter Type Changes:**

| Protocol | Method | Parameter | Old Type | New Type |
|----------|--------|-----------|----------|----------|
| `ProtocolVectorStoreHandler` | `initialize()` | `connection_config` | `**kwargs` | `ModelVectorConnectionConfig` |
| `ProtocolVectorStoreHandler` | `store_embeddings_batch()` | `embeddings` | `list[dict]` | `list[ModelEmbedding]` |
| `ProtocolVectorStoreHandler` | `query_similar()` | `filter_metadata` | `dict[str, Any]` | `ModelVectorMetadataFilter` |
| `ProtocolVectorStoreHandler` | `create_index()` | `index_config` | `**kwargs` | `ModelVectorIndexConfig` |
| `ProtocolGraphDatabaseHandler` | `traverse()` | `filters` | `**kwargs` | `ModelGraphTraversalFilters` |
| `ProtocolEventBusProducerHandler` | `send_batch()` | `messages` | `list[tuple]` | `Sequence[ModelProducerMessage]` |

**Migration Required - Return Types:**

```python
# Before (v0.4.x and earlier) - untyped dict access:
health = await handler.health_check()
if health.get("healthy"):
    latency = health.get("latency_ms", 0)

# After (v0.5.0+) - typed model access:
health = await handler.health_check()
if health.healthy:
    latency = health.latency_ms  # IDE autocomplete, type checking
```

**Migration Required - Input Parameters:**

```python
# Before (v0.4.x and earlier) - untyped inputs:
embeddings = [
    {"id": "doc_001", "vector": [...], "metadata": {"page": 1}},
    {"id": "doc_002", "vector": [...], "metadata": {"page": 2}},
]
await handler.store_embeddings_batch(embeddings=embeddings, index_name="docs")

# After (v0.5.0+) - typed model inputs:
from omnibase_core.models.vector import ModelEmbedding

embeddings = [
    ModelEmbedding(id="doc_001", vector=[...], metadata={"page": 1}),
    ModelEmbedding(id="doc_002", vector=[...], metadata={"page": 2}),
]
await handler.store_embeddings_batch(embeddings=embeddings, index_name="docs")
```

```python
# Before (v0.4.x and earlier) - untyped filter dict:
results = await handler.query_similar(
    query_vector=query_embedding,
    filter_metadata={"field": "category", "operator": "eq", "value": "tech"},
)

# After (v0.5.0+) - typed filter model:
from omnibase_core.models.vector import ModelVectorMetadataFilter

filter_config = ModelVectorMetadataFilter(
    field="category",
    operator="eq",
    value="tech",
)
results = await handler.query_similar(
    query_vector=query_embedding,
    filter_metadata=filter_config,
)
```

#### Producer Handler `send_batch()` Signature Change (OMN-710)

The `send_batch()` method now accepts a `Sequence[ModelProducerMessage]` instead of raw tuples or dictionaries.

**Migration Required:**

```python
# Before (v0.4.x and earlier) - raw tuples:
await producer.send_batch([
    ("topic", b"value1", b"key1"),
    ("topic", b"value2", b"key2"),
])

# After (v0.5.0+) - typed ModelProducerMessage:
from omnibase_core.models.event_bus import ModelProducerMessage

messages = [
    ModelProducerMessage(topic="topic", value=b"value1", key=b"key1"),
    ModelProducerMessage(topic="topic", value=b"value2", key=b"key2"),
]
await producer.send_batch(messages)
```

**Rationale:**
- Typed messages enable IDE autocomplete and static type checking
- `ModelProducerMessage` supports optional `headers` and `partition` fields
- Consistent with the typed-dynamic pattern used across all handler protocols

#### Vector Store Handler `initialize()` Signature Change (OMN-710)

The `initialize()` method now accepts a `ModelVectorConnectionConfig` instead of keyword arguments.

**Migration Required:**

```python
# Before (v0.4.x and earlier) - keyword arguments:
await handler.initialize(
    url="http://localhost:6333",
    api_key="secret-key",
    timeout=30.0,
)

# After (v0.5.0+) - typed configuration model:
from omnibase_core.models.vector import ModelVectorConnectionConfig

config = ModelVectorConnectionConfig(
    url="http://localhost:6333",
    api_key="secret-key",
    timeout=30.0,
)
await handler.initialize(config)
```

**Rationale:**
- Configuration validation happens at model construction time
- Clear documentation of available configuration options via model fields
- Enables serialization/deserialization of configuration for persistence

#### Graph Database Handler `traverse()` Filter Parameter (OMN-710)

The `traverse()` method now accepts an optional `ModelGraphTraversalFilters` parameter instead of inline filter kwargs.

**Migration Required:**

```python
# Before (v0.4.x and earlier) - inline filters:
result = await handler.traverse(
    start_node_id=node_id,
    max_depth=2,
    node_labels=["Person"],
    node_properties={"active": True},
)

# After (v0.5.0+) - typed filter model:
from omnibase_core.models.graph import ModelGraphTraversalFilters

filters = ModelGraphTraversalFilters(
    node_labels=["Person"],
    node_properties={"active": True},
)
result = await handler.traverse(
    start_node_id=node_id,
    max_depth=2,
    filters=filters,
)
```

### Added

#### Handler Contract Factory (OMN-1120)
- **HandlerContractFactory**: Factory class for creating default handler contracts based on handler type category
  - Template-based approach using YAML files for safe, production-ready defaults
  - Supports COMPUTE, EFFECT, and NONDETERMINISTIC_COMPUTE handler types
  - Template caching for performance with deep copy protection
  - Semantic version parsing with full semver support (prerelease, build metadata)
- **ProtocolHandlerContractFactory**: Protocol defining the factory interface
  - `get_default()`: Create contracts with type-safe defaults
  - `available_types()`: Discover supported handler categories
- **get_default_handler_contract()**: Convenience function using cached singleton factory
- **YAML Templates**: Default contract templates in `contracts/defaults/`
  - `default_compute_handler.yaml`: Pure computation, no I/O
  - `default_effect_handler.yaml`: Side-effecting operations with retry policies
  - `default_nondeterministic_compute_handler.yaml`: AI/LLM handlers with extended timeouts
- **Template Exceptions**: New exception types for template operations
  - `TemplateError`: Base class for template-related errors
  - `TemplateNotFoundError`: Raised when template file is missing
  - `TemplateParseError`: Raised when YAML parsing fails
- **Test Coverage**: 1000+ lines of comprehensive tests
  - Version parsing validation (semver compliance)
  - Template caching and isolation tests
  - Error handling coverage

## [0.6.1] - 2026-01-26

### Added

- `ProtocolPatternExtractor` protocol for pattern extraction abstraction [OMN-1580]
  - `extract_patterns()` - Extract patterns from session data
  - Supports 4 pattern kinds: FILE_ACCESS, ERROR, ARCHITECTURE, TOOL_USAGE
  - Uses typed `ModelPatternExtractionInput` and `ModelPatternExtractionOutput` from Core
  - Includes pattern filtering by kind, confidence thresholds, and time windows
  - Structured error surface (warnings/errors in output, not exceptions)

### Changed

- Bumped `omnibase-core` dependency to >=0.9.6 for pattern extraction models

## [0.6.0] - 2026-01-25

### Added
- `ProtocolIntentGraph` protocol for intent graph persistence abstraction [OMN-1479]
  - `store_intent()` - Store intent classification to graph database
  - `get_session_intents()` - Query intents for a session
  - `health_check()` - Health check for graph connectivity
- New `protocols/intelligence/` domain with intent-related protocols
- Comprehensive test suite for ProtocolIntentGraph (20+ tests)

### Changed
- Bumped `omnibase-core` dependency to >=0.9.4 for intent event models

## [0.5.0] - 2026-01-25

### Added
- `ProtocolIntentClassifier` protocol for intent classification abstraction [OMN-1478]
  - `classify()` - Classify user prompt into intent category
  - `get_supported_intents()` - List available intent types
  - `validate_intent()` - Validate intent classification result
- New `protocols/intelligence/` domain for intelligence-related protocols

### Changed
- Bumped `omnibase-core` dependency to >=0.9.3 for intent models

## [0.4.0] - 2025-12-15

### Added

#### Generic Registry Protocols (OMN-845)
- **ProtocolRegistryBase[K, V]**: Generic registry protocol with type-safe CRUD operations
  - Generic key (K) and value (V) type parameters for compile-time type safety
  - Core operations: `register()`, `unregister()`, `get()`, `contains()`, `list_all()`, `clear()`
  - Immutable key enforcement with frozen validation
  - Comprehensive error handling with `RegistryError` for duplicate/missing keys
- **ProtocolVersionedRegistry[K, V]**: Versioned registry protocol extending `ProtocolRegistryBase[K, V]`
  - Semantic version tracking with `ModelSemVer` integration
  - Version-aware operations: `register_version()`, `get_version()`, `get_all_versions()`
  - Latest version resolution with `get_latest()` and `get_latest_version()`
  - Version range queries and compatibility checking
- **Test Coverage**: 95%+ test coverage across 600+ lines of comprehensive tests
  - Property-based testing with Hypothesis for edge cases
  - Thread-safety validation tests
  - Error handling and validation tests
  - Integration tests for real-world usage patterns

#### Documentation
- **IMPLEMENTATION-EXAMPLES.md** (1090 lines): Comprehensive guide showing how to implement protocols in `omnibase_infra`
  - `ProtocolEventBusProvider` implementation examples (minimal and full with caching)
  - `ProtocolComputeNode` implementation examples (JSON transform, vectorization)
  - `ProtocolHandler` implementation examples (HTTP, PostgreSQL with circuit breaker)
  - Implementation checklist covering protocol compliance, type safety, and testing
- **docs/protocols/PROTOCOL_REGISTRY.md**: Complete API reference for generic registry protocols
  - Type parameter guidelines and best practices
  - Error handling patterns and recovery strategies
  - Usage examples for common registry use cases
  - Integration with existing Core implementations

#### Test Infrastructure
- **Integration Test Structure**: New `tests/integration/` directory with comprehensive fixtures and 21 sample integration tests
- **Proper Test Doubles**: Replaced `MagicMock` with typed test doubles (`MockEventBus`, `MockEventBusProvider`, `MockComputeNode`) for better type safety
- **pytest Markers**: Added `integration` and `slow` markers for selective test execution

#### Protocol Enhancements
- **Timeout Parameters**: Added `timeout_seconds: float = 30.0` parameter to 20+ async cleanup methods across protocols:
  - Event bus: `close_all()`, `close()`, `stop()`
  - Handlers: `shutdown()`
  - Networking: `close()`, `close_consumer()`, `close_client()`
  - Container: `close_connection()`, `disconnect()`
  - Storage: `disconnect()`

### Changed

#### Protocol Refactoring (OMN-845)
- **ProtocolServiceRegistry**: Refactored to extend `ProtocolRegistryBase[str, Any]`
  - Maintains backward compatibility with existing consumers
  - Inherits type-safe CRUD operations from base protocol
  - Simplified implementation by delegating to base protocol methods
- **ProtocolWorkflowNodeRegistry**: Refactored to extend `ProtocolRegistryBase[str, ProtocolWorkflowNode]`
  - Type-safe node storage with `ProtocolWorkflowNode` value type
  - Workflow-specific node management operations
  - Enhanced type checking for node registration
- **ProtocolWorkflowReducer**: Enhanced with versioned state management
  - Version tracking for reducer state transitions
  - Backward-compatible state access methods
  - Improved debugging and auditing capabilities

#### Code Quality
- **Sorted `__all__` Exports**: Alphabetically sorted all `__all__` lists across 27 files for RUF022 compliance
- **ARG002 Compliance**: Fixed unused argument warnings in test files with underscore prefix pattern
- **Removed Unused noqa**: Cleaned up unnecessary `noqa: E402` comments

### Fixed

#### Protocol Compliance
- **generate_compliance_report Default**: Fixed default value to `output_format: str = "text"` to match docstring documentation
- **ClassVar Usage**: Fixed incorrect `ClassVar` usage in test mocks; extracted `MockEffectInput` and `MockEffectOutput` to module level

## [0.3.0] - 2025-12-04

### Added

#### Node Protocol Tests (1,883+ lines)
- **Comprehensive Test Suite**: 7 new test files covering all core node protocols
  - `test_compute.py`: Compute node protocol validation (367 lines)
  - `test_effect.py`: Effect node protocol validation (316 lines)
  - `test_orchestrator.py`: Orchestrator node protocol validation (361 lines)
  - `test_reducer.py`: Reducer node protocol validation (298 lines)
  - `test_protocol_handler.py`: Handler protocol validation (271 lines)
  - `test_handler_registry.py`: Registry protocol validation (279 lines)
  - `test_event_bus_provider.py`: Event bus provider validation (355 lines)
- **Protocol Compliance Patterns**: Tests validate runtime checkability, isinstance checks, method signatures, and inheritance

#### Validation Suite
- **3 Standalone Validators** (Python stdlib only):
  - `validate_naming_patterns.py`: Protocol/Error naming, `@runtime_checkable` decorator
  - `validate_namespace_isolation.py`: No Infra imports, no Pydantic models
  - `validate_architecture.py`: Domain cohesion (max 15 protocols per file)
- **Unified Runner**: `run_all_validations.py` with JSON output and CI integration
- **Pre-commit Integration**: Validators run automatically on commit

#### Documentation
- **EVENT-BUS.md** (1,464 lines): Comprehensive event bus API reference with 18+ protocol descriptions
- **WORKFLOW-ORCHESTRATION.md** (1,305 lines): Workflow orchestration API reference
- **Error Handling Examples**: Extensive coverage of SPI exception hierarchy usage patterns

### Changed

#### Event Bus Layer Separation (Critical Architecture Fix)
- **Removed Duplicate Protocols**: Deleted `ProtocolEventBus`, `ProtocolEventBusHeaders`, `ProtocolKafkaEventBusAdapter` from SPI (belong in Core)
- **Renamed Provider**: `ProtocolEventBusInstanceProvider` → `ProtocolEventBusProvider` (factory pattern)
- **Clean Layer Boundaries**: SPI now correctly depends only on Core, never on Infra

#### Protocol Count
- **176+ Protocols**: Across 22 domains with proper `@runtime_checkable` decorators

### Fixed

#### Validation Warnings
- **274 Warnings Fixed** (OMN-375): Resolved all validation warnings across the codebase
- **Duplicate Protocol**: Removed duplicate `ProtocolEventBusAgentStatus` definition
- **Namespace Isolation**: Fixed imports to ensure no Infra dependencies

## [0.2.0] - 2025-10-30

### Added

#### New Protocols (9 protocols)
- **ProtocolContainer** - Generic value container protocol with metadata support (Issue #1)
- **ProtocolServiceResolver** - Service resolution interface for dependency injection
- **ProtocolContract** - Full contract interface with versioning and serialization (Issue #3)
- **ProtocolOnexError** - Standardized error object protocol with categories and context (Issue #4)
- **ProtocolOrchestratorNode** - Node-specific protocol for workflow coordination (Issue #8)
- **ProtocolReducerNode** - Node-specific protocol for data aggregation (Issue #8)
- **ProtocolEffectNode** - Node-specific protocol for side-effecting operations (Issue #8)
- **ProtocolComputeNode** - Node-specific protocol for pure transformations (Issue #8)
- **ProtocolEnvelope** - Alias for ProtocolOnexEnvelope for naming consistency (Issue #5)
- **ProtocolEventEnvelope**: Generic envelope for breaking circular dependencies between Core and SPI
- **ProtocolSecurityValidator**: Security validation protocol for input/output sanitization
- **ProtocolSecurityContext**: Security context protocol for authentication/authorization
- **ProtocolSecurityAuditor**: Security audit logging protocol
- **ProtocolRateLimiter**: Rate limiting protocol for API protection
- **ProtocolCircuitBreaker**: Circuit breaker pattern for fault tolerance

#### Testing & Documentation
- **Comprehensive Tests** - 46 tests covering all new protocols (100% pass rate)
- **Documentation Updates** - API reference documentation for all new protocols
- **SPI Validation** - All new protocols validated for purity (0 violations)

### Changed

- **Protocol Count** - Increased from 165 to 176 protocols (+11)
- **Container Domain** - Updated from 21 to 14 protocols with generic containers
- **ONEX Domain** - Added 4 node-specific protocols for type-safe node execution
- **Type Definitions** - Expanded to 14 comprehensive type modules
- **Async Compliance**: Made `get_metrics()` and `get_summary()` methods async for SPI compliance

### Fixed

- **Protocol Import Consistency** - Standardized to use `typing.Protocol` instead of `typing_extensions`
- **Type Checking Issues** - Removed unused type ignore comments for mypy compliance

## [0.1.1] - 2025-10-23

### Added

- **Initial Protocol Scaffold**: Core SPI protocols and documentation structure
- **README Enhancement**: Added badges and open source information

### Fixed

- **Formatter Issues**: Prevented formatter issues with `.git` directory exclusion
- **Review Feedback**: Addressed Claude bot review feedback

## [0.1.0] - 2025-10-19

### Added

- **Complete Documentation Rebuild** - Comprehensive API reference with 165 protocols across 22 domains
- **MIT License** - Open source licensing for community use
- **Badge System** - Repository status indicators for license, Python version, code style, and more
- **Pre-commit Hooks** - Enhanced SPI-specific validation with .git directory exclusion
- **Protocol Type Safety** - Improved type definitions with UUID types for better type safety
- **Memory Protocols Guide** - Comprehensive memory system implementation patterns
- **Protocol Composition Patterns** - Advanced protocol design patterns and selection guide
- **Node Templates** - ONEX 4-node architecture templates
- **Standards Documentation** - Code quality guidelines and best practices
- **Link Validation Script** - Automated markdown link checking for documentation integrity

### Changed

- **Repository Structure** - Complete documentation reorganization and consolidation
- **Documentation Links** - Fixed all 137 markdown links for perfect navigation
- **Integration Guide** - Merged into comprehensive developer guide
- **Memory Guide** - Moved to examples directory for better categorization
- **Pre-commit Configuration** - Added .git directory exclusion to prevent formatter issues

### Removed

- **Duplicate Documentation** - Consolidated integration guide into developer guide
- **Empty Directories** - Cleaned up unused guides and integration directories
- **Broken Links** - Fixed all 77 broken markdown links
- **Placeholder Content** - Replaced template placeholders with real protocol references

### Fixed

- **Relative Path Issues** - Added proper `../` prefixes for cross-directory links
- **Non-existent File References** - Removed links to files that don't exist
- **Template Placeholders** - Replaced placeholder links with actual protocol references
- **Validation Directory** - Updated references to non-existent example files
- **Documentation Navigation** - All 137 links now work perfectly

---

## Protocol Statistics

| Version | Total Protocols | Test Coverage | Validation Status |
|---------|-----------------|---------------|-------------------|
| 0.6.1   | 183+            | 345+ tests    | All passing       |
| 0.6.0   | 182+            | 340+ tests    | All passing       |
| 0.5.0   | 180+            | 320+ tests    | All passing       |
| 0.4.0   | 178+            | 300+ tests    | All passing       |
| 0.3.0   | 176+            | 268 tests     | All passing       |
| 0.2.0   | 176             | 210 tests     | All passing       |
| 0.1.1   | 165             | Basic         | All passing       |
| 0.1.0   | 165             | Initial       | All passing       |

## Links

- [omnibase_spi on GitHub](https://github.com/OmniNode-ai/omnibase_spi)
- [omnibase_core](https://github.com/OmniNode-ai/omnibase_core)
- [ONEX Documentation](https://docs.omninode.ai)

---

**Legend:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes
