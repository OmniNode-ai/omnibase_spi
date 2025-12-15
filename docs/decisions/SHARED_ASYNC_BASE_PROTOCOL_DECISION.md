# Decision: Shared Async Base Protocol for Registries

**Date**: 2025-12-15
**Status**: **DEFERRED** to v0.5.0+
**Context**: PR #42 review feedback on `ProtocolVersionedRegistry` design
**Decision Maker**: Architecture Review (based on codebase analysis)

---

## Executive Summary

**Question**: Should we create a shared async base protocol (`ProtocolAsyncRegistryBase[K, V]`) that both sync and async registries could use?

**Answer**: **No, not at this time.** The decision is to **DEFER** this work to v0.5.0 or later, pending validation of the need with additional async registry implementations.

**Rationale Summary**:
- Only one async registry currently exists (`ProtocolVersionedRegistry`)
- No validated abstraction pattern (need 2+ async registries to validate)
- Premature abstraction risk outweighs current duplication cost
- Current design is simple, self-contained, and consistent with codebase patterns
- Non-breaking to add later when justified by concrete use cases

---

## Background

### Current State

**Sync Base Protocol** (`ProtocolRegistryBase[K, V]`):
```python
@runtime_checkable
class ProtocolRegistryBase(Protocol, Generic[K, V]):
    """Synchronous base protocol for key-value registries."""
    def register(self, key: K, value: V) -> None: ...
    def get(self, key: K) -> V: ...
    def list_keys(self) -> list[K]: ...
    def is_registered(self, key: K) -> bool: ...
    def unregister(self, key: K) -> bool: ...
```

**Async Versioned Protocol** (`ProtocolVersionedRegistry[K, V]`):
```python
@runtime_checkable
class ProtocolVersionedRegistry(Protocol, Generic[K, V]):
    """Independent async protocol with version-aware operations."""
    # Base methods (async, ~130 lines duplicated from ProtocolRegistryBase)
    async def register(self, key: K, value: V) -> None: ...
    async def get(self, key: K) -> V: ...
    async def list_keys(self) -> list[K]: ...
    async def is_registered(self, key: K) -> bool: ...
    async def unregister(self, key: K) -> bool: ...

    # Version-specific methods
    async def register_version(self, key: K, version: str, value: V) -> None: ...
    async def get_version(self, key: K, version: str) -> V: ...
    async def get_latest(self, key: K) -> V: ...
    async def list_versions(self, key: K) -> list[str]: ...
    async def get_all_versions(self, key: K) -> dict[str, V]: ...
```

### Design History

1. **PR #41 Initial Design**: `ProtocolVersionedRegistry` inherited from `ProtocolRegistryBase`
2. **PR #41 Revision**: Removed inheritance due to async/sync incompatibility (LSP violation)
3. **PR #42 Review**: Suggestion to create shared async base protocol
4. **Current Analysis**: Evaluation of shared async base protocol feasibility

### The Problem

`ProtocolVersionedRegistry` duplicates ~130 lines of base protocol methods (with async signatures). This raises the question: should we create a shared async base protocol to eliminate duplication?

---

## Design Options Analysis

### Option A: Keep Separate (Current Approach) ✅ SELECTED

**Structure**:
```python
# Sync base protocol
@runtime_checkable
class ProtocolRegistryBase(Protocol, Generic[K, V]):
    def register(...) -> None: ...  # sync
    def get(...) -> V: ...  # sync
    # ... other sync methods

# Independent async protocol (with duplicated base methods)
@runtime_checkable
class ProtocolVersionedRegistry(Protocol, Generic[K, V]):
    async def register(...) -> None: ...  # async
    async def get(...) -> V: ...  # async
    # ... other async base methods
    async def register_version(...) -> None: ...  # version-specific
    async def get_version(...) -> V: ...  # version-specific
    # ... other version methods
```

