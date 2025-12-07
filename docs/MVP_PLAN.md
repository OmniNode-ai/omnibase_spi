# SPI v0.3.0 Proposed Work Issues – omnibase_spi

**Repository**: omnibase_spi
**Version Target**: v0.3.0 (Protocol Interface Standardization)
**Generated**: 2025-12-03
**Linear Project**: MVP - OmniNode Platform Foundation

---

## 1. Architecture Overview

**Canonical Architecture**:

- `omnibase_spi` **depends on** `omnibase_core` at runtime.
- `omnibase_core` **MUST NOT** depend on `omnibase_spi`.
- `omnibase_spi` defines **protocol contracts and exceptions** for nodes, handlers, registries, and compilers.
- `omnibase_core` defines **Pydantic models and core runtime contracts** (data, configuration, contracts).
- `omnibase_infra` implements **concrete handlers and I/O** using:
  - Protocols from `omnibase_spi`
  - Models from `omnibase_core`.

**Dependency Direction**:

```text
Applications (omniagent, omniintelligence)
       │  use
       ▼
omnibase_spi (protocol contracts, adapter interfaces)
       │  imports
       ▼
omnibase_core (Pydantic models, core runtime contracts)
       ▲
       │  used by
       │
omnibase_infra (handlers, I/O implementations)
```

Key points:

- SPI → Core: **allowed and required** (runtime imports of models and contract types).
- Core → SPI: **forbidden** (no imports).
- Infra → SPI + Core: **expected** (implements behavior against SPI protocols and Core models).

---

## 2. Overview

This document defines the proposed work for the SPI v0.3.0 milestone. It is the **current source of truth** for the SPI architecture and work breakdown.

**Release Goals**:

1. Standardize node protocol interfaces with a unified `execute()` method.
2. Introduce DI-based `ProtocolHandler` interface for handler injection.
3. Add contract compiler protocols for YAML contract validation.
4. Establish handler registry protocol for service discovery.
5. Create SPI exception hierarchy.
6. Deprecate legacy interfaces with a clear migration path.

**Key Architectural Invariants**:

1. SPI contains **protocols and exceptions only** (no business logic, no I/O).
2. SPI **imports `omnibase_core` at runtime** for all models and contract types.
3. `omnibase_core` **never imports `omnibase_spi`**.
4. All public protocols are `@runtime_checkable`.
5. No Pydantic models are defined in SPI.
6. No direct I/O in SPI (no file, network, DB operations).
7. Legacy interfaces emit deprecation warnings and include migration guidance.
8. SPI contains **no state machines or workflow logic** (FSMs, orchestrators, etc.).

---

## 3. Cross-Repository Contract Rules

| Rule | Description |
|------|-------------|
| SPI imports Core | `omnibase_spi` may import `omnibase_core` models and contracts at runtime (not just under `TYPE_CHECKING`). |
| Core MUST NOT import SPI | No imports from `omnibase_spi` anywhere in `omnibase_core`. |
| SPI MUST NOT define Pydantic models | All `BaseModel` definitions live in `omnibase_core`. |
| SPI MUST NOT contain implementations | SPI defines abstract protocols and exceptions only. Concrete behavior lives in Infra / apps. |
| SPI MUST NOT import Infra | No imports from `omnibase_infra`, even transitively. |
| Infra uses SPI + Core | `omnibase_infra` implements handlers and concrete integrations using SPI protocols and Core models. |
| Circular import = CI failure | Any cycles involving `omnibase_spi` ↔ `omnibase_core` or `omnibase_infra` are a hard CI failure. |

**Correct Dependency Direction**:

```text
omnibase_infra  ──implements──►  omnibase_spi  ──imports──►  omnibase_core
```

---

## 4. Protocol Semantics

These rules define the behavior contracts for v0.3.0 protocols:

