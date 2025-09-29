# ONEX Protocol Migration Guide

This guide helps you migrate from the old protocol naming conventions to the new naming structure implemented in omnibase-spi. The migration reflects improved architectural clarity and separation of concerns.

## Migration Overview

| Old Name | New Name | Migration Complexity | Breaking Changes |
|----------|----------|---------------------|------------------|
| `ProtocolRegistry` | `ProtocolArtifactContainer` | **Medium** | Method signatures unchanged |
| `ProtocolHandlerRegistry` | `ProtocolNodeDiscoveryRegistry` | **High** | New discovery pattern |
| N/A | `ProtocolNodeRegistry` | **New** | Distributed node coordination |
| N/A | `ProtocolServiceRegistry` | **New** | Service registry information |

## Protocol Name Changes

### 1. ProtocolRegistry → ProtocolArtifactContainer

#### What Changed
- **Old**: Generic "registry" concept
- **New**: Specific "artifact container" for managing ONEX components
- **Reason**: Clearer separation between artifact management and service discovery

#### Migration Steps

**Step 1: Update Import Statements**
```python
# OLD - Before migration
from omnibase_spi.protocols.core.protocol_registry import ProtocolRegistry

# NEW - After migration  
from omnibase_spi.protocols.container.protocol_artifact_container import ProtocolArtifactContainer
```

**Step 2: Update Type Annotations**
```python
# OLD - Generic registry reference
def process_artifacts(registry: ProtocolRegistry) -> List[ArtifactInfo]:
    return registry.get_all_artifacts()

# NEW - Specific container reference
def process_artifacts(container: ProtocolArtifactContainer) -> List[ProtocolArtifactInfo]:
    return container.get_artifacts()
```

**Step 3: Update Variable Names (Recommended)**
```python
# OLD - Generic naming
registry: ProtocolRegistry = SomeRegistryImpl()
items = registry.get_items()

# NEW - Descriptive naming
container: ProtocolArtifactContainer = ArtifactLoaderNode()
artifacts = container.get_artifacts()
```

#### Method Compatibility
✅ **No breaking changes** - all core methods remain the same:

```python
# These methods work identically in both old and new protocols
def get_status() -> ProtocolArtifactContainerStatus  # Same return type
def get_artifacts() -> List[ProtocolArtifactInfo]    # Same method signature
def has_artifact(name: str) -> bool                  # Same method signature
```

### 2. ProtocolHandlerRegistry → ProtocolNodeDiscoveryRegistry

#### What Changed
- **Old**: Direct handler registration model
- **New**: Discovery-based node registration with multiple sources
- **Reason**: Support for plugin architectures and flexible node discovery

#### Terminology Clarification
- **Handler**: File type implementation (e.g., `ProtocolFileTypeHandler`)
- **Node**: Deployed/discovered instance of a handler  
- **Discovery**: Process of finding and registering handler nodes

#### Migration Complexity: **HIGH** ⚠️
This migration requires architectural changes to support the new discovery pattern.

**Step 1: Update Core Import**
```python
# OLD - Direct handler registry
from omnibase_spi.protocols.handler.protocol_handler_registry import ProtocolHandlerRegistry

# NEW - Discovery-based node registry
from omnibase_spi.protocols.discovery.protocol_handler_discovery import (
    ProtocolNodeDiscoveryRegistry,
    ProtocolHandlerDiscovery
)
```

**Step 2: Implement Discovery Sources**
The new pattern requires implementing discovery sources rather than direct registration:

```python
# OLD - Direct registration pattern
class OldHandlerSystem:
    def __init__(self):
        self.registry: ProtocolHandlerRegistry = HandlerRegistryImpl()

    def add_handler(self, handler_class, extensions):
        # Direct registration
        self.registry.register_handler(handler_class, extensions)

# NEW - Discovery-based pattern  
class NewHandlerSystem:
    def __init__(self):
        self.registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()

        # Setup discovery sources
        self.setup_discovery_sources()

    def setup_discovery_sources(self):
        # Entry point node discovery
        entry_discovery: ProtocolHandlerDiscovery = EntryPointDiscovery("onex.handlers")
        self.registry.register_discovery_source(entry_discovery)

        # Config file node discovery
        config_discovery: ProtocolHandlerDiscovery = ConfigFileDiscovery("config/handlers.yaml")
        self.registry.register_discovery_source(config_discovery)

        # Environment node discovery
        env_discovery: ProtocolHandlerDiscovery = EnvironmentDiscovery("ONEX_HANDLER_")
        self.registry.register_discovery_source(env_discovery)

        # Trigger node discovery and registration
        self.registry.discover_and_register_nodes()
```

**Step 3: Update Handler Information Model**
```python
# OLD - Simple handler info
class OldHandlerInfo:
    def __init__(self, handler_class, extensions):
        self.handler_class = handler_class
        self.extensions = extensions

# NEW - Rich node metadata  
class NewHandlerInfo:
    def __init__(self):
        self.node_class: Type[ProtocolFileTypeHandler] = handler_class
        self.name: str = "pdf_handler"
        self.source: str = "entry_point"  # "core", "runtime", "plugin"
        self.priority: int = 50
        self.extensions: List[str] = [".pdf", ".docx"]
        self.special_files: List[str] = ["README", "Dockerfile"]
        self.metadata: Dict[str, Any] = {"version": "1.0.0"}
```

**Step 4: Migration Script Example**
```python
def migrate_handler_registry():
    """Migration script from old to new handler registry."""

    # 1. Extract existing handlers from old registry
    old_registry: ProtocolHandlerRegistry = get_legacy_registry()
    existing_handlers = old_registry.get_all_handlers()

    # 2. Create new discovery registry
    new_registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()

    # 3. Create compatibility discovery source for existing handlers
    class LegacyHandlerDiscovery:
        def __init__(self, legacy_handlers):
            self.legacy_handlers = legacy_handlers

        def discover_nodes(self) -> List[ProtocolHandlerInfo]:
            nodes = []
            for handler in self.legacy_handlers:
                node_info = ProtocolHandlerInfo(
                    node_class=handler.handler_class,
                    name=handler.name,
                    source="legacy_migration",
                    priority=50,
                    extensions=handler.extensions,
                    special_files=handler.special_files or [],
                    metadata={"migrated_from": "legacy_registry"}
                )
                nodes.append(node_info)
            return nodes

        def get_source_name(self) -> str:
            return "LegacyMigration"

    # 4. Register legacy handlers through discovery
    legacy_discovery = LegacyHandlerDiscovery(existing_handlers)
    new_registry.register_discovery_source(legacy_discovery)

    # 5. Add modern discovery sources
    new_registry.register_discovery_source(EntryPointDiscovery("onex.handlers"))
    new_registry.register_discovery_source(ConfigFileDiscovery("config/handlers.yaml"))

    # 6. Discover and register all handlers
    new_registry.discover_and_register_nodes()

    return new_registry
```

## New Protocols (No Migration Needed)

### 3. ProtocolNodeRegistry (NEW)
**Purpose**: Distributed node coordination and service discovery
**When to add**: When building distributed ONEX systems

```python
# Add when implementing distributed node coordination
from omnibase_spi.protocols.core.protocol_node_registry import (
    ProtocolNodeRegistry,
    ProtocolNodeInfo
)

class DistributedSystem:
    def __init__(self, environment: str = "prod"):
        # NEW - Add distributed node registry
        self.node_registry: ProtocolNodeRegistry = ConsulNodeRegistry(environment)

    async def coordinate_nodes(self):
        # Register this node
        node_info = self._create_node_info()
        await self.node_registry.register_node(node_info)

        # Discover peer nodes
        peer_nodes = await self.node_registry.discover_nodes(
            node_type="COMPUTE",
            environment="prod",
            group="processing"
        )
```