**Pros**:
- ✅ **Simple and self-contained**: All methods visible in single protocol definition
- ✅ **No premature abstraction**: Wait for validated need (Rule of Three)
- ✅ **Clear documentation**: Complete method list in one place
- ✅ **Consistent with codebase**: Other specialized protocols are independent
- ✅ **Maintains flexibility**: Versioned registry can evolve independently
- ✅ **Structural typing**: Protocol inheritance doesn't provide runtime benefits in Python
- ✅ **Minimal API surface**: No unnecessary protocol hierarchy

**Cons**:
- ❌ **Code duplication**: ~130 lines duplicated from `ProtocolRegistryBase`
- ❌ **Maintenance burden**: Docstring drift risk if base methods change
- ❌ **No type hierarchy**: Cannot write generic code for "any async registry"

**Risk Assessment**:
- **Low Risk**: Duplication is only 5 methods; CRUD operations are stable
- **Mitigation**: Validation scripts prevent docstring drift
- **Impact**: Copy-paste once vs maintain abstraction forever

### Option B: Create `ProtocolAsyncRegistryBase[K, V]`

**Structure**:
```python
# Shared async base protocol
@runtime_checkable
class ProtocolAsyncRegistryBase(Protocol, Generic[K, V]):
    """Shared base for async key-value registries."""
    async def register(self, key: K, value: V) -> None: ...
    async def get(self, key: K) -> V: ...
    async def list_keys(self) -> list[K]: ...
    async def is_registered(self, key: K) -> bool: ...
    async def unregister(self, key: K) -> bool: ...

# Versioned registry extends async base
@runtime_checkable
class ProtocolVersionedRegistry(ProtocolAsyncRegistryBase[K, V]):
    """Versioned registry extending async base."""
    # Base methods inherited (documentation updated)
    async def register_version(...) -> None: ...
    async def get_version(...) -> V: ...
    # ... other version methods
```

**Pros**:
- ✅ **Reduces duplication**: Base methods inherited, not duplicated
- ✅ **Type hierarchy**: Can write generic code for `ProtocolAsyncRegistryBase`
- ✅ **Future-proof**: Other async registries can extend base
- ✅ **Clear separation**: Base CRUD vs specialized behavior

**Cons**:
- ❌ **Premature abstraction**: Only one async registry exists (no validation)
- ❌ **Documentation split**: Base methods hidden in parent protocol
- ❌ **Type complexity**: Multiple inheritance with `Generic[K, V]`
- ❌ **No current use case**: No other async registries need this base
- ❌ **Maintenance overhead**: Abstraction to maintain without clear benefit
- ❌ **Constrains evolution**: Forces versioned registry into base protocol shape

**Risk Assessment**:
- **High Risk**: Premature abstraction without validated need
- **Impact**: Ongoing maintenance cost for unvalidated abstraction
- **Reversibility**: Hard to remove once established in public API

### Option C: Use Abstract Base Methods (Sync/Async Variants)

**Structure**:
```python
@runtime_checkable
class ProtocolUnifiedRegistryBase(Protocol, Generic[K, V]):
    """Base protocol with both sync and async methods."""
    # Sync methods (required)
    def register(self, key: K, value: V) -> None: ...
    def get(self, key: K) -> V: ...

    # Async methods (optional overrides)
    async def async_register(self, key: K, value: V) -> None: ...
    async def async_get(self, key: K) -> V: ...
```

**Verdict**: ❌ **Rejected**

**Rationale**:
- Violates single responsibility (mixed sync/async semantics)
- Confusing API (when to use sync vs async?)
- Breaks Liskov Substitution Principle
- No clear advantage over Option A or B

---

## Decision Analysis

### Key Findings

#### 1. Only One Async Registry Exists

**Current async registries in codebase**:

| Protocol | Async? | CRUD Pattern? | Notes |
|----------|--------|---------------|-------|
| `ProtocolRegistryBase` | No | Yes | Sync base protocol |
| `ProtocolVersionedRegistry` | Yes | Yes | **Only async CRUD registry** |
| `ProtocolSchemaRegistry` | Yes | No | Domain-specific, not key-value |
| `ProtocolServiceRegistry` | No | Yes | Sync CRUD with async helpers |
| `ProtocolRegistry` (container) | Yes | No | Artifact retrieval, not key-value |
| `ProtocolHandlerRegistry` | No | Yes | Sync CRUD |
| `ProtocolMCPRegistry` | No | Yes | Sync CRUD |