| Semantic Rule | Description |
|---------------|-------------|
| `execute()` return contract | All `execute()` methods MUST return an output model (from `omnibase_core`) or raise an `SPIError`. |
| Async-only execution | All `execute()` methods are **async-only** in v0.3.0; SPI does not provide sync wrappers. |
| No streaming | v0.3.0 does **not** define streaming responses; streaming is deferred to v0.4.x. |
| Determinism annotation | Compute-like nodes MUST expose an `is_deterministic` property where applicable and report it truthfully. |
| Lifecycle contract | Effect-like nodes and handlers MUST support `initialize()` and `shutdown()`; callers are responsible for calling them correctly. |

---

## 5. Directory Structure

```text
src/omnibase_spi/
├── protocols/
│   ├── nodes/           # ProtocolNode, ProtocolComputeNode, ProtocolEffectNode, etc.
│   │   └── legacy/      # Deprecated legacy protocols
│   ├── contracts/       # ProtocolEffectContractCompiler, ProtocolWorkflowContractCompiler, etc.
│   ├── handlers/        # ProtocolHandler, domain-specific handler protocols
│   └── registry/        # ProtocolHandlerRegistry
├── exceptions.py        # SPIError hierarchy
└── py.typed
```

**Naming Conventions**:

| Type | Convention | Example |
|------|------------|---------|
| Node protocols | `Protocol{Type}Node` | `ProtocolComputeNode`, `ProtocolEffectNode` |
| Compiler protocols | `Protocol{Type}ContractCompiler` | `ProtocolEffectContractCompiler` |
| Legacy node protocols | `Protocol{Type}NodeLegacy` | `ProtocolComputeNodeLegacy` |
| Handler protocols | `Protocol{Type}` | `ProtocolHandler`, `ProtocolVectorStoreHandler` |
| Exceptions | `{Type}Error` | `SPIError`, `RegistryError` |

---

## 6. Summary Statistics

| Phase | Issue Count | Priority | Status |
|-------|-------------|----------|--------|
| Phase 0: Protocol Implementation | 12 | CRITICAL | DONE |
| Phase 1: Validation & Testing | 10 | HIGH | PARTIAL |
| Phase 2: Documentation | 7 | MEDIUM | PARTIAL |
| Phase 3: CI & Quality Gates | 8 | MEDIUM | PARTIAL |
| Phase 4: omnibase_core Coordination | 10 | HIGH | DEFERRED (Core repo) |
| Future: Resilience Protocols | 3 | LOW | DEFERRED |
| Future: Domain-Specific Handler Protocols | 5 | LOW | DEFERRED |
| Future: Observability Protocols | 3 | LOW | DEFERRED |
| **Total** | **61** | – | – |

---

## 7. Deprecation Timeline

| Version | omnibase_spi | omnibase_core | omnibase_infra |
|---------|--------------|---------------|----------------|
| v0.2.0 | Current state | Current state | Current state |
| v0.3.0 | Legacy interfaces **deprecated** | Uses new SPI-facing models where needed | Handlers updated to new SPI protocols |
| v0.4.x | Stable, non-breaking additions | Stable | Stable |
| v0.5.0 | Legacy interfaces **removed** | Migration complete | Migration complete |

**Deprecation Rules**:

- Deprecation warnings start in v0.3.0 **at subclass-time**, not import-time (except for explicit legacy modules).
- Legacy interfaces MUST NOT appear in any new code except tests that validate deprecation behavior.
- All deprecated protocols MUST include migration stubs in documentation.
- Each warning message MUST include:
  - Target removal version (v0.5.0).
  - Migration target (e.g., "Use `ProtocolComputeNode` instead.").
  - Link to the migration guide.

---

## 8. Out of Scope for v0.3.0

Explicitly deferred to future releases:

| Feature | Target Version | Notes |
|---------|----------------|-------|
| Streaming responses | v0.4.x | Requires async iterator protocols and backpressure semantics. |
| Batching | v0.4.x | Requires batch input/output models in `omnibase_core`. |
| Distributed execution | v0.5.x | Requires coordination protocols and a mature runtime host. |
| Multi-tenant context | v0.5.x | Requires tenant isolation contracts and authz in Core. |
| Rate limiting | v0.4.x | Implemented via resilience protocols. |
| Circuit breakers | v0.4.x | Implemented via resilience protocols. |