### 4. ProtocolServiceRegistry (NEW)
**Purpose**: Service registry information and monitoring
**When to add**: When building DI containers or service monitoring

```python
# Add for service registry monitoring
from omnibase_spi.protocols.types.container_types import ProtocolServiceRegistry

class ServiceMonitor:
    def __init__(self, registry: ProtocolServiceRegistry):
        self.registry = registry

    def get_health_status(self):
        return {
            "total_services": self.registry.total_services,
            "active_services": self.registry.active_services,
            "health_ratio": self.registry.active_services / self.registry.total_services
        }
```

## Migration Impact Assessment

### Low Impact Changes
✅ **ProtocolRegistry → ProtocolArtifactContainer**
- Import path changes only
- Method signatures unchanged
- Variable renaming recommended but not required
- **Estimated effort**: 2-4 hours for medium-sized codebase

### High Impact Changes  
⚠️ **ProtocolHandlerRegistry → ProtocolNodeDiscoveryRegistry**
- Architectural pattern change from direct registration to discovery
- New discovery source implementations required
- Handler information model changes
- **Estimated effort**: 1-2 days for complete migration

### Code Search Patterns

Use these patterns to find code that needs migration:

```bash
# Find old protocol imports
grep -r "ProtocolRegistry" src/ --include="*.py"
grep -r "ProtocolHandlerRegistry" src/ --include="*.py"

# Find old protocol usages
grep -r "registry\.register_handler" src/ --include="*.py"
grep -r "registry\.get_handlers" src/ --include="*.py"

# Find variable declarations
grep -r ": ProtocolRegistry" src/ --include="*.py"
grep -r ": ProtocolHandlerRegistry" src/ --include="*.py"
```

## Migration Timeline

### Phase 1: Low-Risk Changes (Week 1)
1. **Update imports** for `ProtocolRegistry` → `ProtocolArtifactContainer`
2. **Update type annotations** and variable names
3. **Test existing functionality** - no behavioral changes expected

### Phase 2: Discovery Migration Planning (Week 2)  
1. **Audit existing handler registrations** using `ProtocolHandlerRegistry`
2. **Design discovery sources** for your specific use cases
3. **Create migration scripts** for handler metadata conversion

### Phase 3: Discovery Implementation (Week 3-4)
1. **Implement discovery sources** (entry points, config files, environment)
2. **Update handler registration logic** to use discovery pattern
3. **Test handler discovery and registration**
4. **Migrate existing handlers** to new discovery model

### Phase 4: Integration & Testing (Week 5)
1. **Integration testing** with new protocol structure
2. **Performance validation** - discovery should be one-time cost
3. **Documentation updates** for team members
4. **Deployment and monitoring**

## Backward Compatibility Strategy

### Approach 1: Parallel Implementation
Run both old and new protocols during transition:

```python
class TransitionSystem:
    def __init__(self):
        # Keep old system running
        self.legacy_registry: ProtocolHandlerRegistry = LegacyHandlerRegistry()

        # Add new system
        self.new_registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()

        # Synchronize between them
        self.sync_registries()

    def sync_registries(self):
        """Keep registries synchronized during transition."""
        legacy_handlers = self.legacy_registry.get_all_handlers()

        # Register legacy handlers in new system
        for handler in legacy_handlers:
            handler_info = self._convert_to_new_format(handler)
            self.new_registry.register_node_info(handler_info)
```

### Approach 2: Gradual Migration
Migrate one component at a time:

```python
class GradualMigration:
    def __init__(self):
        self.migration_phase = os.getenv("MIGRATION_PHASE", "legacy")

    def get_registry(self) -> Union[ProtocolHandlerRegistry, ProtocolNodeDiscoveryRegistry]:
        if self.migration_phase == "legacy":
            return LegacyHandlerRegistry()
        elif self.migration_phase == "transition":
            return TransitionRegistry()  # Supports both APIs
        else:
            return NodeDiscoveryRegistryImpl()
```

