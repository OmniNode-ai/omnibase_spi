# Developer Guide

## Overview

Comprehensive guide for developers using, implementing, and extending the omnibase-spi Service Provider Interface. This guide covers everything from initial setup to advanced protocol implementation patterns.

## Who This Guide Is For

### New to ONEX SPI
If you're new to the ONEX ecosystem or Service Provider Interfaces:
1. Start with [Quick Start Guide](../quick-start.md)
2. Read [Core Concepts](#core-concepts) below
3. Follow the [Development Setup](#development-setup)
4. Work through [Your First Protocol Implementation](#your-first-protocol-implementation)

### Experienced Developers
If you're familiar with protocol-based architectures:
1. Review [Development Setup](#development-setup) for tool configuration
2. Check [Protocol Implementation Patterns](#protocol-implementation-patterns)
3. Explore [Advanced Topics](#advanced-topics)
4. Reference [Best Practices](#best-practices)

### Framework Integrators
If you're integrating omnibase-spi with existing frameworks:
1. Read [Integration Patterns](#integration-patterns)  
2. Review [Dependency Injection](#dependency-injection)
3. Check [Framework-Specific Guides](#framework-specific-guides)
4. See [Testing Strategies](#testing-strategies)

## Core Concepts

### Service Provider Interface (SPI) Architecture

The omnibase-spi follows a pure SPI architecture pattern:

```python
# Protocol Definition (SPI Layer)
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProtocolUserService(Protocol):
    """Protocol for user management operations."""
    
    async def get_user(self, user_id: str) -> Optional["User"]:
        """Get user by ID."""
        ...

# Implementation (Separate Package)
from omnibase_spi.protocols.user import ProtocolUserService

class DatabaseUserService(ProtocolUserService):
    """Database-backed user service implementation."""
    
    async def get_user(self, user_id: str) -> Optional[User]:
        return await self.db.fetch_user(user_id)
```

**Key Principles:**
- **Interface Segregation**: Protocols define only what clients need
- **Dependency Inversion**: Depend on abstractions, not implementations  
- **Runtime Checking**: Use `isinstance(obj, Protocol)` for validation
- **Type Safety**: Full mypy compatibility with strict checking
- **Zero Dependencies**: Protocols have no runtime dependencies

### Protocol vs Implementation Separation

```python
# ✅ SPI Layer - Pure protocols only
from typing import Protocol

class ProtocolEventBus(Protocol):
    async def publish(self, event: dict) -> None: ...
    async def subscribe(self, handler: Callable) -> None: ...

# ✅ Implementation Layer - Concrete implementations  
from omnibase_spi.protocols.event_bus import ProtocolEventBus

class RedisEventBus(ProtocolEventBus):
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def publish(self, event: dict) -> None:
        await self.redis.publish("events", json.dumps(event))

# ❌ Never mix protocols and implementations
class BadEventBus(ProtocolEventBus):
    """Don't do this - mixing protocol and implementation"""
    
    def __init__(self):
        self.redis = redis.Redis()  # Concrete dependency in protocol
    
    async def publish(self, event: dict) -> None:
        # Actual implementation in protocol layer
        await self.redis.publish("events", json.dumps(event))
```

### Namespace Isolation

The omnibase-spi maintains strict namespace isolation:

```python
# ✅ ALLOWED - SPI-only imports
from omnibase_spi.protocols.core import ProtocolLogger
from omnibase_spi.protocols.types.core_types import LogLevel

# ✅ ALLOWED - Forward references with TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types.workflow_types import WorkflowState

# ❌ FORBIDDEN - Implementation imports
from omnibase_spi.core.services import LoggerService  # Breaks SPI purity
from redis import Redis  # External implementation dependency
```

## Development Setup

### Prerequisites

- **Python**: 3.11, 3.12, or 3.13
- **Poetry**: For dependency management
- **Git**: For version control
- **IDE**: VS Code, PyCharm, or similar with Python support

### Installation

#### 1. Clone and Install

```bash
# Clone repository
git clone <omnibase-spi-repo>
cd omnibase-spi

# Install with Poetry
poetry install

# Verify installation
poetry run python -c "import omnibase_spi.protocols; print('✅ Installation successful')"
```

#### 2. Development Dependencies

```bash
# Install development dependencies
poetry install --with dev

# Setup pre-commit hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push -c .pre-commit-config-push.yaml

# Verify setup
poetry run pytest tests/test_protocol_imports.py -v
poetry run mypy src/ --strict
```

#### 3. IDE Configuration

**VS Code (`settings.json`):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.mypyArgs": ["--strict", "--show-error-codes"],
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

**PyCharm:**
- Configure Poetry interpreter: Settings → Project → Python Interpreter
- Enable mypy: Settings → Tools → External Tools → Add mypy
- Configure Black formatter: Settings → Tools → External Tools → Add black

### Validation Tools

#### SPI Purity Validation

```bash
# Validate namespace isolation
./scripts/validate-namespace-isolation.sh

# AST-based protocol validation
poetry run python scripts/ast_spi_validator.py

# Check for forbidden patterns
./scripts/validate-forbidden-patterns.sh
```

#### Type Checking

```bash
# Strict type checking
poetry run mypy src/ --strict

# Specific protocol checking
poetry run mypy src/omnibase/protocols/workflow_orchestration/ --strict
```

#### Testing

```bash
# Run all tests
poetry run pytest

# Test protocol imports
poetry run pytest tests/test_protocol_imports.py -v

# Test with coverage
poetry run pytest --cov=src/omnibase/protocols --cov-report=html
```

## Your First Protocol Implementation

### Step 1: Define the Protocol

Create a new protocol in the appropriate domain:

```python
# src/omnibase/protocols/example/protocol_user_service.py
from typing import Optional, Protocol, runtime_checkable, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.example_types import User, UserFilter

@runtime_checkable
class ProtocolUserService(Protocol):
    """
    Protocol for user management operations.
    
    Provides user CRUD operations with filtering and validation
    capabilities for distributed user management systems.
    
    Key Features:
        - **User Management**: Create, read, update, delete operations
        - **Filtering**: Advanced user filtering capabilities
        - **Validation**: Input validation with detailed error reporting
        - **Async Support**: Full async/await support for scalability
    
    Example:
        ```python
        async def manage_users(service: ProtocolUserService):
            # Create user
            user = await service.create_user(
                email="user@example.com",
                name="John Doe"
            )
            
            # Get user
            retrieved_user = await service.get_user(user.id)
            
            # Update user
            await service.update_user(user.id, {"name": "Jane Doe"})
            
            # List users
            users = await service.list_users(
                filter_criteria={"active": True}
            )
        ```
    """
    
    async def create_user(
        self, 
        email: str, 
        name: str,
        metadata: Optional[dict[str, str]] = None
    ) -> "User":
        """
        Create a new user.
        
        Args:
            email: User email address (must be unique)
            name: User display name
            metadata: Optional user metadata
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        ...
    
    async def get_user(self, user_id: UUID) -> Optional["User"]:
        """
        Get user by ID.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User object or None if not found
        """
        ...
    
    async def list_users(
        self,
        filter_criteria: Optional["UserFilter"] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list["User"]:
        """
        List users with optional filtering.
        
        Args:
            filter_criteria: Optional filter criteria
            limit: Maximum users to return
            offset: Number of users to skip
            
        Returns:
            List of matching users
        """
        ...
    
    async def update_user(
        self, 
        user_id: UUID, 
        updates: dict[str, str]
    ) -> bool:
        """
        Update user information.
        
        Args:
            user_id: User to update
            updates: Fields to update
            
        Returns:
            True if update successful
            
        Raises:
            ValueError: If user not found or validation fails
        """
        ...
    
    async def delete_user(self, user_id: UUID) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User to delete
            
        Returns:
            True if deletion successful
        """
        ...
```

### Step 2: Define Supporting Types

```python
# src/omnibase/protocols/types/example_types.py
from typing import Literal, Optional, Protocol
from uuid import UUID
from datetime import datetime

UserStatus = Literal["active", "inactive", "suspended", "deleted"]

class User(Protocol):
    """Protocol for user data objects."""
    
    id: UUID
    email: str
    name: str
    status: UserStatus
    created_at: datetime
    updated_at: Optional[datetime]
    metadata: dict[str, str]

class UserFilter(Protocol):
    """Protocol for user filtering criteria."""
    
    status: Optional[UserStatus]
    email_contains: Optional[str]
    created_after: Optional[datetime]
    created_before: Optional[datetime]
    has_metadata_key: Optional[str]
```

### Step 3: Update Package Imports

```python
# src/omnibase/protocols/example/__init__.py
"""Example domain protocol interfaces."""

from .protocol_user_service import ProtocolUserService

__all__ = ["ProtocolUserService"]

# src/omnibase/protocols/types/__init__.py  
from .example_types import User, UserFilter, UserStatus

__all__ = [
    # ... existing exports
    "User", "UserFilter", "UserStatus"
]
```

### Step 4: Create Implementation Tests

```python
# tests/test_user_service_protocol.py
import pytest
from uuid import uuid4
from omnibase_spi.protocols.example import ProtocolUserService
from omnibase_spi.protocols.types.example_types import User, UserFilter

class MockUser(User):
    """Test user implementation."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockUserService(ProtocolUserService):
    """Test implementation of user service protocol."""
    
    def __init__(self):
        self.users: dict[UUID, MockUser] = {}
    
    async def create_user(self, email: str, name: str, metadata=None):
        user_id = uuid4()
        user = MockUser(
            id=user_id,
            email=email,
            name=name,
            status="active",
            created_at=datetime.now(),
            updated_at=None,
            metadata=metadata or {}
        )
        self.users[user_id] = user
        return user
    
    async def get_user(self, user_id: UUID):
        return self.users.get(user_id)
    
    # ... implement other methods

def test_protocol_compliance():
    """Test that mock implementation satisfies protocol."""
    mock_service = MockUserService()
    assert isinstance(mock_service, ProtocolUserService)

@pytest.mark.asyncio
async def test_user_creation():
    """Test user creation functionality."""
    service = MockUserService()
    
    user = await service.create_user(
        email="test@example.com",
        name="Test User"
    )
    
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.status == "active"
    
    # Verify retrieval
    retrieved_user = await service.get_user(user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == user.email
```

### Step 5: Validate Implementation

```bash
# Run validation tools
poetry run python scripts/ast_spi_validator.py
poetry run mypy src/ --strict
poetry run pytest tests/test_user_service_protocol.py -v

# Validate namespace isolation  
./scripts/validate-namespace-isolation.sh
```

## Protocol Implementation Patterns

### Dependency Injection Pattern

```python
# Service container with protocol contracts
from typing import TypeVar, Type, Dict, Any

T = TypeVar('T')

class ServiceContainer:
    """Simple service container for protocol-based DI."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, protocol: Type[T], implementation: T) -> None:
        """Register implementation for protocol."""
        if not isinstance(implementation, protocol):
            raise ValueError(f"Implementation must satisfy {protocol}")
        self._services[protocol] = implementation
    
    def register_singleton(self, protocol: Type[T], implementation: T) -> None:
        """Register singleton implementation."""
        self.register(protocol, implementation)
        self._singletons[protocol] = implementation
    
    def get(self, protocol: Type[T]) -> T:
        """Get implementation for protocol."""
        if protocol in self._singletons:
            return self._singletons[protocol]
        
        if protocol in self._services:
            impl_class = self._services[protocol]
            if isinstance(impl_class, type):
                return impl_class()  # Instantiate if class
            return impl_class  # Return instance
        
        raise ValueError(f"No implementation registered for {protocol}")

# Usage
container = ServiceContainer()
container.register(ProtocolUserService, DatabaseUserService)
container.register_singleton(ProtocolLogger, ConsoleLogger())

user_service = container.get(ProtocolUserService)
logger = container.get(ProtocolLogger)
```

### Factory Pattern

```python
from typing import Protocol, runtime_checkable
from abc import ABC

@runtime_checkable
class ProtocolServiceFactory(Protocol):
    """Protocol for service factory implementations."""
    
    def create_user_service(self) -> ProtocolUserService:
        """Create user service implementation."""
        ...
    
    def create_logger(self) -> ProtocolLogger:
        """Create logger implementation."""
        ...

class ProductionServiceFactory(ProtocolServiceFactory):
    """Production service factory."""
    
    def __init__(self, config: dict):
        self.config = config
    
    def create_user_service(self) -> ProtocolUserService:
        return DatabaseUserService(
            connection_string=self.config["database_url"]
        )
    
    def create_logger(self) -> ProtocolLogger:
        return StructuredLogger(
            level=self.config.get("log_level", "INFO")
        )

class TestServiceFactory(ProtocolServiceFactory):
    """Test service factory with mocks."""
    
    def create_user_service(self) -> ProtocolUserService:
        return MockUserService()
    
    def create_logger(self) -> ProtocolLogger:
        return MockLogger()

# Factory selection
def create_factory(environment: str) -> ProtocolServiceFactory:
    if environment == "production":
        return ProductionServiceFactory(load_config())
    elif environment == "test":
        return TestServiceFactory()
    else:
        raise ValueError(f"Unknown environment: {environment}")
```

### Adapter Pattern

```python
# Adapt third-party libraries to protocols
from external_user_lib import ExternalUserAPI

class ExternalUserServiceAdapter(ProtocolUserService):
    """Adapt external user API to our protocol."""
    
    def __init__(self, api_client: ExternalUserAPI):
        self.client = api_client
    
    async def create_user(self, email: str, name: str, metadata=None):
        # Adapt external API call to our protocol
        result = await self.client.users.create({
            "email_address": email,  # Different field name
            "full_name": name,
            "custom_fields": metadata or {}
        })
        
        # Convert external format to our protocol
        return User(
            id=UUID(result["user_id"]),
            email=result["email_address"],
            name=result["full_name"],
            status="active" if result["is_active"] else "inactive",
            created_at=datetime.fromisoformat(result["created_timestamp"]),
            updated_at=None,
            metadata=result.get("custom_fields", {})
        )
    
    async def get_user(self, user_id: UUID):
        try:
            result = await self.client.users.get(str(user_id))
            return self._convert_external_user(result)
        except ExternalUserAPI.NotFound:
            return None
    
    def _convert_external_user(self, external_user: dict) -> User:
        """Convert external user format to protocol format."""
        return User(
            id=UUID(external_user["user_id"]),
            email=external_user["email_address"],
            name=external_user["full_name"],
            status="active" if external_user["is_active"] else "inactive",
            created_at=datetime.fromisoformat(external_user["created_timestamp"]),
            updated_at=datetime.fromisoformat(external_user["updated_timestamp"]) 
                       if external_user.get("updated_timestamp") else None,
            metadata=external_user.get("custom_fields", {})
        )
```

## Advanced Topics

### Event Sourcing with Protocols

```python
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolWorkflowEventBus,
    ProtocolWorkflowEventHandler
)

class UserEventHandler(ProtocolWorkflowEventHandler):
    """Handle user-related workflow events."""
    
    def __init__(self, user_service: ProtocolUserService):
        self.user_service = user_service
    
    async def __call__(self, event: ProtocolWorkflowEvent, context: dict):
        if event.event_type == "user.creation_requested":
            await self._handle_user_creation(event)
        elif event.event_type == "user.update_requested":
            await self._handle_user_update(event)
    
    async def _handle_user_creation(self, event: ProtocolWorkflowEvent):
        """Handle user creation event."""
        user_data = event.data
        
        try:
            user = await self.user_service.create_user(
                email=user_data["email"],
                name=user_data["name"],
                metadata=user_data.get("metadata")
            )
            
            # Publish success event
            success_event = ProtocolWorkflowEvent(
                event_type="user.created",
                workflow_type=event.workflow_type,
                instance_id=event.instance_id,
                sequence_number=event.sequence_number + 1,
                causation_id=event.event_id,
                data={"user_id": str(user.id), "email": user.email}
            )
            
        except Exception as e:
            # Publish failure event
            failure_event = ProtocolWorkflowEvent(
                event_type="user.creation_failed",
                workflow_type=event.workflow_type,
                instance_id=event.instance_id,
                sequence_number=event.sequence_number + 1,
                causation_id=event.event_id,
                data={"error": str(e), "email": user_data["email"]}
            )

# Setup event handling
async def setup_user_event_handling(
    event_bus: ProtocolWorkflowEventBus,
    user_service: ProtocolUserService
):
    handler = UserEventHandler(user_service)
    
    await event_bus.subscribe_to_workflow_events(
        workflow_type="user_management",
        event_types=["user.creation_requested", "user.update_requested"],
        handler=handler,
        group_id="user_service_handlers"
    )
```

### Multi-Protocol Composition

```python
class CompositeUserManager:
    """Compose multiple protocols for complex user management."""
    
    def __init__(
        self,
        user_service: ProtocolUserService,
        logger: ProtocolLogger,
        event_bus: ProtocolWorkflowEventBus,
        cache: ProtocolCacheService
    ):
        self.user_service = user_service
        self.logger = logger
        self.event_bus = event_bus
        self.cache = cache
    
    async def create_user_with_workflow(
        self,
        email: str,
        name: str,
        workflow_instance_id: UUID
    ) -> User:
        """Create user with full workflow integration."""
        
        correlation_id = uuid4()
        
        # Log operation start
        await self.logger.info(
            "Starting user creation workflow",
            context={
                "email": email,
                "correlation_id": str(correlation_id),
                "workflow_instance_id": str(workflow_instance_id)
            }
        )
        
        try:
            # Check cache first
            cache_key = f"user_creation:{email}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Create user
            user = await self.user_service.create_user(email, name)
            
            # Cache result
            await self.cache.set(cache_key, user, ttl_seconds=300)
            
            # Publish workflow event
            creation_event = ProtocolWorkflowEvent(
                event_type="user.created",
                workflow_type="user_onboarding",
                instance_id=workflow_instance_id,
                sequence_number=1,
                correlation_chain=[correlation_id],
                data={
                    "user_id": str(user.id),
                    "email": user.email,
                    "name": user.name
                }
            )
            await self.event_bus.publish_workflow_event(creation_event)
            
            # Log success
            await self.logger.info(
                "User creation completed successfully",
                context={
                    "user_id": str(user.id),
                    "email": email,
                    "correlation_id": str(correlation_id)
                }
            )
            
            return user
            
        except Exception as e:
            # Log error
            await self.logger.error(
                "User creation failed",
                context={
                    "email": email,
                    "error": str(e),
                    "correlation_id": str(correlation_id)
                }
            )
            
            # Publish failure event
            failure_event = ProtocolWorkflowEvent(
                event_type="user.creation_failed",
                workflow_type="user_onboarding",
                instance_id=workflow_instance_id,
                sequence_number=1,
                correlation_chain=[correlation_id],
                data={"error": str(e), "email": email}
            )
            await self.event_bus.publish_workflow_event(failure_event)
            
            raise
```

## Integration Patterns

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from omnibase_spi.protocols.example import ProtocolUserService

app = FastAPI()

# Dependency injection setup
def get_user_service() -> ProtocolUserService:
    """FastAPI dependency for user service."""
    return container.get(ProtocolUserService)

@app.post("/users")
async def create_user(
    user_data: dict,
    user_service: ProtocolUserService = Depends(get_user_service)
):
    """Create user endpoint."""
    try:
        user = await user_service.create_user(
            email=user_data["email"],
            name=user_data["name"]
        )
        return {"user_id": str(user.id), "email": user.email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    user_service: ProtocolUserService = Depends(get_user_service)
):
    """Get user endpoint."""
    user = await user_service.get_user(UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": str(user.id),
        "email": user.email,
        "name": user.name,
        "status": user.status
    }
```

### Django Integration

```python
# django_integration/protocols.py
from django.conf import settings
from omnibase_spi.protocols.example import ProtocolUserService
from .services import DjangoUserService

def get_user_service() -> ProtocolUserService:
    """Get user service based on Django settings."""
    if settings.DEBUG:
        from .mock_services import MockUserService
        return MockUserService()
    else:
        return DjangoUserService()

# django_integration/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .protocols import get_user_service

@require_http_methods(["POST"])
async def create_user(request):
    """Create user view."""
    user_service = get_user_service()
    
    data = json.loads(request.body)
    user = await user_service.create_user(
        email=data["email"],
        name=data["name"]
    )
    
    return JsonResponse({
        "user_id": str(user.id),
        "email": user.email
    })
```

## Testing Strategies

### Protocol Compliance Testing

```python
import pytest
from abc import ABC
from typing import get_args
from omnibase_spi.protocols.example import ProtocolUserService

class UserServiceComplianceTests(ABC):
    """Abstract test suite for user service protocol compliance."""
    
    @pytest.fixture
    def user_service(self) -> ProtocolUserService:
        """Override in subclasses to provide implementation."""
        raise NotImplementedError
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service: ProtocolUserService):
        """Test successful user creation."""
        user = await user_service.create_user(
            email="test@example.com",
            name="Test User"
        )
        
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.status in get_args(UserStatus)  # Valid status
        assert user.id is not None
    
    @pytest.mark.asyncio
    async def test_get_user_existing(self, user_service: ProtocolUserService):
        """Test retrieving existing user."""
        # Create user first
        created_user = await user_service.create_user(
            email="existing@example.com",
            name="Existing User"
        )
        
        # Retrieve user
        retrieved_user = await user_service.get_user(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_nonexistent(self, user_service: ProtocolUserService):
        """Test retrieving non-existent user."""
        non_existent_id = uuid4()
        user = await user_service.get_user(non_existent_id)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service: ProtocolUserService):
        """Test creating user with duplicate email."""
        email = "duplicate@example.com"
        
        # Create first user
        await user_service.create_user(email=email, name="First User")
        
        # Try to create second user with same email
        with pytest.raises(ValueError):
            await user_service.create_user(email=email, name="Second User")

# Concrete test implementations
class TestMockUserService(UserServiceComplianceTests):
    @pytest.fixture
    def user_service(self):
        return MockUserService()

class TestDatabaseUserService(UserServiceComplianceTests):
    @pytest.fixture
    def user_service(self):
        return DatabaseUserService(connection_string="sqlite:///:memory:")
```

### Integration Testing

```python
@pytest.mark.integration
class TestUserServiceIntegration:
    """Integration tests with real dependencies."""
    
    @pytest.fixture
    async def services(self):
        """Setup real service dependencies."""
        # Setup real database, cache, etc.
        db_service = DatabaseUserService("postgresql://test_db")
        cache_service = RedisCache("redis://localhost:6379/0")
        logger = StructuredLogger(level="DEBUG")
        
        return {
            "user_service": db_service,
            "cache": cache_service,
            "logger": logger
        }
    
    @pytest.mark.asyncio
    async def test_user_lifecycle_integration(self, services):
        """Test complete user lifecycle with all services."""
        user_service = services["user_service"]
        cache = services["cache"]
        logger = services["logger"]
        
        # Create composite manager
        manager = CompositeUserManager(
            user_service=user_service,
            logger=logger,
            cache=cache,
            event_bus=MockEventBus()  # Could be real for full integration
        )
        
        # Test user creation workflow
        workflow_id = uuid4()
        user = await manager.create_user_with_workflow(
            email="integration@example.com",
            name="Integration User",
            workflow_instance_id=workflow_id
        )
        
        # Verify user exists in database
        db_user = await user_service.get_user(user.id)
        assert db_user is not None
        
        # Verify caching worked
        cache_key = f"user_creation:integration@example.com"
        cached_user = await cache.get(cache_key)
        assert cached_user is not None
```

### Mock and Stub Patterns

```python
class MockUserService(ProtocolUserService):
    """Mock implementation for testing."""
    
    def __init__(self):
        self.users: dict[UUID, User] = {}
        self.call_log: list[dict] = []
    
    async def create_user(self, email: str, name: str, metadata=None):
        # Log call for test assertions
        self.call_log.append({
            "method": "create_user",
            "args": {"email": email, "name": name, "metadata": metadata}
        })
        
        # Simulate email uniqueness constraint
        for user in self.users.values():
            if user.email == email:
                raise ValueError(f"User with email {email} already exists")
        
        user = MockUser(
            id=uuid4(),
            email=email,
            name=name,
            status="active",
            created_at=datetime.now(),
            updated_at=None,
            metadata=metadata or {}
        )
        self.users[user.id] = user
        return user
    
    def assert_create_user_called_with(self, email: str, name: str):
        """Test helper for verifying calls."""
        for call in self.call_log:
            if (call["method"] == "create_user" and 
                call["args"]["email"] == email and
                call["args"]["name"] == name):
                return True
        raise AssertionError(f"create_user not called with email={email}, name={name}")

# Usage in tests
def test_user_manager_calls_user_service():
    mock_service = MockUserService()
    manager = UserManager(user_service=mock_service)
    
    await manager.register_user("test@example.com", "Test User")
    
    # Verify the service was called correctly
    mock_service.assert_create_user_called_with("test@example.com", "Test User")
```

## Best Practices

### Protocol Design

#### Do: Single Responsibility

```python
# Good - focused on user operations only
class ProtocolUserService(Protocol):
    async def create_user(self, email: str, name: str) -> User: ...
    async def get_user(self, user_id: UUID) -> Optional[User]: ...
    async def update_user(self, user_id: UUID, updates: dict) -> bool: ...

# Good - focused on logging only  
class ProtocolLogger(Protocol):
    async def info(self, message: str, context: dict) -> None: ...
    async def error(self, message: str, context: dict) -> None: ...

# Avoid - mixing responsibilities
class ProtocolUserLogger(Protocol):  # Bad - mixed concerns
    async def create_user(self, email: str) -> User: ...
    async def log_user_creation(self, user: User) -> None: ...
```

#### Do: Rich Type Information

```python
# Good - specific types with validation
async def create_user(
    self,
    email: str,  # Specific type
    name: str,   # Specific type
    status: UserStatus = "active",  # Literal type with default
    metadata: Optional[dict[str, str]] = None  # Specific dict type
) -> User:  # Specific return type
    ...

# Avoid - generic types
async def create_user(self, data: dict) -> Any:  # Too generic
    ...
```

#### Do: Comprehensive Documentation

```python
@runtime_checkable
class ProtocolPaymentService(Protocol):
    """
    Payment processing service protocol.
    
    Handles secure payment transactions with support for multiple
    payment methods, refunds, and transaction monitoring.
    
    Key Features:
        - **Multi-Payment Methods**: Credit card, PayPal, bank transfer
        - **Security**: PCI DSS compliant transaction handling
        - **Refund Support**: Full and partial refund capabilities
        - **Transaction Tracking**: Complete audit trail
        - **Async Processing**: Non-blocking payment operations
    
    Security Considerations:
        - Never log sensitive payment data
        - Use secure tokenization for card storage
        - Implement proper error handling to prevent data leakage
    
    Example:
        ```python
        async def process_order(payment_service: ProtocolPaymentService):
            # Process payment
            transaction = await payment_service.charge_card(
                amount=Decimal("99.99"),
                currency="USD",
                card_token="tok_abc123",
                description="Order #12345"
            )
            
            if transaction.status == "completed":
                print(f"Payment successful: {transaction.id}")
            else:
                print(f"Payment failed: {transaction.error_message}")
        ```
    """
```

### Implementation Guidelines

#### Use Composition Over Inheritance

```python
# Good - composition pattern
class EnhancedUserService:
    """Enhanced user service using composition."""
    
    def __init__(
        self,
        user_service: ProtocolUserService,
        logger: ProtocolLogger,
        cache: ProtocolCacheService
    ):
        self._user_service = user_service
        self._logger = logger
        self._cache = cache
    
    async def create_user_with_caching(self, email: str, name: str) -> User:
        # Check cache first
        cached_user = await self._cache.get(f"user:email:{email}")
        if cached_user:
            return cached_user
        
        # Create user
        user = await self._user_service.create_user(email, name)
        
        # Cache result
        await self._cache.set(f"user:{user.id}", user, ttl_seconds=3600)
        
        # Log creation
        await self._logger.info(
            "User created",
            context={"user_id": str(user.id), "email": email}
        )
        
        return user

# Avoid - inheritance mixing concerns
class CachedUserService(DatabaseUserService):  # Tight coupling
    def __init__(self, db_connection, cache_client):
        super().__init__(db_connection)
        self.cache = cache_client  # Mixed concerns
```

#### Handle Errors Appropriately

```python
class RobustUserService(ProtocolUserService):
    """User service with comprehensive error handling."""
    
    async def create_user(self, email: str, name: str, metadata=None):
        try:
            # Validate input
            if not email or "@" not in email:
                raise ValueError("Invalid email address")
            
            if not name or len(name.strip()) == 0:
                raise ValueError("Name cannot be empty")
            
            # Check for existing user
            existing = await self._find_user_by_email(email)
            if existing:
                raise ValueError(f"User with email {email} already exists")
            
            # Create user
            user = await self._create_user_in_database(email, name, metadata)
            return user
            
        except DatabaseError as e:
            # Log and re-raise as appropriate exception type
            await self._logger.error(
                "Database error during user creation",
                context={"email": email, "error": str(e)}
            )
            raise RuntimeError("Failed to create user due to database error") from e
        
        except ValidationError as e:
            # Log validation errors
            await self._logger.warning(
                "User creation validation failed",
                context={"email": email, "validation_error": str(e)}
            )
            raise ValueError(f"Validation failed: {e}") from e
```

#### Use Async Patterns Effectively

```python
class EfficientUserService(ProtocolUserService):
    """User service with efficient async patterns."""
    
    async def get_users_batch(self, user_ids: list[UUID]) -> dict[UUID, Optional[User]]:
        """Get multiple users efficiently."""
        # Good - concurrent fetching
        tasks = [self.get_user(user_id) for user_id in user_ids]
        users = await asyncio.gather(*tasks, return_exceptions=True)
        
        result = {}
        for user_id, user in zip(user_ids, users):
            if isinstance(user, Exception):
                result[user_id] = None
            else:
                result[user_id] = user
        
        return result
    
    async def create_users_batch(self, user_data_list: list[dict]) -> list[User]:
        """Create multiple users with proper error handling."""
        created_users = []
        
        # Process in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(user_data_list), batch_size):
            batch = user_data_list[i:i + batch_size]
            
            # Create batch concurrently
            tasks = [
                self.create_user(data["email"], data["name"], data.get("metadata"))
                for data in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    # Log error but continue processing
                    await self._logger.error(
                        "Failed to create user in batch",
                        context={"error": str(result)}
                    )
                else:
                    created_users.append(result)
        
        return created_users
```

## Performance Considerations

### Protocol Method Design

```python
# Good - efficient protocol design
class ProtocolUserService(Protocol):
    async def get_users_paginated(
        self,
        limit: int = 100,
        offset: int = 0,
        filter_criteria: Optional[UserFilter] = None
    ) -> tuple[list[User], int]:  # Returns (users, total_count)
        """Get users with pagination info in single call."""
        ...
    
    async def get_user_exists(self, email: str) -> bool:
        """Efficient existence check without full user data."""
        ...

# Avoid - inefficient protocol requiring multiple calls
class IneffientUserService(Protocol):
    async def get_all_users(self) -> list[User]:  # Could be huge
        ...
    
    async def get_user_count(self) -> int:  # Separate call needed
        ...
```

### Caching Integration

```python
class CachedProtocolWrapper:
    """Generic caching wrapper for protocols."""
    
    def __init__(
        self, 
        wrapped_service: ProtocolUserService,
        cache: ProtocolCacheService,
        default_ttl: int = 3600
    ):
        self._service = wrapped_service
        self._cache = cache
        self._default_ttl = default_ttl
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user with caching."""
        cache_key = f"user:{user_id}"
        
        # Try cache first
        cached_user = await self._cache.get(cache_key)
        if cached_user:
            return cached_user
        
        # Get from service
        user = await self._service.get_user(user_id)
        
        # Cache result
        if user:
            await self._cache.set(cache_key, user, ttl_seconds=self._default_ttl)
        
        return user
    
    async def create_user(self, email: str, name: str, metadata=None) -> User:
        """Create user and cache result."""
        user = await self._service.create_user(email, name, metadata)
        
        # Cache the new user
        cache_key = f"user:{user.id}"
        await self._cache.set(cache_key, user, ttl_seconds=self._default_ttl)
        
        return user
```

## Troubleshooting

### Common Issues

#### Protocol Not Recognized at Runtime

```python
# Problem: isinstance check fails
service = MyUserService()
assert isinstance(service, ProtocolUserService)  # AssertionError

# Solution: Ensure @runtime_checkable decorator
@runtime_checkable  # This decorator is required!
class ProtocolUserService(Protocol):
    async def get_user(self, user_id: UUID) -> Optional[User]:
        ...
```

#### Type Checking Failures

```python
# Problem: mypy errors about protocol implementation
class UserService(ProtocolUserService):  # mypy error
    async def get_user(self, user_id: str) -> User:  # Wrong type
        ...

# Solution: Match protocol signature exactly
class UserService(ProtocolUserService):
    async def get_user(self, user_id: UUID) -> Optional[User]:  # Correct
        ...
```

#### Import Errors

```python
# Problem: Circular imports with TYPE_CHECKING
from omnibase_spi.protocols.types.user_types import User  # Circular import

# Solution: Use TYPE_CHECKING for forward references
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types.user_types import User

async def get_user(self, user_id: UUID) -> Optional["User"]:  # Forward ref
    ...
```

### Debugging Tips

#### Protocol Compliance Debugging

```python
def debug_protocol_compliance(obj: object, protocol: type) -> None:
    """Debug protocol compliance issues."""
    print(f"Checking {obj.__class__.__name__} against {protocol.__name__}")
    
    # Check if runtime checkable
    if not hasattr(protocol, '__runtime_checkable__'):
        print("❌ Protocol is not @runtime_checkable")
        return
    
    # Check required methods
    for attr_name in dir(protocol):
        if not attr_name.startswith('_'):
            protocol_attr = getattr(protocol, attr_name)
            if callable(protocol_attr):
                if hasattr(obj, attr_name):
                    obj_attr = getattr(obj, attr_name)
                    if callable(obj_attr):
                        print(f"✅ Method {attr_name} found")
                    else:
                        print(f"❌ Attribute {attr_name} is not callable")
                else:
                    print(f"❌ Method {attr_name} missing")
    
    # Final check
    compliant = isinstance(obj, protocol)
    print(f"Overall compliance: {'✅' if compliant else '❌'}")

# Usage
service = MyUserService()
debug_protocol_compliance(service, ProtocolUserService)
```

#### Performance Debugging

```python
import time
import functools

def debug_async_performance(func):
    """Decorator to debug async method performance."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            print(f"✅ {func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ {func.__name__} failed in {duration:.3f}s: {e}")
            raise
    return wrapper

class DebugUserService(ProtocolUserService):
    @debug_async_performance
    async def create_user(self, email: str, name: str, metadata=None):
        # Implementation with timing
        return await self._actual_create_user(email, name, metadata)
```

---

*This developer guide provides comprehensive coverage of omnibase-spi usage patterns. For specific protocol documentation, see the [API Reference](../api-reference/). For integration examples, see the [Integration Guide](../integration/).*