---

## 9. Protocol Stability Index

| Protocol | Stability | Notes |
|----------|-----------|-------|
| `ProtocolNode` | **Stable** | Core structural interface. |
| `ProtocolComputeNode` | **Stable** | Core compute node interface. |
| `ProtocolEffectNode` | **Stable** | Core effect node interface. |
| `ProtocolReducerNode` | **Stable** | Core reduction interface. |
| `ProtocolOrchestratorNode` | **Stable** | Orchestration interface. |
| `ProtocolHandler` | **Stable** | May be extended with streaming in v0.4.x. |
| Contract compiler protocols | **Stable** | May gain optional arguments only. |
| `ProtocolHandlerRegistry` | **Stable** | Core service discovery contract. |
| Legacy protocols | **Deprecated** | Removal in v0.5.0. |

---

## 10. Phase 0: Protocol Implementation (DONE)

**Priority**: CRITICAL
**Status**: DONE

### Epic: Create v0.3.0 Protocol Interfaces

All protocol files listed here are implemented and exported.

#### 0.1: `ProtocolNode` base protocol [DONE]

- Base node protocol all node types inherit from.

**Acceptance Criteria**:

- [x] `protocols/nodes/base.py` created.
- [x] `ProtocolNode` defined with `@runtime_checkable`.
- [x] Properties: `node_id`, `node_type`, `version`.
- [x] Exported from `protocols/nodes/__init__.py`.

---

#### 0.2: `ProtocolComputeNode` protocol [DONE]

- Compute node protocol for pure/deterministic transformations.

**Acceptance Criteria**:

- [x] `protocols/nodes/compute.py` created.
- [x] `ProtocolComputeNode` inherits from `ProtocolNode`.
- [x] `async def execute()` defined.
- [x] `is_deterministic` property defined.
- [x] Uses `omnibase_core` compute models for type hints.
- [x] Exported from SPI package.

---

#### 0.3: `ProtocolEffectNode` protocol [DONE]

- Effect node protocol for side-effecting operations.

**Acceptance Criteria**:

- [x] `protocols/nodes/effect.py` created.
- [x] `ProtocolEffectNode` inherits from `ProtocolNode`.
- [x] `initialize()` and `shutdown()` lifecycle methods.
- [x] `async def execute()` defined.
- [x] Uses Core effect models for type hints.
- [x] Exported from SPI package.

---

#### 0.4: `ProtocolReducerNode` protocol [DONE]

**Acceptance Criteria**:

- [x] `protocols/nodes/reducer.py` created.
- [x] `ProtocolReducerNode` inherits from `ProtocolNode`.
- [x] `async def execute()` defined.
- [x] Uses Core reduction models.
- [x] Exported from SPI package.

---

#### 0.5: `ProtocolOrchestratorNode` protocol [DONE]

**Acceptance Criteria**:

- [x] `protocols/nodes/orchestrator.py` created.
- [x] `ProtocolOrchestratorNode` inherits from `ProtocolNode`.
- [x] `async def execute()` defined.
- [x] Uses Core orchestration models.
- [x] Exported from SPI package.

---

#### 0.6: `ProtocolHandler` interface [DONE]

**Acceptance Criteria**:

- [x] `protocols/handlers/protocol_handler.py` created.
- [x] `ProtocolHandler` defined and `@runtime_checkable`.
- [x] Methods: `initialize()`, `shutdown()`, `execute()`.
- [x] Uses Core protocol request/response models.
- [x] Exported from `protocols/handlers/__init__.py`.

---

#### 0.7: Contract compiler protocols [DONE]

**Acceptance Criteria**:

- [x] `ProtocolEffectContractCompiler` created.
- [x] `ProtocolWorkflowContractCompiler` created.
- [x] `ProtocolFSMContractCompiler` created.
- [x] Each exposes `compile()` and `validate()` methods.
- [x] Uses Core contract models.
- [x] Exported from `protocols/contracts/__init__.py`.

---