**Conclusion**: `ProtocolVersionedRegistry` is the **only** async key-value registry with CRUD semantics.

#### 2. Premature Abstraction Risk

**Rule of Three**: Abstract after third occurrence, not first.

**Current State**:
- **1st async registry**: `ProtocolVersionedRegistry` (exists)
- **2nd async registry**: None (hypothetical)
- **3rd async registry**: None (hypothetical)

**Industry Best Practice**:
> "Duplication is far cheaper than the wrong abstraction." — Sandi Metz

**Conclusion**: Creating abstraction now is premature optimization.

#### 3. Structural Typing Makes Inheritance Unnecessary

Python protocols use structural subtyping, not nominal subtyping:

```python
# Inheritance provides NO runtime benefit
@runtime_checkable
class ProtocolAsyncRegistryBase(Protocol, Generic[K, V]):
    async def register(...): ...

@runtime_checkable
class ProtocolVersionedRegistry(ProtocolAsyncRegistryBase[K, V]):
    # Inherits structure
    pass

# VS

@runtime_checkable
class ProtocolVersionedRegistry(Protocol, Generic[K, V]):
    async def register(...): ...  # Duplicated

# Both work identically with isinstance() - structural match
isinstance(obj, ProtocolVersionedRegistry)  # True if structure matches
```

**Conclusion**: Protocol inheritance doesn't provide runtime benefits; duplication is acceptable.

#### 4. Documentation Clarity

**With duplication (current)**:
```python
class ProtocolVersionedRegistry(Protocol, Generic[K, V]):
    """
    Complete docstring with ALL methods listed.

    Base methods: register, get, list_keys, is_registered, unregister
    Version methods: register_version, get_version, ...
    """
    async def register(...): ...  # ✅ Visible in protocol
    async def register_version(...): ...  # ✅ Visible in protocol
```

**With inheritance**:
```python
class ProtocolVersionedRegistry(ProtocolAsyncRegistryBase[K, V]):
    """
    See ProtocolAsyncRegistryBase for base methods.  # ❌ Jump to other file

    Version methods: register_version, get_version, ...
    """
    # Base methods hidden ❌
    async def register_version(...): ...  # ✅ Visible
```

**Conclusion**: Current approach provides better documentation clarity.

#### 5. Consistency with Codebase Patterns

**Other specialized protocols are independent**:

```python
# ProtocolHandlerRegistry does NOT inherit ProtocolRegistryBase
# (has different semantics despite similar CRUD interface)

# ProtocolServiceRegistry does NOT inherit ProtocolRegistryBase
# (has sync methods + async helpers)

# ProtocolVersionedRegistry following same pattern
# (independent protocol with version-aware semantics)
```

**Conclusion**: Current design is consistent with established patterns.

---

## Decision: DEFER to v0.5.0+

### Selected Option

**Option A: Keep Separate (Current Approach)**

### Rationale