## Testing Migration

### Unit Testing
```python
class TestProtocolMigration:
    def test_artifact_container_compatibility(self):
        """Ensure ProtocolArtifactContainer works with existing logic."""
        # OLD usage pattern should still work
        container: ProtocolArtifactContainer = TestArtifactContainer()

        # Test same method signatures  
        artifacts = container.get_artifacts()
        status = container.get_status()
        has_node = container.has_artifact("test_node")

        assert len(artifacts) > 0
        assert status.status in ["ACTIVE", "INACTIVE", "ERROR", "UNKNOWN"]
        assert isinstance(has_node, bool)

    def test_discovery_registry_functionality(self):
        """Test new discovery-based registration."""
        registry: ProtocolNodeDiscoveryRegistry = TestDiscoveryRegistry()

        # Test discovery source registration
        discovery_source = MockHandlerDiscovery()
        registry.register_discovery_source(discovery_source)

        # Test node discovery and registration
        registry.discover_and_register_nodes()

        # Verify handlers were discovered and registered
        # (specific assertions depend on your implementation)
```

### Integration Testing
```python
class TestE2EMigration:
    def test_full_migration_workflow(self):
        """Test complete migration from old to new protocols."""

        # 1. Start with legacy system
        legacy_system = LegacyHandlerSystem()
        legacy_handlers = legacy_system.get_all_handlers()

        # 2. Migrate to new system
        new_system = NewHandlerSystem()
        migration_result = migrate_handlers(legacy_handlers, new_system)

        # 3. Verify functionality preserved
        assert len(new_system.get_discovered_handlers()) >= len(legacy_handlers)

        # 4. Test handler functionality still works
        for handler in new_system.get_discovered_handlers():
            assert handler.can_handle_file("test.pdf") == expected_result
```

## Troubleshooting Migration Issues

### Common Issues & Solutions

**Issue**: Import errors after migration
```python
# Error: ModuleNotFoundError: No module named 'omnibase_spi.protocols.core.protocol_registry'

# Solution: Update import paths
from omnibase_spi.protocols.container.protocol_artifact_container import ProtocolArtifactContainer
```

**Issue**: Handler discovery not finding expected handlers
```python
# Problem: New discovery registry returns empty handler list

# Solution: Check discovery source configuration
registry.register_discovery_source(EntryPointDiscovery("onex.handlers"))  # Correct group name
registry.register_discovery_source(ConfigFileDiscovery("config/handlers.yaml"))  # File exists
registry.discover_and_register_nodes()  # Call discovery
```

**Issue**: Type annotation errors
```python
# Error: Incompatible types in assignment

# Solution: Update type annotations
def process_container(container: ProtocolArtifactContainer) -> List[ProtocolArtifactInfo]:
    return container.get_artifacts()
```

## Post-Migration Verification

### Checklist
- [ ] All imports updated to new protocol paths
- [ ] Type annotations updated to new protocol names  
- [ ] Discovery sources implemented and tested
- [ ] Handler registration working through discovery
- [ ] Integration tests passing
- [ ] Performance acceptable (discovery is one-time cost)
- [ ] Documentation updated for team
- [ ] Old protocol references removed

### Monitoring
After migration, monitor these metrics:
- **Handler Discovery Time**: Should be reasonable at startup
- **Handler Registration Success Rate**: Should match or exceed legacy system
- **System Functionality**: All file processing should work as before
- **Error Rates**: No increase in handler-related errors

## Getting Help

If you encounter issues during migration:

1. **Check the Protocol Selection Guide** for proper protocol usage patterns
2. **Review the Protocol Composition Patterns** for integration examples
3. **Run the migration test suite** to validate your changes
4. **Create minimal reproduction cases** for debugging specific issues

The migration represents a significant architectural improvement that will provide better separation of concerns and more flexible handler management in the long term.