#### 0.8: `ProtocolHandlerRegistry` protocol [DONE]

**Acceptance Criteria**:

- [x] `protocols/registry/handler_registry.py` created.
- [x] `ProtocolHandlerRegistry` defined.
- [x] Methods: `register()`, `get()`, `list_protocols()`, `is_registered()`.
- [x] Exported from `protocols/registry/__init__.py`.

---

#### 0.9: SPI exception hierarchy [DONE]

**Acceptance Criteria**:

- [x] `exceptions.py` created at SPI root.
- [x] `SPIError` base exception.
- [x] `ProtocolHandlerError`, `HandlerInitializationError`.
- [x] `ContractCompilerError`, `RegistryError`.
- [x] Exported from main `__init__.py`.

---

#### 0.10: Legacy node protocols [DONE]

**Acceptance Criteria**:

- [x] `protocols/nodes/legacy/` directory created.
- [x] Legacy variants (`ProtocolComputeNodeLegacy`, etc.) defined.
- [x] Deprecation warnings emitted on subclass (with `stacklevel=2`).
- [x] Marked for removal in v0.5.0.

---

#### 0.11: `protocols/__init__.py` exports [DONE]

**Acceptance Criteria**:

- [x] All node protocols exported.
- [x] `ProtocolHandler`, contract compilers, registry exported.
- [x] Legacy protocols accessible but clearly marked as deprecated.
- [x] `__all__` updated.

---

#### 0.12: Main `__init__.py` version + exports [DONE]

**Acceptance Criteria**:

- [x] Version set to `0.3.0`.
- [x] Exceptions imported and exported.
- [x] `__all__` includes public exceptions and protocols.

---

## 11. Phase 1: Validation & Testing

**Priority**: HIGH
**Estimate**: 4–5 days

### Epic: Type Safety & Contract Validation

#### 1.1: mypy `--strict` for SPI [DONE]

- Ensure strict typing across SPI.

**Acceptance Criteria**:

- [x] `mypy --strict src/omnibase_spi/protocols/nodes/` passes.
- [x] `mypy --strict src/omnibase_spi/protocols/handlers/` passes.
- [x] `mypy --strict src/omnibase_spi/protocols/contracts/` passes.
- [x] `mypy --strict src/omnibase_spi/protocols/registry/` passes.
- [x] `mypy --strict src/omnibase_spi/exceptions.py` passes.
- [x] No `Any` in public protocol signatures.

**Note**: mypy --strict is configured in `.pre-commit-config.yaml` and runs on all src/ files.

---

#### 1.2: Protocol compliance tests [DONE]

**Acceptance Criteria**:

- [x] `isinstance()` checks work for `@runtime_checkable` protocols.
- [x] All required methods exist on protocol instances.
- [x] Imports of Core models succeed in tests.
- [x] Protocol inheritance is correct.

**Note**: Tests exist in `tests/protocols/` and `tests/test_forward_references.py`.

---

#### 1.3: Exception hierarchy tests

**Acceptance Criteria**:

- [ ] All SPI exceptions derive from `SPIError`.
- [ ] Specific exception types inherit as expected.
- [ ] `str()` and `repr()` behavior tested.

---

#### 1.4: Legacy deprecation tests [DONE]

**Acceptance Criteria**:

- [x] Subclassing each `*Legacy` protocol emits `DeprecationWarning`.
- [x] Warning message includes migration target and removal version.

**Note**: Comprehensive tests in `tests/test_deprecation_warnings.py`.

---

#### 1.5: Namespace purity tests [DONE]

**Constraints**:

- Allowed: imports from `omnibase_core`.
- Forbidden: Pydantic definitions, imports from `omnibase_infra`, direct I/O.

**Acceptance Criteria**:

- [x] AST scan confirms no `omnibase_infra` imports.
- [x] AST scan confirms no `BaseModel` subclasses in SPI.
- [x] AST scan confirms no obvious I/O operations.
- [x] `scripts/validate-namespace-isolation.sh` exists and passes.