1. **Only one async registry exists** (`ProtocolVersionedRegistry` is unique)
2. **No validated abstraction** (need 2+ async registries to validate shared base)
3. **Premature optimization** (wait for second use case to emerge)
4. **Simplicity over abstraction** (current design is simple and self-contained)
5. **Structural typing** (protocol inheritance doesn't provide runtime benefits)
6. **Documentation clarity** (all methods visible in single protocol definition)
7. **Consistent with codebase** (other specialized registries are independent)
8. **Low duplication cost** (only 5 methods; CRUD operations are stable)
9. **Non-breaking to add later** (can introduce async base when justified)

### When to Revisit

Create `ProtocolAsyncRegistryBase[K, V]` when:

1. **Second async registry emerges** with identical CRUD semantics (e.g., `ProtocolAsyncHandlerRegistry`)
2. **Third async registry** validates the abstraction (Rule of Three)
3. **Shared behavior identified** that benefits from common base
4. **Refactoring cost justified** by maintenance savings
5. **Type hierarchy benefits** outweigh documentation split

### Validation Metrics

**Monitor in v0.4.0-v0.5.0**:
- How many async registries created?
- Do they share identical CRUD semantics?
- Would shared base reduce actual duplication?

**Trigger Threshold**:
- 2+ async registries with >80% method overlap
- Clear type hierarchy benefits identified
- Maintenance burden exceeds abstraction cost

**Action Plan**:
- If metrics met: Refactor to shared base protocol in v0.5.0
- If not met: Continue current approach indefinitely

---

## Implementation Guidance

### For Current Work (PR #42)

**No changes required**. Keep `ProtocolVersionedRegistry` as independent protocol.

**Documentation updates**:
- ✅ Document rationale for independence (lines 25-54 of `protocol_versioned_registry.py`)
- ✅ Note duplication is intentional (not an oversight)
- ✅ Reference this decision document

### For Future Work (v0.5.0+)

**If creating shared async base**:

**Step 1: Create base protocol**
```python
# src/omnibase_spi/protocols/registry/protocol_async_registry_base.py

@runtime_checkable
class ProtocolAsyncRegistryBase(Protocol, Generic[K, V]):
    """Shared base for async key-value registries.

    This protocol provides async CRUD operations for registries that need
    async I/O (database queries, remote registries, event notifications).

    .. versionadded:: 0.5.0
    """

    async def register(self, key: K, value: V) -> None:
        """Register a key-value pair."""
        ...

    async def get(self, key: K) -> V:
        """Retrieve value by key."""
        ...

    async def list_keys(self) -> list[K]:
        """List all registered keys."""
        ...

    async def is_registered(self, key: K) -> bool:
        """Check if key is registered."""
        ...

    async def unregister(self, key: K) -> bool:
        """Remove key-value pair."""
        ...
```

**Step 2: Update `ProtocolVersionedRegistry` (non-breaking)**
```python
@runtime_checkable
class ProtocolVersionedRegistry(ProtocolAsyncRegistryBase[K, V]):
    """Versioned registry extending async base.

    Inherits base CRUD methods from ProtocolAsyncRegistryBase.
    Adds version-aware operations for managing multiple versions per key.

    .. versionadded:: 0.4.0
    .. versionchanged:: 0.5.0
       Now extends ProtocolAsyncRegistryBase for shared async CRUD interface.
    """

    # Base methods inherited (no duplication)

    # Version-specific methods
    async def register_version(self, key: K, version: str, value: V) -> None: ...
    async def get_version(self, key: K, version: str) -> V: ...
    async def get_latest(self, key: K) -> V: ...
    async def list_versions(self, key: K) -> list[str]: ...
    async def get_all_versions(self, key: K) -> dict[str, V]: ...
```

**Step 3: Update other async registries**
```python
@runtime_checkable
class ProtocolAsyncHandlerRegistry(ProtocolAsyncRegistryBase[str, type[ProtocolHandler]]):
    """Async handler registry.

    .. versionadded:: 0.5.0
    """
    # Base methods inherited
    # Domain-specific extensions
    ...
```

**Step 4: Update documentation**
- Document migration path from independent to inherited protocols
- Add examples showing type hierarchy benefits
- Update API reference diagrams

---

## Alternatives Considered

### Alternative 1: Dual-Mode Registry

**Idea**: Single registry implementing both sync and async methods.

```python
class DualModeRegistry:
    # Sync methods (ProtocolRegistryBase)
    def register(self, key: str, value: type) -> None:
        asyncio.run(self.async_register(key, value))

    # Async methods (ProtocolVersionedRegistry)
    async def async_register(self, key: str, value: type) -> None:
        ...
```

**Verdict**: ❌ **Rejected**
- Confusing API (sync vs async methods)
- Hidden async execution in sync methods
- Violates single responsibility principle

### Alternative 2: Generate Async Protocol from Sync

**Idea**: Auto-generate async protocol from sync using decorator/metaclass.

```python
@async_protocol(ProtocolRegistryBase)
class ProtocolAsyncRegistryBase:
    pass  # Methods auto-generated as async
```

**Verdict**: ❌ **Rejected**
- Too much magic (unclear what's happening)
- Hard to maintain and debug
- Type checkers struggle with generated protocols

### Alternative 3: Mixin Pattern

**Idea**: Use mixin for shared base methods.

```python
class AsyncRegistryMixin:
    async def register(...): ...
    async def get(...): ...

class ProtocolVersionedRegistry(AsyncRegistryMixin, Protocol, Generic[K, V]):
    async def register_version(...): ...
```

**Verdict**: ❌ **Rejected**
- Mixins don't work well with structural protocols
- Violates protocol-based design (mixins are implementation detail)

---

## Impact Assessment

### No Impact on Current Work

- ✅ **Zero breaking changes**: Current implementation unchanged
- ✅ **No migration needed**: Existing code continues to work
- ✅ **Documentation complete**: Rationale documented in protocol docstrings

### Future Extensibility Preserved

- ✅ **Non-breaking to add**: Can introduce async base later
- ✅ **Protocol compatibility**: Structural typing enables smooth migration
- ✅ **Clear trigger**: Metrics defined for when to revisit decision

### Maintenance Considerations

**Current Approach (Duplication)**:
- ~130 lines duplicated (5 methods with docstrings)
- CRUD operations are stable (low change frequency)
- Validation scripts prevent docstring drift
- One-time copy-paste cost

**Future Approach (Shared Base)**:
- Abstraction to maintain across versions
- Protocol hierarchy to document and update
- Type complexity to manage
- Ongoing maintenance cost

**Conclusion**: Current approach has lower total cost until 2+ async registries exist.

---

## References

- **PR #42**: fix(protocols): PR #41 follow-up review feedback
- **PR #41**: feat(protocols): create generic ProtocolRegistry[K, V] to unify all registry protocols
- **Design Document**: `/workspace/omnibase_spi/docs/decisions/PR42_PROTOCOL_DESIGN_ANALYSIS.md`
- **Protocol File**: `/workspace/omnibase_spi/src/omnibase_spi/protocols/registry/protocol_versioned_registry.py`
- **Documentation**: `/workspace/omnibase_spi/docs/api-reference/REGISTRY.md`

---

## Appendix: Liskov Substitution Principle and Async/Sync

### Why Async Cannot Override Sync

**Liskov Substitution Principle (LSP)**:
> "Objects of a superclass shall be replaceable with objects of its subclasses without breaking the application."

**Problem with async overriding sync**:

```python
# Base protocol (sync)
class ProtocolRegistryBase(Protocol, Generic[K, V]):
    def register(self, key: K, value: V) -> None: ...

# Subclass protocol (async override - VIOLATES LSP)
class ProtocolVersionedRegistry(ProtocolRegistryBase[K, V]):
    async def register(self, key: K, value: V) -> None: ...  # ❌ LSP violation

# Usage that breaks
registry: ProtocolRegistryBase = versioned_registry
registry.register(key, value)  # ❌ Returns coroutine, not None!
# TypeError: object NoneType can't be used in 'await' expression
```

**Why this violates LSP**:
1. **Return type changed**: `None` → `Coroutine[None, None, None]`
2. **Execution model changed**: Synchronous → asynchronous
3. **Caller expectations broken**: `registry.register(...)` returns unawaited coroutine

**Solution**: Separate protocols for sync and async

```python
# Sync protocol
class ProtocolRegistryBase(Protocol, Generic[K, V]):
    def register(self, key: K, value: V) -> None: ...

# Independent async protocol (not inheriting)
class ProtocolVersionedRegistry(Protocol, Generic[K, V]):
    async def register(self, key: K, value: V) -> None: ...  # ✅ Independent
```

---

**Decision Status**: **FINAL** (for v0.4.0)
**Review Cycle**: To be revisited in v0.5.0 planning based on validation metrics
**Document Maintainer**: Architecture Team
