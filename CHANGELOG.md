## [0.15.0] - 2026-02-28

### Added
- feat(ci): add auto-tag-on-merge caller workflow (#93)
- feat(testing): protocol signature snapshot tests for SPI drift detection (#94)
- feat(lint): enable pydocstyle rules for public API docstrings (#97)
- feat(tooling): unused protocol export checker (#96)

### Fixed
_(none)_

### Changed
- chore(omnibase_spi): add AI-slop checker (Phase 2 rollout) (#104)
- ci: add tests-gate aggregator job for branch protection (#103)
- ci: add merge_group trigger to namespace-validation workflow (#102)

## v0.14.0 (2026-02-27)

### Features
- feat(protocols): export ProtocolRateLimiter and add resilience protocol tests [OMN-796] (#98)
- feat(ci): add build and package verification workflow [OMN-793]

### Bug Fixes
- fix(ci): correct merge_queue to merge_group event name
- fix(ci): add merge_queue trigger to prevent queue deadlock
- fix(ci): use uv pip install instead of bare pip in build verification

### Other Changes
_(none)_

# Changelog

All notable changes to the ONEX Service Provider Interface (omnibase_spi) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.13.0] - 2026-02-25

### Added

#### ProtocolProjectionView SPI Contract for NodeProjectionEffect Pattern (OMN-2382) #91
- **`ProtocolProjectionView`**: New `@runtime_checkable` SPI contract in `protocols/projections/` defining the view-layer interface for the `NodeProjectionEffect` pattern — supports `render(artifact_ref: str) -> object` with forward-compatible `extra="allow"` semantics

#### Event Registry, SPI Contracts, and Producer Protocols (OMN-2655) #90
- **Event registry**: New `registry/` module in `omnibase_spi` providing a typed event registry for cross-boundary event-type discovery
- **Event SPI contracts**: Frozen wire-format contracts in `contracts/events/` for event envelope, routing metadata, and emission results
- **Producer protocols**: `ProtocolEventProducer` and `ProtocolEventEmitter` in `protocols/event_bus/` defining the SPI boundary for event emission with structured error returns

### Changed

- Bumped version to 0.13.0

## [0.12.0] - 2026-02-23

### Added

#### Synchronous Effect Protocol and Node Projection Effect (OMN-2508)
- **`ProtocolEffect`**: New `@runtime_checkable` synchronous effect boundary protocol in `protocols/effects/` — defines `execute(intent: object) -> object` with `synchronous_execution: ClassVar[bool]` ordering guarantee flag
- **`ProtocolNodeProjectionEffect`**: Concrete synchronous `ProtocolEffect` implementation in `effects/` — executes node projection persistence operations with blocking semantics (bridges async storage via `asyncio.run()`)
- **`ContractProjectionResult`**: New frozen wire-format contract in `contracts/projections/` capturing projection outcome — `success`, `artifact_ref`, `schema_version`, and optional `error`; `extra="allow"` for forward compatibility
- All new protocols and contracts are re-exported at the `omnibase_spi` root level via lazy-loading map
- 586 unit tests covering protocol compliance, validator SPI005/SPI-T003 suppression, runtime `isinstance` checks, and `get_type_hints()` correctness

### Changed

- Bumped version to 0.12.0
- `omnibase-core` dependency targets `>=0.19.0`

## [0.10.0] - 2026-02-18

### Added

#### Context Enrichment Protocol and Contract (OMN-2252)
- **`ProtocolContextEnrichment`**: New `@runtime_checkable` protocol in `protocols/intelligence/` defining `enrich(prompt, context)` for pluggable context enrichment implementations
- **`ContractEnrichmentResult`**: Frozen wire-format contract in `contracts/enrichment/` capturing enrichment output — summary, token count, relevance score, and provenance metadata
- Fixed SPI012 namespace isolation validator to allow `omnibase_spi.contracts` imports inside protocol files
- 297 unit tests covering creation, immutability, field validation, and architectural guardrails

#### Delegation Output Contracts (OMN-2254)
- **`ContractDelegatedResponse`**: Unified output shape for all delegation handlers
- **`ContractDelegationAttribution`**: Model name, endpoint, latency, and confidence metadata
- **`ContractAttachment`**: File attachment envelope with content type and base64-encoded payload
- **`ContractComplianceResult`**: Quality gate pass/fail verdict with score and violation list
- All delegation contracts use `frozen=True, extra="forbid"` with validation deferred to consumers per SPI wire-format convention
- 42 unit tests covering immutability, field validation, and JSON round-trip

### Changed

- Bumped version to 0.10.0
- `omnibase-core` dependency targets `>=0.18.0`

## [0.9.0] - 2026-02-15

### Changed

- Bumped version to 0.9.0
- Updated `omnibase-core` dependency to >=0.18.0

## [0.8.0] - 2026-02-12

### Changed

#### Canonical RRH Rule Enum (OMN-2139)
- **`RRHRule` redefined**: Replaced 17-rule enum (dev-toolchain checks) with canonical 13-rule enum covering 8 validation domains: repo (10xx), environment (11xx), kafka (12xx), kubernetes (13xx), toolchain (14xx), cross-checks branch/ticket (15xx), cross-checks contract fields (16xx), repo-boundary (17xx)
- **`RRHRule` relocated**: Moved from `contracts/pipeline/enum_rrh_rule.py` to `enums/enum_rrh_rule.py`; re-exported via `omnibase_spi.contracts.pipeline` and `omnibase_spi.contracts` for backward compatibility
- Updated `omnibase-core` dependency to >=0.17.0

## [0.7.0] - 2026-02-09

### Added

#### Shared Pipeline and Validation Wire-Format Contracts (OMN-2004)
- **Shared primitives**: `ContractCheckResult` (single check outcome) and `ContractVerdict` (aggregated PASS/FAIL/QUARANTINE verdict)
- **Pipeline contracts** (14 models): Hook invocation envelope/result, node operation request/result, `ContractNodeError`, `ContractRunContext`, `ContractSessionIndex`, `ContractWorkAuthorization`, `ContractExecutionContext`, `ContractRRHResult`, `ContractCheckpoint`, `ContractRepoScope`, `ContractArtifactPointer`, `ContractAuthGateInput`
- **Pipeline enums**: `RRHRule` (17 rules), `AuthReasonCode` (12 codes)
- **Pipeline utilities**: `contract_wire_codec` (JSON/YAML serialization helpers), `contract_schema_compat` (versioning policy)
- **Validation contracts** (6 models): `ContractPatternCandidate`, `ContractValidationPlan`, `ContractValidationRun`, `ContractValidationResult`, `ContractValidationVerdict`, `ContractAttributionRecord`
- **Validation enum**: `ValidationCheck` (17 checks across 5 domains)
- All contracts are frozen, `extra=allow`, with `schema_version` field and zero `omnibase_core`/infra/omniclaude imports
- 252 unit tests covering creation, immutability, forward-compat, serialization round-trips, and architectural guardrails

#### Measurement Pipeline Wire-Format Contracts (OMN-2024)
- **Measurement enums**: `ContractEnumPipelinePhase` (5 phases), `ContractEnumResultClassification` (5 categories), `MeasurementCheck` (CHECK-MEAS-001 through 006)
- **Measurement contracts** (8 models): `ContractMeasurementContext` (correlation identity with baseline key derivation), `ContractProducer` (structured producer identity), `ContractPhaseMetrics` (primary measurement unit with sub-contracts for duration, cost, outcome, tests, and artifact pointers), `ContractMeasurementEvent` (domain envelope), `ContractAggregatedRun` (run-level rollup), `ContractPromotionGate` (per-dimension evidence), `ContractMeasuredAttribution` (attribution + measurement composition)
- Measurement contracts use `frozen=True` + `extra="forbid"` + explicit extensions field (stricter than SPI convention because measurement data feeds promotion gates)
- Cross-field validators: `mandatory_phases_succeeded <= mandatory_phases_total`, `sufficient_count <= total_count`, `delta_pct=None` when `baseline_value=0`
- Null-byte separator in `derive_baseline_key` to prevent delimiter collision
- 83 unit tests covering enum stability, frozen/forbid invariants, JSON round-trip, and validation behaviors

#### Architecture Handshake (OMN-1983)
- **Architecture handshake constraint map** (`.claude/architecture-handshake.md`): Installed naming conventions and dependency rules from `omnibase_core`
- **CI workflow** (`.github/workflows/check-handshake.yml`): Verifies handshake stays in sync with `omnibase_core` source via SHA256 hash comparison

### Fixed

- Added `ge=0` constraints to float duration and cost fields in measurement contracts: `wall_clock_ms`, `cpu_ms`, `queue_ms`, `estimated_cost_usd`, `total_duration_ms`, `total_cost_usd` (#76)
- Extended `ContractCheckResult.domain` Literal type to include `"measurement"` subsystem

### Changed

- Updated `omnibase-core` dependency to >=0.16.0
- Updated namespace isolation validator to exempt `contracts/` directory from NSI002 (Pydantic model check)

## [0.6.4] - 2026-01-30

### Changed

- **ProtocolIntentGraph semantic fix** (OMN-1729): Updated `store_intent()` to accept `ModelIntentClassificationOutput` instead of `ModelIntentClassificationInput`
  - Storage boundary now correctly accepts classification **output** (category, confidence, keywords)
  - Classification happens upstream; this protocol persists the results
  - Docstrings updated to reflect semantic change
- Updated `omnibase-core` dependency to >=0.9.11

## [0.6.3] - 2026-01-30

### Changed

- Bumped version to 0.6.3
- Updated `omnibase-core` dependency to >=0.9.10

## [0.6.2] - 2026-01-27

### Added

- **ProtocolEventPublisher semantics documentation** (OMN-1615): Codified topic override and partition_key semantics in protocol docstrings
- **Publisher Protocol Policy** in EVENT-BUS.md: Documents canonical interface rule forbidding handler-local publish protocols
- **Protocol signature tests**: 18 unit tests verifying ProtocolEventPublisher interface contract
- **SPDX header prevention hook**: Pre-commit hook to prevent SPDX license headers from being (re)introduced

### Changed

- Made ProtocolEventPublisher docstring transport-agnostic (removed Kafka-specific wording)
- Enhanced publish() method documentation with routing behavior and partition_key responsibility boundaries

### Removed

- SPDX license headers from 10 files (centralized LICENSE file is the single source of truth)

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
| 0.9.0   | 183+            | 680+ tests    | All passing       |
| 0.8.0   | 183+            | 680+ tests    | All passing       |
| 0.7.0   | 183+            | 680+ tests    | All passing       |
| 0.6.4   | 183+            | 345+ tests    | All passing       |
| 0.6.3   | 183+            | 345+ tests    | All passing       |
| 0.6.2   | 183+            | 345+ tests    | All passing       |
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