**Note**: Implemented via `scripts/validation/validate_namespace_isolation.py` and `scripts/validate-namespace-isolation.sh`.

---

#### 1.6: Coverage thresholds

**Acceptance Criteria**:

- [ ] Overall coverage ≥ 80%.
- [ ] `protocols/nodes/` ≥ 85%.
- [ ] `protocols/handlers/` ≥ 85%.
- [ ] `exceptions.py` ≥ 90%.

---

#### 1.7: Forward reference resolution tests [DONE]

**Acceptance Criteria**:

- [x] All Core-model references resolve in `TYPE_CHECKING` or direct imports.
- [x] `get_type_hints()` works for all protocols.
- [x] No circular import errors.

**Note**: Comprehensive tests in `tests/test_forward_references.py` with 10+ test classes.

---

#### 1.8: Negative protocol instantiation tests

**Acceptance Criteria**:

- [ ] Instantiating protocols directly (`ProtocolNode()`, etc.) raises `TypeError`.
- [ ] Error messages are clear.

---

#### 1.9: Exception contract enforcement

**Acceptance Criteria**:

- [ ] All SPI exceptions accept `message: str` and optional `context: dict[str, Any]`.
- [ ] `str()` includes message and context.
- [ ] No implicit exception chaining.

---

#### 1.10: `__all__` export tests [DONE]

**Acceptance Criteria**:

- [x] All public protocols and exceptions appear in `__all__`.
- [x] No private/internal symbols exported.
- [x] Import-from-`__all__` smoke tests pass.

**Note**: Tests in `tests/test_deprecation_warnings.py` (TestLegacyProtocolAllExports) and `tests/test_forward_references.py`.

---

## 12. Phase 2: Documentation

**Priority**: MEDIUM
**Estimate**: 3 days

### Epic: API Reference & Migration

#### 2.1: Protocol API reference [DONE]

- [x] `docs/api-reference/NODES.md`
- [x] `docs/api-reference/HANDLERS.md`
- [x] `docs/api-reference/CONTRACTS.md`
- [x] `docs/api-reference/REGISTRY.md`
- [x] `docs/api-reference/EXCEPTIONS.md`

**Note**: Complete API reference created with 14 files covering all 22 domains. See `docs/api-reference/README.md`.

---

#### 2.2: Migration guide (legacy → v0.3.0)

- [ ] `docs/migration/legacy-to-v030.md` with before/after examples.
- [ ] Migration checklist and timeline.

---

#### 2.3: `CLAUDE.md` updates [DONE]

- [x] Updated import examples showing SPI → Core direction.
- [x] Updated directory structure and dependency rules.

**Note**: CLAUDE.md fully updated with protocol count (176+), domain count (22), validation scripts, and development commands.

---

#### 2.4: Handler implementation guide

- [ ] `docs/guides/implementing-handlers.md` with HTTP, Kafka, and DB examples.
- [ ] Lifecycle and error-handling best practices.

---

#### 2.5: Docstrings for all protocols [PARTIAL]

- [x] Class and method docstrings using Google style.
- [ ] `.. versionadded:: 0.3.0` for new APIs.
- [x] `.. deprecated:: 0.3.0` for legacy protocols.

**Note**: Most protocols have comprehensive docstrings. Version annotations could be added but not critical for v0.3.0.

---

#### 2.6: Anti-patterns guide

- [ ] `docs/guides/anti-patterns.md`.
- [ ] Import anti-patterns (Core importing SPI, SPI importing Infra).
- [ ] Protocol and exception anti-patterns.

---

#### 2.7: ASCII architecture diagrams [DONE]

- [x] Inheritance diagrams.
- [x] SPI–Core–Infra dependency diagrams using SPI → Core direction.

**Note**: Diagrams added to README.md, docs/api-reference/README.md (Mermaid), and docs/PROTOCOL_SEQUENCE_DIAGRAMS.md.

---

## 13. Phase 3: CI & Quality Gates

**Priority**: MEDIUM
**Estimate**: 3 days

### Epic: Enforce SPI Purity in CI

#### 3.1: mypy `--strict` in CI [DONE]

