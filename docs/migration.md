# Migration Guide

## Overview

Comprehensive guide for migrating between versions of omnibase-spi, handling protocol evolution, and managing breaking changes in production systems. This guide covers versioning strategies, backward compatibility patterns, and safe migration procedures.

## Table of Contents

- [Versioning Strategy](#versioning-strategy)
- [Migration Planning](#migration-planning)
- [Protocol Evolution](#protocol-evolution)
- [Breaking Changes](#breaking-changes)
- [Backward Compatibility](#backward-compatibility)
- [Production Migration](#production-migration)
- [Testing Migration](#testing-migration)

## Versioning Strategy

### Semantic Versioning (SemVer)

omnibase-spi follows semantic versioning:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes to protocol interfaces
- **MINOR** (1.0.0 → 1.1.0): New protocols or backward-compatible additions
- **PATCH** (1.0.0 → 1.0.1): Bug fixes and documentation updates

### Version Compatibility Matrix

| SPI Version | Python Support | Breaking Changes | Migration Required |
|-------------|----------------|------------------|--------------------|
| 0.1.x       | 3.11+          | Initial release  | N/A                |
| 0.2.x       | 3.11+          | Protocol additions | No                |
| 1.0.x       | 3.11+          | Stable API       | No                |
| 1.1.x       | 3.11+          | New protocols    | No                |
| 2.0.x       | 3.12+          | Protocol changes | **Yes**            |

### Protocol Versioning

Individual protocols are versioned through interface evolution:

```python
# Version 1: Initial protocol
@runtime_checkable
class ProtocolUserServiceV1(Protocol):
    """Version 1 of user service protocol."""
    
    async def get_user(self, user_id: UUID) -> Optional[User]: ...
    async def create_user(self, email: str, name: str) -> User: ...

# Version 2: Backward compatible additions
@runtime_checkable  
class ProtocolUserServiceV2(ProtocolUserServiceV1, Protocol):
    """Version 2 adds batch operations while maintaining V1 compatibility."""
    
    # Inherited from V1
    # async def get_user(self, user_id: UUID) -> Optional[User]: ...
    # async def create_user(self, email: str, name: str) -> User: ...
    
    # New in V2
    async def get_users_batch(
        self, user_ids: list[UUID]
    ) -> dict[UUID, Optional[User]]: ...
    
    async def create_users_batch(
        self, user_data: list[dict[str, str]]
    ) -> list[User]: ...

# Version 3: Breaking changes require new interface
@runtime_checkable
class ProtocolUserServiceV3(Protocol):
    """Version 3 with breaking changes - new interface required."""
    
    # BREAKING: Changed signature (added required metadata parameter)
    async def get_user(
        self, 
        user_id: UUID,
        include_metadata: bool = True  # New required behavior
    ) -> Optional[UserV3]: ...  # Different return type
    
    # BREAKING: Changed signature (email validation requirements)
    async def create_user(
        self,
        email: EmailAddress,  # Stricter type
        name: str,
        metadata: dict[str, str]  # Now required
    ) -> UserV3: ...  # Different return type
```

## Migration Planning

### Pre-Migration Assessment

Before starting a migration:

1. **Inventory Current Usage**
```python
# Script to analyze current protocol usage
import ast
from pathlib import Path

class ProtocolUsageAnalyzer(ast.NodeVisitor):
    """Analyze protocol usage in codebase."""
    
    def __init__(self):
        self.protocol_imports = []
        self.protocol_usage = []
    
    def visit_ImportFrom(self, node):
        if node.module and "omnibase_spi.protocols" in node.module:
            for alias in node.names:
                self.protocol_imports.append({
                    'module': node.module,
                    'name': alias.name,
                    'line': node.lineno
                })
    
    def visit_Call(self, node):
        # Track protocol method calls
        if isinstance(node.func, ast.Attribute):
            self.protocol_usage.append({
                'method': node.func.attr,
                'line': node.lineno
            })
        self.generic_visit(node)

def analyze_codebase(root_path: Path) -> dict:
    """Analyze protocol usage across codebase."""
    analyzer = ProtocolUsageAnalyzer()
    
    for py_file in root_path.rglob("*.py"):
        with open(py_file) as f:
            try:
                tree = ast.parse(f.read())
                analyzer.visit(tree)
            except SyntaxError:
                continue
    
    return {
        'imports': analyzer.protocol_imports,
        'usage': analyzer.protocol_usage,
        'total_files': len(list(root_path.rglob("*.py")))
    }

# Run analysis
usage_report = analyze_codebase(Path("src/"))
print(f"Found {len(usage_report['imports'])} protocol imports")
print(f"Found {len(usage_report['usage'])} protocol method calls")
```

2. **Dependency Analysis**
```python
# Check implementation dependencies
def check_implementation_compatibility(
    current_version: str,
    target_version: str
) -> dict:
    """Check if implementations are compatible with target version."""
    
    compatibility_matrix = {
        "0.1.x": {"supports": ["DatabaseUserService", "InMemoryUserService"]},
        "0.2.x": {"supports": ["DatabaseUserService", "InMemoryUserService", "CacheUserService"]},
        "1.0.x": {"supports": ["DatabaseUserService", "InMemoryUserService", "CacheUserService", "RestUserService"]},
        "2.0.x": {"requires_migration": ["DatabaseUserService"], "supports": ["CacheUserService", "RestUserServiceV2"]}
    }
    
    current_support = compatibility_matrix.get(current_version, {})
    target_support = compatibility_matrix.get(target_version, {})
    
    return {
        "breaking_changes": target_support.get("requires_migration", []),
        "new_implementations": set(target_support.get("supports", [])) - set(current_support.get("supports", [])),
        "deprecated_implementations": set(current_support.get("supports", [])) - set(target_support.get("supports", []))
    }
```

3. **Testing Strategy**
```python
# Migration testing plan
@dataclass
class MigrationTestPlan:
    """Plan for testing migration."""
    
    current_version: str
    target_version: str
    test_phases: list[str]
    rollback_plan: str
    validation_criteria: list[str]
    
    @classmethod
    def create_migration_plan(
        cls,
        current: str,
        target: str
    ) -> 'MigrationTestPlan':
        return cls(
            current_version=current,
            target_version=target,
            test_phases=[
                "Unit tests with new protocols",
                "Integration tests with mixed versions",
                "Performance regression testing",
                "Backward compatibility verification",
                "End-to-end workflow testing"
            ],
            rollback_plan=f"Revert to {current} if critical issues found",
            validation_criteria=[
                "All existing functionality works",
                "New features are accessible",
                "Performance meets benchmarks",
                "No data corruption or loss"
            ]
        )
```

## Protocol Evolution

### Backward Compatible Changes

These changes don't require migration:

```python
# ✅ SAFE: Adding optional parameters with defaults
@runtime_checkable
class ProtocolUserService(Protocol):
    async def create_user(
        self,
        email: str,
        name: str,
        metadata: Optional[dict[str, str]] = None  # ✅ Optional with default
    ) -> User: ...

# ✅ SAFE: Adding new methods
@runtime_checkable
class ProtocolUserService(Protocol):
    # Existing methods unchanged
    async def get_user(self, user_id: UUID) -> Optional[User]: ...
    
    # ✅ New method doesn't break existing implementations
    async def search_users(
        self,
        query: str,
        limit: int = 10
    ) -> list[User]: ...

# ✅ SAFE: Adding new literal values to types
UserStatus = Literal[
    "active", "inactive", "suspended",
    "pending_verification"  # ✅ New status added
]

# ✅ SAFE: Extending unions with new types
ContextValue = (
    str | int | float | bool | list[str] | dict[str, str] |
    datetime  # ✅ New type added to union
)
```

### Breaking Changes

These changes require migration:

```python
# ❌ BREAKING: Changing method signatures
@runtime_checkable
class ProtocolUserService(Protocol):
    # ❌ BREAKING: Changed parameter type
    async def get_user(
        self, 
        user_id: str  # Was UUID, now str
    ) -> Optional[User]: ...
    
    # ❌ BREAKING: Removed default value
    async def create_user(
        self,
        email: str,
        name: str,
        metadata: dict[str, str]  # Was optional, now required
    ) -> User: ...
    
    # ❌ BREAKING: Changed return type
    async def list_users(self) -> UserCollection:  # Was list[User]

# ❌ BREAKING: Removing literal values
UserStatus = Literal[
    "active", "inactive"  # ❌ BREAKING: Removed "suspended"
]

# ❌ BREAKING: Removing methods
@runtime_checkable
class ProtocolUserService(Protocol):
    async def get_user(self, user_id: UUID) -> Optional[User]: ...
    # ❌ BREAKING: create_user method removed
```

### Evolution Strategies

#### 1. Interface Extension (Preferred)

```python
# Step 1: Create extended interface
@runtime_checkable
class ProtocolUserServiceEnhanced(ProtocolUserService, Protocol):
    """Enhanced user service with additional capabilities."""
    
    # Inherit existing methods
    # async def get_user(self, user_id: UUID) -> Optional[User]: ...
    # async def create_user(self, email: str, name: str) -> User: ...
    
    # Add new methods
    async def get_user_with_permissions(
        self, 
        user_id: UUID
    ) -> Optional[UserWithPermissions]: ...
    
    async def bulk_update_users(
        self,
        updates: list[UserUpdate]
    ) -> BulkUpdateResult: ...

# Step 2: Implement enhanced interface
class DatabaseUserServiceEnhanced(
    DatabaseUserService,
    ProtocolUserServiceEnhanced
):
    """Enhanced database user service."""
    
    # Inherit base implementation
    # get_user, create_user methods from DatabaseUserService
    
    # Implement new methods
    async def get_user_with_permissions(
        self,
        user_id: UUID
    ) -> Optional[UserWithPermissions]:
        user = await self.get_user(user_id)
        if not user:
            return None
        
        permissions = await self.get_user_permissions(user_id)
        return UserWithPermissions(user=user, permissions=permissions)

# Step 3: Gradual adoption
def get_user_service_enhanced(
    base_service: ProtocolUserService
) -> ProtocolUserServiceEnhanced:
    """Upgrade service to enhanced version."""
    if isinstance(base_service, ProtocolUserServiceEnhanced):
        return base_service
    else:
        # Wrap with adapter
        return UserServiceEnhancedAdapter(base_service)
```

#### 2. Deprecation and Replacement

```python
# Step 1: Mark old interface as deprecated
import warnings

@runtime_checkable
class ProtocolUserServiceDeprecated(Protocol):
    """
    User service protocol (DEPRECATED).
    
    .. deprecated:: 1.2.0
        Use ProtocolUserServiceV2 instead.
    """
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        .. deprecated:: 1.2.0
            Use get_user_detailed instead.
        """
        warnings.warn(
            "ProtocolUserService.get_user is deprecated, use ProtocolUserServiceV2.get_user_detailed",
            DeprecationWarning,
            stacklevel=2
        )
        ...

# Step 2: Create new interface
@runtime_checkable
class ProtocolUserServiceV2(Protocol):
    """New user service protocol with enhanced capabilities."""
    
    async def get_user_detailed(
        self,
        user_id: UUID,
        include_permissions: bool = False
    ) -> Optional[UserDetailed]: ...

# Step 3: Provide migration adapter
class UserServiceV1ToV2Adapter(ProtocolUserServiceV2):
    """Adapter from V1 to V2 interface."""
    
    def __init__(self, v1_service: ProtocolUserServiceDeprecated):
        self.v1_service = v1_service
    
    async def get_user_detailed(
        self,
        user_id: UUID,
        include_permissions: bool = False
    ) -> Optional[UserDetailed]:
        # Convert V1 call to V2 response
        v1_user = await self.v1_service.get_user(user_id)
        if not v1_user:
            return None
        
        # Convert to V2 format
        return UserDetailed(
            id=v1_user.id,
            email=v1_user.email,
            name=v1_user.name,
            status=v1_user.status,
            created_at=v1_user.created_at,
            permissions=[] if not include_permissions else await self._get_permissions(user_id)
        )
```

## Breaking Changes

### Handling Major Version Upgrades

#### Migration Checklist for 1.x → 2.x

1. **Protocol Interface Changes**
```python
# omnibase-spi 1.x
@runtime_checkable
class ProtocolUserService(Protocol):
    async def create_user(
        self, email: str, name: str
    ) -> User: ...

# omnibase-spi 2.x (BREAKING CHANGES)
@runtime_checkable  
class ProtocolUserService(Protocol):
    async def create_user(
        self,
        user_data: UserCreateRequest  # ❌ BREAKING: Different parameter structure
    ) -> UserCreateResponse: ...  # ❌ BREAKING: Different return type
```

2. **Type Definition Changes**
```python
# omnibase-spi 1.x
UserStatus = Literal["active", "inactive", "suspended"]

# omnibase-spi 2.x (BREAKING CHANGES)
UserStatus = Literal["enabled", "disabled", "archived"]  # ❌ Different values
```

3. **Migration Implementation**
```python
class UserServiceV1ToV2Migration:
    """Migration helper for User Service 1.x to 2.x."""
    
    def __init__(self, v1_service: ProtocolUserServiceV1):
        self.v1_service = v1_service
    
    def convert_user_status(self, v1_status: str) -> str:
        """Convert V1 status to V2 status."""
        status_mapping = {
            "active": "enabled",
            "inactive": "disabled", 
            "suspended": "archived"
        }
        return status_mapping.get(v1_status, "disabled")
    
    def convert_user_to_v2(self, v1_user: UserV1) -> UserV2:
        """Convert V1 user to V2 format."""
        return UserV2(
            id=v1_user.id,
            email=v1_user.email,
            name=v1_user.name,
            status=self.convert_user_status(v1_user.status),
            created_at=v1_user.created_at,
            metadata=v1_user.metadata or {}  # V2 requires metadata
        )
    
    async def migrate_user_data(self) -> None:
        """Migrate all user data from V1 to V2 format."""
        # Implementation specific migration logic
        pass

# V2 service that can work with V1 data during migration
class MigrationAwareUserServiceV2(ProtocolUserServiceV2):
    """V2 service with V1 compatibility during migration."""
    
    def __init__(
        self,
        v2_service: ProtocolUserServiceV2,
        migration_helper: UserServiceV1ToV2Migration,
        migration_complete: bool = False
    ):
        self.v2_service = v2_service
        self.migration_helper = migration_helper
        self.migration_complete = migration_complete
    
    async def create_user(
        self, user_data: UserCreateRequest
    ) -> UserCreateResponse:
        """Create user with migration support."""
        if self.migration_complete:
            # Use V2 service directly
            return await self.v2_service.create_user(user_data)
        else:
            # Handle both V1 and V2 data formats during migration
            try:
                return await self.v2_service.create_user(user_data)
            except ValidationError:
                # Fallback to V1 compatibility mode
                v1_user = await self._create_user_v1_compatible(user_data)
                return self.migration_helper.convert_user_to_v2(v1_user)
```

### Feature Flag Migration

```python
from typing import Protocol
import os

@runtime_checkable
class ProtocolFeatureFlags(Protocol):
    """Protocol for feature flag management."""
    
    async def is_enabled(
        self,
        flag_name: str,
        context: Optional[dict[str, str]] = None
    ) -> bool: ...

class MigrationFeatureFlags:
    """Feature flags for managing migrations."""
    
    # Migration-related feature flags
    USE_USER_SERVICE_V2 = "use_user_service_v2"
    ENABLE_BATCH_OPERATIONS = "enable_batch_operations"
    STRICT_VALIDATION = "strict_validation"

class GradualMigrationManager:
    """Manage gradual migration using feature flags."""
    
    def __init__(
        self,
        feature_flags: ProtocolFeatureFlags,
        v1_service: ProtocolUserServiceV1,
        v2_service: ProtocolUserServiceV2
    ):
        self.feature_flags = feature_flags
        self.v1_service = v1_service
        self.v2_service = v2_service
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Route to V1 or V2 based on feature flag."""
        use_v2 = await self.feature_flags.is_enabled(
            MigrationFeatureFlags.USE_USER_SERVICE_V2,
            context={"user_id": str(user_id)}
        )
        
        if use_v2:
            try:
                v2_result = await self.v2_service.get_user_detailed(user_id)
                return self._convert_v2_to_common_format(v2_result)
            except Exception:
                # Fallback to V1 on V2 failure
                return await self.v1_service.get_user(user_id)
        else:
            return await self.v1_service.get_user(user_id)
    
    def _convert_v2_to_common_format(self, v2_user) -> User:
        """Convert V2 detailed user to common format."""
        return User(
            id=v2_user.id,
            email=v2_user.email,
            name=v2_user.name,
            status=self._map_v2_status_to_v1(v2_user.status),
            created_at=v2_user.created_at
        )
```

## Backward Compatibility

### Compatibility Adapters

```python
# Adapter pattern for backward compatibility
class UserServiceV2ToV1Adapter(ProtocolUserServiceV1):
    """Adapter to use V2 service with V1 interface."""
    
    def __init__(self, v2_service: ProtocolUserServiceV2):
        self.v2_service = v2_service
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """V1 interface method using V2 service."""
        v2_user = await self.v2_service.get_user_detailed(user_id)
        if not v2_user:
            return None
        
        # Convert V2 detailed user to V1 simple user
        return User(
            id=v2_user.id,
            email=v2_user.email,
            name=v2_user.name,
            status=self._convert_status_v2_to_v1(v2_user.status),
            created_at=v2_user.created_at
        )
    
    async def create_user(self, email: str, name: str) -> User:
        """V1 interface method using V2 service."""
        # Convert V1 parameters to V2 format
        create_request = UserCreateRequest(
            email=email,
            name=name,
            metadata={}  # V2 requires metadata, provide empty
        )
        
        v2_response = await self.v2_service.create_user(create_request)
        
        # Convert V2 response to V1 format
        return User(
            id=v2_response.user.id,
            email=v2_response.user.email,
            name=v2_response.user.name,
            status=self._convert_status_v2_to_v1(v2_response.user.status),
            created_at=v2_response.user.created_at
        )
    
    def _convert_status_v2_to_v1(self, v2_status: str) -> str:
        """Convert V2 status to V1 status."""
        status_mapping = {
            "enabled": "active",
            "disabled": "inactive",
            "archived": "suspended"
        }
        return status_mapping.get(v2_status, "inactive")
```

### Multi-Version Support

```python
from typing import Union

# Support multiple versions simultaneously
class MultiVersionUserService:
    """Service supporting multiple protocol versions."""
    
    def __init__(self):
        self.v1_implementations: list[ProtocolUserServiceV1] = []
        self.v2_implementations: list[ProtocolUserServiceV2] = []
        self.default_version = "v2"
    
    def register_v1_implementation(self, service: ProtocolUserServiceV1):
        """Register V1 service implementation."""
        self.v1_implementations.append(service)
    
    def register_v2_implementation(self, service: ProtocolUserServiceV2):
        """Register V2 service implementation."""
        self.v2_implementations.append(service)
    
    def get_service_v1(self) -> ProtocolUserServiceV1:
        """Get V1 service (with V2→V1 adapter if needed)."""
        if self.v1_implementations:
            return self.v1_implementations[0]
        elif self.v2_implementations:
            # Use adapter to provide V1 interface from V2 service
            return UserServiceV2ToV1Adapter(self.v2_implementations[0])
        else:
            raise ValueError("No user service implementations available")
    
    def get_service_v2(self) -> ProtocolUserServiceV2:
        """Get V2 service (with V1→V2 adapter if needed)."""
        if self.v2_implementations:
            return self.v2_implementations[0]
        elif self.v1_implementations:
            # Use adapter to provide V2 interface from V1 service
            return UserServiceV1ToV2Adapter(self.v1_implementations[0])
        else:
            raise ValueError("No user service implementations available")
    
    def get_service(
        self,
        version: str = None
    ) -> Union[ProtocolUserServiceV1, ProtocolUserServiceV2]:
        """Get service for specified version."""
        version = version or self.default_version
        
        if version == "v1":
            return self.get_service_v1()
        elif version == "v2":
            return self.get_service_v2()
        else:
            raise ValueError(f"Unsupported version: {version}")
```

## Production Migration

### Blue-Green Deployment Strategy

```python
# Blue-Green deployment with protocol versioning
class BlueGreenMigrationManager:
    """Manage blue-green migration of protocol services."""
    
    def __init__(
        self,
        blue_container: ServiceContainer,  # Current version
        green_container: ServiceContainer,  # New version
        feature_flags: ProtocolFeatureFlags
    ):
        self.blue_container = blue_container
        self.green_container = green_container
        self.feature_flags = feature_flags
        self.migration_percentage = 0
    
    async def route_request(
        self,
        protocol_type: type,
        context: dict[str, str] = None
    ):
        """Route request to blue or green environment."""
        # Check feature flag for this protocol
        use_green = await self.feature_flags.is_enabled(
            f"use_green_{protocol_type.__name__}",
            context=context or {}
        )
        
        if use_green:
            return self.green_container.get(protocol_type)
        else:
            return self.blue_container.get(protocol_type)
    
    async def gradual_migration(
        self,
        protocol_type: type,
        percentage_step: int = 10
    ):
        """Gradually migrate traffic to green environment."""
        while self.migration_percentage < 100:
            self.migration_percentage += percentage_step
            
            # Update feature flag to route X% of traffic to green
            await self.feature_flags.set_percentage(
                f"use_green_{protocol_type.__name__}",
                self.migration_percentage
            )
            
            # Wait and monitor metrics
            await asyncio.sleep(300)  # 5 minutes between steps
            
            # Check health metrics
            if not await self._check_green_health():
                # Rollback on issues
                await self._rollback_migration(protocol_type)
                break
    
    async def _check_green_health(self) -> bool:
        """Check health of green environment."""
        # Implementation specific health checks
        return True
    
    async def _rollback_migration(self, protocol_type: type):
        """Rollback migration to blue environment."""
        await self.feature_flags.disable(f"use_green_{protocol_type.__name__}")
        self.migration_percentage = 0
```

### Canary Deployment

```python
class CanaryMigrationManager:
    """Manage canary deployment of new protocol versions."""
    
    def __init__(
        self,
        stable_service: ProtocolUserService,
        canary_service: ProtocolUserService,
        canary_percentage: float = 5.0
    ):
        self.stable_service = stable_service
        self.canary_service = canary_service
        self.canary_percentage = canary_percentage
        self.metrics_collector = MetricsCollector()
    
    async def route_request(self, user_id: UUID, operation: str) -> ProtocolUserService:
        """Route request to stable or canary service."""
        # Use consistent hashing for user-based routing
        if self._should_use_canary(user_id):
            await self.metrics_collector.increment("canary.requests", {
                "operation": operation
            })
            return self.canary_service
        else:
            await self.metrics_collector.increment("stable.requests", {
                "operation": operation
            })
            return self.stable_service
    
    def _should_use_canary(self, user_id: UUID) -> bool:
        """Determine if request should use canary service."""
        # Consistent hashing based on user ID
        hash_value = hash(str(user_id)) % 100
        return hash_value < self.canary_percentage
    
    async def monitor_and_adjust(self):
        """Monitor canary metrics and adjust traffic."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            
            # Get error rates
            canary_errors = await self.metrics_collector.get_error_rate("canary")
            stable_errors = await self.metrics_collector.get_error_rate("stable")
            
            # If canary error rate is significantly higher, reduce traffic
            if canary_errors > stable_errors * 2:
                self.canary_percentage = max(0, self.canary_percentage - 1)
                print(f"Reducing canary traffic to {self.canary_percentage}%")
            
            # If canary is performing well, increase traffic
            elif canary_errors <= stable_errors:
                self.canary_percentage = min(100, self.canary_percentage + 1)
                print(f"Increasing canary traffic to {self.canary_percentage}%")
```

## Testing Migration

### Migration Test Suite

```python
class MigrationTestSuite:
    """Comprehensive test suite for protocol migrations."""
    
    def __init__(
        self,
        old_service: ProtocolUserServiceV1,
        new_service: ProtocolUserServiceV2,
        migration_adapter: UserServiceV1ToV2Migration
    ):
        self.old_service = old_service
        self.new_service = new_service
        self.migration_adapter = migration_adapter
    
    async def test_data_consistency(self):
        """Test that migrated data maintains consistency."""
        # Create test data in old format
        v1_user = await self.old_service.create_user("test@example.com", "Test User")
        
        # Migrate data
        v2_user = self.migration_adapter.convert_user_to_v2(v1_user)
        
        # Verify data consistency
        assert v2_user.id == v1_user.id
        assert v2_user.email == v1_user.email
        assert v2_user.name == v1_user.name
        
        # Verify status mapping
        expected_v2_status = self.migration_adapter.convert_user_status(v1_user.status)
        assert v2_user.status == expected_v2_status
    
    async def test_functionality_equivalence(self):
        """Test that migrated service provides equivalent functionality."""
        # Test with adapter
        adapter = UserServiceV2ToV1Adapter(self.new_service)
        
        # Create user through adapter (V1 interface → V2 service)
        v1_user = await adapter.create_user("adapter@example.com", "Adapter User")
        
        # Verify user can be retrieved
        retrieved_user = await adapter.get_user(v1_user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == "adapter@example.com"
    
    async def test_performance_regression(self):
        """Test that migration doesn't introduce performance regressions."""
        import time
        
        # Benchmark old service
        start_time = time.time()
        for i in range(100):
            await self.old_service.create_user(f"perf{i}@example.com", f"User {i}")
        old_service_time = time.time() - start_time
        
        # Benchmark new service (through adapter)
        adapter = UserServiceV2ToV1Adapter(self.new_service)
        start_time = time.time()
        for i in range(100):
            await adapter.create_user(f"perf_new{i}@example.com", f"User {i}")
        new_service_time = time.time() - start_time
        
        # Allow up to 20% performance regression
        assert new_service_time <= old_service_time * 1.2, (
            f"Performance regression: {new_service_time:.2f}s vs {old_service_time:.2f}s"
        )
    
    async def test_error_handling_compatibility(self):
        """Test that error handling remains consistent."""
        # Test duplicate email error in both versions
        await self.old_service.create_user("error@example.com", "Error User")
        
        with pytest.raises(ValueError, match="already exists"):
            await self.old_service.create_user("error@example.com", "Duplicate")
        
        # Test same error through adapter
        adapter = UserServiceV2ToV1Adapter(self.new_service)
        
        with pytest.raises(ValueError, match="already exists"):
            await adapter.create_user("error@example.com", "Duplicate New")

# Integration test for complete migration workflow
@pytest.mark.integration
async def test_complete_migration_workflow():
    """Test complete migration from V1 to V2."""
    # Setup V1 service with test data
    v1_service = create_test_user_service_v1()
    await v1_service.create_user("migrate@example.com", "Migration User")
    
    # Setup migration helper
    migration = UserServiceV1ToV2Migration(v1_service)
    
    # Perform migration
    await migration.migrate_user_data()
    
    # Setup V2 service
    v2_service = create_test_user_service_v2()
    
    # Verify migrated data is accessible in V2
    v2_users = await v2_service.list_users_detailed()
    assert len(v2_users) == 1
    assert v2_users[0].email == "migrate@example.com"
    
    # Test migration test suite
    test_suite = MigrationTestSuite(v1_service, v2_service, migration)
    await test_suite.test_data_consistency()
    await test_suite.test_functionality_equivalence()
    await test_suite.test_performance_regression()
    await test_suite.test_error_handling_compatibility()
```

## Summary

This migration guide provides comprehensive strategies for:

1. **Version Planning**: Assess current usage and plan migration strategy
2. **Protocol Evolution**: Handle backward-compatible and breaking changes
3. **Compatibility**: Maintain backward compatibility with adapters
4. **Production Migration**: Blue-green and canary deployment strategies
5. **Testing**: Comprehensive migration testing frameworks

**Key Migration Principles:**

- **Plan Thoroughly**: Assess impact before starting migration
- **Gradual Migration**: Use feature flags and percentage rollouts
- **Maintain Compatibility**: Use adapters during transition periods
- **Test Comprehensively**: Verify functionality, performance, and error handling
- **Monitor Continuously**: Track metrics during migration
- **Rollback Ready**: Always have rollback plans for critical issues

These strategies enable safe, reliable migration between protocol versions while maintaining system stability and user experience.

---

*For specific protocol documentation, see the [API Reference](api-reference/). For implementation patterns, see the [Developer Guide](developer-guide/).*