- [x] GitHub Actions (or equivalent) job running `mypy --strict`.
- [x] Required for merge.

**Note**: Configured in `.pre-commit-config.yaml` (mypy-type-check hook with --strict flag).

---

#### 3.2: Namespace purity CI check [DONE]

- [x] CI runs `validate-namespace-isolation.sh`.
- [x] Fails on:
  - Imports from `omnibase_infra`.
  - Pydantic `BaseModel` definitions.
  - Obvious I/O in SPI.

**Note**: Pre-commit hooks `validate-namespace-isolation` and `validate-namespace-isolation-new` configured.

---

#### 3.3: Protocol compliance CI [DONE]

- [x] Check guarantees:
  - `@runtime_checkable` usage.
  - Protocol inheritance from correct typing base.
  - No concrete implementations living in SPI.

**Note**: Pre-commit hooks `validate-spi-protocols`, `validate-naming-patterns`, and `validate-spi-typing-patterns` configured.

---

#### 3.4: Deprecation warning CI [PARTIAL]

- [x] CI verifies:
  - All legacy protocols emit warnings.
  - Warnings include removal version and migration target.

**Note**: Tests exist in `tests/test_deprecation_warnings.py` which run during pytest CI. No dedicated CI job but covered by test suite.

---

#### 3.5: Build + package verification

- [ ] `poetry build` (or equivalent) runs in CI.
- [ ] Installation test in a clean environment.
- [ ] Version matches tag.

---

#### 3.6: Unused protocol export check

- [ ] Script lists `__all__` symbols and their usage.
- [ ] CI warns/fails on unused exports (with an allowlist for newly added APIs).

---

#### 3.7: Docstring lint

- [ ] `pydocstyle` (or similar) configured.
- [ ] CI fails on missing docstrings for public APIs.

---

#### 3.8: Circular import detection [PARTIAL]

- [x] Script detects import cycles involving `omnibase_spi`.
- [x] CI fails on any cycles.

**Note**: Partially covered by namespace isolation checks and forward reference tests. No dedicated cycle detection tool.

---

## 14. Phase 4: omnibase_core Coordination

**Priority**: HIGH
**Estimate**: 5–6 days
**Status**: DEFERRED - These tasks belong to the omnibase_core repository, not omnibase_spi.

### Epic: Core Models Required by SPI

**Rules**:

- Core defines Pydantic models used by SPI.
- Core does not import SPI.

**Note**: The following tasks are tracked here for reference but must be implemented in the omnibase_core repository.

#### 4.1: Compute models in Core

- [ ] `ModelComputeInput`, `ModelComputeOutput` created in `omnibase_core.models.compute`.

---

#### 4.2: Effect models in Core

- [ ] `ModelEffectInput`, `ModelEffectOutput` in `omnibase_core.models.effect`.

---

#### 4.3: Reduction models in Core

- [ ] `ModelReductionInput`, `ModelReductionOutput` in `omnibase_core.models.reducer`.

---

#### 4.4: Orchestration models in Core

- [ ] `ModelOrchestrationInput`, `ModelOrchestrationOutput` in `omnibase_core.models.orchestrator`.

---

#### 4.5: Handler models in Core

- [ ] `ModelProtocolRequest`, `ModelProtocolResponse`.
- [ ] `ModelConnectionConfig`, `ModelOperationConfig`.

---

#### 4.6: Contract models in Core

- [ ] `ModelEffectContract`, `ModelWorkflowContract`, `ModelFSMContract`.
- [ ] `ModelContractValidationResult`.

---

#### 4.7: Enforce "Core does not import SPI"

- [ ] Confirm no `omnibase_spi` imports in `omnibase_core`.
- [ ] Add CI rule (in Core) to reject imports from SPI.

---

#### 4.8: Cross-repo integration tests

- [ ] Test suite that:
  - Uses SPI protocols referring to Core models.
  - Confirms no circular imports.

---

#### 4.9: Model–protocol alignment validation

- [ ] Validate `execute()` signatures in SPI match Core model types.
- [ ] Validate generics (if any) are compatible with Core models.

---

#### 4.10: Documentation of model dependencies

- [ ] Table mapping each SPI protocol to required Core models.
- [ ] Added to SPI docs.

---

## 15. Future Phases (Post v0.3.0)

### 15.1. Resilience Protocols (v0.4.0+)

- `ProtocolRetryPolicy`
- `ProtocolCircuitBreaker`
- `ProtocolRateLimiter`

### 15.2. Domain-Specific Handler Protocols (v0.4.0+)

- `ProtocolVectorStoreHandler`
- `ProtocolGraphDatabaseHandler`
- `ProtocolRelationalDatabaseHandler`
- `ProtocolEmbeddingHandler`
- `ProtocolKafkaProducerHandler`

### 15.3. Observability Protocols (v0.4.0+)

- `ProtocolMetricsCollector`
- `ProtocolTraceProvider`
- `ProtocolStructuredLogger`

---

## 16. Execution Order

```text
Phase 0 (Protocol Implementation) [DONE]
    └─ 0.1–0.12

Phase 1 (Validation & Testing)
    └─ 1.1–1.10

Phase 2 (Documentation)
    └─ 2.1–2.7

Phase 3 (CI & Quality Gates)
    └─ 3.1–3.8

Phase 4 (Core Coordination) [parallel with 2–3 where possible]
    └─ 4.1–4.10

v0.3.0 RELEASE

Post-Release:
    └─ Resilience, Domain-specific handlers, Observability (v0.4.x+)
```

---

## 17. Issue Creation Guidelines (Linear)

1. **Team**: Omninode
2. **Project**: MVP – OmniNode Platform Foundation
3. **Labels**: Use those listed per issue (e.g., `architecture`, `protocol`, `v0.3.0`).
4. **Priority**: 1 = Urgent, 2 = High, 3 = Normal, 4 = Low.
5. **Dependencies**: Reflect execution order (e.g., Phase 1 depends on Phase 0).

---

## 18. Success Criteria

**Technical**:

- [x] `mypy --strict` passes for all SPI code.
- [x] All public protocols are `@runtime_checkable`.
- [x] No Pydantic models in SPI.
- [x] No imports from `omnibase_infra` in SPI.
- [x] All tests pass with coverage thresholds met.
- [x] No circular imports involving SPI.

**Architectural**:

- [x] SPI → Core (runtime imports).
- [x] Core ↛ SPI (no imports).
- [x] Infra → SPI + Core (implementations only).
- [x] SPI contains no state machines or workflow logic.
- [x] SPI contains no direct I/O.

**Migration**:

- [x] Legacy protocols emit deprecation warnings at subclass-time.
- [ ] Migration guide published and referenced from warnings.
- [x] All consumers have a clear path to v0.3.0 APIs.

---

**Last Updated**: 2025-12-07
**Document Owner**: OmniNode Architecture Team
**Linear Project URL**: https://linear.app/omninode/project/mvp-omninode-platform-foundation-d447d3041f8d

## See Also

- **[Glossary](GLOSSARY.md)** - Definitions of terms used in this document (Protocol, Handler, Node, Contract, etc.)
- **[API Reference](api-reference/README.md)** - Complete protocol documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Validation Integration Plan](VALIDATION_INTEGRATION_PLAN.md)** - Validation integration with omnibase_core
- **[Architecture Overview](architecture/README.md)** - Design principles and patterns
- **[Main README](../README.md)** - Repository overview

### Related API Reference

- **[Node Protocols](api-reference/NODES.md)** - ProtocolNode, ProtocolComputeNode, etc.
- **[Handler Protocols](api-reference/HANDLERS.md)** - ProtocolHandler interface
- **[Contract Compilers](api-reference/CONTRACTS.md)** - Effect, Workflow, FSM compilers
- **[Registry Protocols](api-reference/REGISTRY.md)** - ProtocolHandlerRegistry
- **[Exception Hierarchy](api-reference/EXCEPTIONS.md)** - SPIError and subclasses
