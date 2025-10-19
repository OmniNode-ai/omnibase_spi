# Integration Guide

## Overview

Comprehensive guide for integrating omnibase-spi protocols into existing applications, frameworks, and systems. This guide covers dependency injection patterns, framework-specific integration, testing strategies, and production deployment considerations.

## Table of Contents

- [Dependency Injection](#dependency-injection)
- [Framework Integration](#framework-integration)
- [Testing Integration](#testing-integration)
- [Production Deployment](#production-deployment)
- [Migration Strategies](#migration-strategies)
- [Performance Optimization](#performance-optimization)

## Dependency Injection

### Simple Container Pattern

```python
from typing import Type, TypeVar, Dict, Any, Optional
from omnibase_spi.protocols.core import ProtocolLogger, ProtocolCacheService
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus

T = TypeVar('T')

class ServiceContainer:
    """Simple dependency injection container for protocol-based services."""

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}

    def register_singleton(self, protocol: Type[T], instance: T) -> None:
        """Register singleton instance for protocol."""
        if not isinstance(instance, protocol):
            raise ValueError(f"Instance must implement {protocol.__name__}")
        self._singletons[protocol] = instance

    def register_transient(self, protocol: Type[T], impl_class: Type[T]) -> None:
        """Register transient implementation class for protocol."""
        self._services[protocol] = impl_class

    def register_factory(self, protocol: Type[T], factory_func) -> None:
        """Register factory function for protocol."""
        self._factories[protocol] = factory_func

    def get(self, protocol: Type[T]) -> T:
        """Resolve instance for protocol."""
        # Check singletons first
        if protocol in self._singletons:
            return self._singletons[protocol]

        # Check factories
        if protocol in self._factories:
            instance = self._factories[protocol]()
            if not isinstance(instance, protocol):
                raise ValueError(f"Factory must return {protocol.__name__}")
            return instance

        # Check transient services
        if protocol in self._services:
            impl_class = self._services[protocol]
            return impl_class()

        raise ValueError(f"No implementation registered for {protocol.__name__}")

    def resolve_dependencies(self, obj: Any) -> None:
        """Resolve dependencies for object using constructor annotations."""
        if hasattr(obj.__class__, '__init__'):
            annotations = getattr(obj.__class__.__init__, '__annotations__', {})
            for param_name, param_type in annotations.items():
                if param_name != 'return' and hasattr(param_type, '__runtime_checkable__'):
                    dependency = self.get(param_type)
                    setattr(obj, param_name, dependency)

# Usage example
def setup_container() -> ServiceContainer:
    """Setup service container with implementations."""
    container = ServiceContainer()

    # Register singleton services (shared instances)
    container.register_singleton(
        ProtocolLogger,
        StructuredLogger(level="INFO")
    )

    # Register transient services (new instance each time)
    container.register_transient(
        ProtocolUserService,
        DatabaseUserService
    )

    # Register factory functions (custom creation logic)
    container.register_factory(
        ProtocolCacheService,
        lambda: RedisCache(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379"))
        )
    )

    return container
```

### Advanced Container with Scopes

```python
from enum import Enum
from contextlib import contextmanager
from threading import local

class ServiceScope(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"  # Per-request or per-operation

class ScopedServiceContainer:
    """Advanced container with scoping support."""

    def __init__(self):
        self._registrations: Dict[Type, Dict] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances = local()

    def register(
        self,
        protocol: Type[T],
        implementation: Any,
        scope: ServiceScope = ServiceScope.TRANSIENT
    ) -> None:
        """Register service with scope."""
        self._registrations[protocol] = {
            'implementation': implementation,
            'scope': scope
        }

    def get(self, protocol: Type[T]) -> T:
        """Get service instance based on scope."""
        if protocol not in self._registrations:
            raise ValueError(f"No registration for {protocol.__name__}")

        registration = self._registrations[protocol]
        scope = registration['scope']
        implementation = registration['implementation']

        if scope == ServiceScope.SINGLETON:
            if protocol not in self._singletons:
                self._singletons[protocol] = self._create_instance(implementation)
            return self._singletons[protocol]

        elif scope == ServiceScope.SCOPED:
            if not hasattr(self._scoped_instances, 'instances'):
                self._scoped_instances.instances = {}

            if protocol not in self._scoped_instances.instances:
                self._scoped_instances.instances[protocol] = self._create_instance(implementation)
            return self._scoped_instances.instances[protocol]

        else:  # TRANSIENT
            return self._create_instance(implementation)

    def _create_instance(self, implementation):
        """Create instance, handling both classes and factories."""
        if callable(implementation) and not isinstance(implementation, type):
            return implementation()  # Factory function
        elif isinstance(implementation, type):
            return implementation()  # Class constructor
        else:
            return implementation   # Instance

    @contextmanager
    def scope(self):
        """Context manager for scoped services."""
        # Clear scoped instances at start of scope
        self._scoped_instances.instances = {}
        try:
            yield self
        finally:
            # Clean up scoped instances
            if hasattr(self._scoped_instances, 'instances'):
                del self._scoped_instances.instances
```

## Framework Integration

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import AsyncGenerator
import asyncio

# FastAPI dependency injection with omnibase protocols
app = FastAPI(title="ONEX API Server")

# Global service container
container = ScopedServiceContainer()

# Setup services
def setup_services():
    """Configure services for FastAPI application."""
    container.register(
        ProtocolLogger,
        StructuredLogger(level="INFO"),
        ServiceScope.SINGLETON
    )

    container.register(
        ProtocolUserService,
        lambda: DatabaseUserService(
            connection_string=os.getenv("DATABASE_URL")
        ),
        ServiceScope.SCOPED
    )

    container.register(
        ProtocolWorkflowEventBus,
        lambda: KafkaWorkflowEventBus(
            bootstrap_servers=os.getenv("KAFKA_SERVERS", "localhost:9092")
        ),
        ServiceScope.SINGLETON
    )

# Middleware to manage scoped services
class ServiceScopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        with container.scope():
            response = await call_next(request)
        return response

app.add_middleware(ServiceScopeMiddleware)

# Dependency functions
async def get_user_service() -> ProtocolUserService:
    """FastAPI dependency for user service."""
    return container.get(ProtocolUserService)

async def get_logger() -> ProtocolLogger:
    """FastAPI dependency for logger."""
    return container.get(ProtocolLogger)

async def get_workflow_event_bus() -> ProtocolWorkflowEventBus:
    """FastAPI dependency for workflow event bus."""
    return container.get(ProtocolWorkflowEventBus)

# API endpoints using protocol dependencies
@app.post("/users", response_model=dict)
async def create_user(
    user_data: dict,
    user_service: ProtocolUserService = Depends(get_user_service),
    logger: ProtocolLogger = Depends(get_logger)
):
    """Create user endpoint with protocol dependencies."""
    try:
        await logger.info(
            "Creating user",
            context={"email": user_data.get("email")}
        )

        user = await user_service.create_user(
            email=user_data["email"],
            name=user_data["name"]
        )

        await logger.info(
            "User created successfully",
            context={"user_id": str(user.id), "email": user.email}
        )

        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name
        }

    except ValueError as e:
        await logger.error(
            "User creation failed",
            context={"error": str(e), "email": user_data.get("email")}
        )
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    user_service: ProtocolUserService = Depends(get_user_service)
):
    """Get user endpoint."""
    try:
        user = await user_service.get_user(UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name,
            "status": user.status
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@app.post("/workflows/{workflow_type}/start")
async def start_workflow(
    workflow_type: str,
    workflow_data: dict,
    event_bus: ProtocolWorkflowEventBus = Depends(get_workflow_event_bus),
    logger: ProtocolLogger = Depends(get_logger)
):
    """Start workflow endpoint."""
    instance_id = uuid4()

    # Create workflow started event
    event = ProtocolWorkflowEvent(
        event_id=uuid4(),
        event_type="workflow.started",
        workflow_type=workflow_type,
        instance_id=instance_id,
        sequence_number=1,
        timestamp=datetime.now(),
        data=workflow_data,
        metadata={"source": "api"},
        idempotency_key=f"{workflow_type}-{instance_id}-started",
        source_node_id="api-server"
    )

    await event_bus.publish_workflow_event(event)

    await logger.info(
        "Workflow started",
        context={
            "workflow_type": workflow_type,
            "instance_id": str(instance_id)
        }
    )

    return {
        "workflow_type": workflow_type,
        "instance_id": str(instance_id),
        "status": "started"
    }

# Application startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    setup_services()

    logger = container.get(ProtocolLogger)
    await logger.info("FastAPI application started", context={"version": "1.0.0"})

# Application shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger = container.get(ProtocolLogger)
    await logger.info("FastAPI application shutting down", context={})
```

### Django Integration

```python
# django_project/protocols.py
from django.conf import settings
from omnibase_spi.protocols.core import ProtocolLogger
from omnibase_spi.protocols.workflow_orchestration import ProtocolUserService

class DjangoServiceRegistry:
    """Django-specific service registry."""

    def __init__(self):
        self._services = {}
        self._setup_services()

    def _setup_services(self):
        """Setup services based on Django settings."""
        # Logger setup
        if settings.DEBUG:
            self._services[ProtocolLogger] = DevelopmentLogger()
        else:
            self._services[ProtocolLogger] = ProductionLogger(
                level=settings.LOG_LEVEL
            )

        # User service setup
        if hasattr(settings, 'USER_SERVICE_TYPE'):
            if settings.USER_SERVICE_TYPE == 'database':
                self._services[ProtocolUserService] = DjangoORMUserService()
            elif settings.USER_SERVICE_TYPE == 'api':
                self._services[ProtocolUserService] = ExternalAPIUserService(
                    api_url=settings.EXTERNAL_USER_API_URL
                )
        else:
            self._services[ProtocolUserService] = DjangoORMUserService()

    def get(self, protocol: Type[T]) -> T:
        """Get service implementation."""
        if protocol not in self._services:
            raise ValueError(f"No service registered for {protocol.__name__}")
        return self._services[protocol]

# Global registry instance
service_registry = DjangoServiceRegistry()

# django_project/views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import asyncio
from .protocols import service_registry

@csrf_exempt
@require_http_methods(["POST"])
def create_user_view(request):
    """Django view for user creation using protocols."""
    try:
        data = json.loads(request.body)

        # Get services from registry
        user_service = service_registry.get(ProtocolUserService)
        logger = service_registry.get(ProtocolLogger)

        # Run async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Log request
            loop.run_until_complete(
                logger.info("User creation requested", context={
                    "email": data.get("email"),
                    "method": request.method,
                    "user_agent": request.META.get("HTTP_USER_AGENT", "")
                })
            )

            # Create user
            user = loop.run_until_complete(
                user_service.create_user(
                    email=data["email"],
                    name=data["name"]
                )
            )

            # Log success
            loop.run_until_complete(
                logger.info("User created successfully", context={
                    "user_id": str(user.id),
                    "email": user.email
                })
            )

            return JsonResponse({
                "success": True,
                "user": {
                    "user_id": str(user.id),
                    "email": user.email,
                    "name": user.name
                }
            })

        finally:
            loop.close()

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except KeyError as e:
        return JsonResponse({"error": f"Missing field: {e}"}, status=400)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Internal server error"}, status=500)

# django_project/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .protocols import service_registry
import asyncio
import uuid

class ProtocolLoggingMiddleware(MiddlewareMixin):
    """Django middleware for protocol-based logging."""

    def process_request(self, request):
        """Log incoming requests."""
        request.correlation_id = str(uuid.uuid4())

        logger = service_registry.get(ProtocolLogger)

        # Run async logging in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                logger.info("Request received", context={
                    "correlation_id": request.correlation_id,
                    "method": request.method,
                    "path": request.path,
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "remote_addr": request.META.get("REMOTE_ADDR", "")
                })
            )
        finally:
            loop.close()

    def process_response(self, request, response):
        """Log responses."""
        if hasattr(request, 'correlation_id'):
            logger = service_registry.get(ProtocolLogger)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(
                    logger.info("Request completed", context={
                        "correlation_id": request.correlation_id,
                        "status_code": response.status_code,
                        "content_type": response.get("Content-Type", "")
                    })
                )
            finally:
                loop.close()

        return response
```

### Flask Integration

```python
from flask import Flask, request, jsonify, g
from functools import wraps
import asyncio
from threading import local

app = Flask(__name__)

# Thread-local storage for async event loop
thread_local = local()

def get_event_loop():
    """Get or create event loop for current thread."""
    if not hasattr(thread_local, 'loop'):
        thread_local.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_local.loop)
    return thread_local.loop

# Service container
container = ServiceContainer()

def setup_flask_services():
    """Setup services for Flask application."""
    container.register_singleton(
        ProtocolLogger,
        FlaskLogger(app.logger)
    )

    container.register_transient(
        ProtocolUserService,
        DatabaseUserService
    )

# Dependency injection decorator
def inject(*protocols):
    """Decorator to inject protocol dependencies."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Resolve dependencies
            dependencies = {}
            for protocol in protocols:
                dependencies[protocol.__name__] = container.get(protocol)

            # Add dependencies to kwargs
            kwargs.update(dependencies)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Routes with dependency injection
@app.route('/users', methods=['POST'])
@inject(ProtocolUserService, ProtocolLogger)
def create_user(ProtocolUserService=None, ProtocolLogger=None):
    """Create user with injected dependencies."""
    loop = get_event_loop()

    try:
        data = request.get_json()

        # Log request
        loop.run_until_complete(
            ProtocolLogger.info("User creation requested", context={
                "email": data.get("email"),
                "remote_addr": request.remote_addr
            })
        )

        # Create user
        user = loop.run_until_complete(
            ProtocolUserService.create_user(
                email=data["email"],
                name=data["name"]
            )
        )

        # Log success
        loop.run_until_complete(
            ProtocolLogger.info("User created", context={
                "user_id": str(user.id)
            })
        )

        return jsonify({
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name
        })

    except Exception as e:
        loop.run_until_complete(
            ProtocolLogger.error("User creation failed", context={
                "error": str(e)
            })
        )
        return jsonify({"error": str(e)}), 400

@app.before_first_request
def initialize_app():
    """Initialize Flask application."""
    setup_flask_services()

# Context manager for request-scoped services
@app.before_request
def before_request():
    """Setup request context."""
    g.correlation_id = str(uuid.uuid4())
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """Cleanup after request."""
    if hasattr(g, 'correlation_id'):
        duration = time.time() - g.start_time

        logger = container.get(ProtocolLogger)
        loop = get_event_loop()

        loop.run_until_complete(
            logger.info("Request completed", context={
                "correlation_id": g.correlation_id,
                "duration_ms": round(duration * 1000, 2),
                "status_code": response.status_code
            })
        )

    return response
```

## Testing Integration

### Protocol Mock Framework

```python
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, Optional
import pytest

class ProtocolMockFactory:
    """Factory for creating protocol mocks."""

    @staticmethod
    def create_mock_user_service() -> ProtocolUserService:
        """Create mock user service with common behaviors."""
        mock = AsyncMock(spec=ProtocolUserService)

        # Store users for stateful testing
        mock._users: Dict[UUID, Any] = {}

        async def mock_create_user(email: str, name: str) -> Any:
            # Simulate validation
            if not email or "@" not in email:
                raise ValueError("Invalid email")
            if not name:
                raise ValueError("Name required")

            # Check for duplicates
            for user in mock._users.values():
                if user.email == email:
                    raise ValueError(f"User {email} already exists")

            # Create mock user
            user = MagicMock()
            user.id = uuid.uuid4()
            user.email = email
            user.name = name
            user.status = "active"
            user.created_at = datetime.now()

            mock._users[user.id] = user
            return user

        async def mock_get_user(user_id: UUID) -> Optional[Any]:
            return mock._users.get(user_id)

        async def mock_list_users() -> list:
            return list(mock._users.values())

        # Bind mock methods
        mock.create_user.side_effect = mock_create_user
        mock.get_user.side_effect = mock_get_user
        mock.list_users.side_effect = mock_list_users

        return mock

    @staticmethod
    def create_mock_logger() -> ProtocolLogger:
        """Create mock logger that captures log entries."""
        mock = AsyncMock(spec=ProtocolLogger)
        mock.log_entries = []

        async def capture_log(level: str, message: str, context: dict):
            mock.log_entries.append({
                "level": level,
                "message": message,
                "context": context,
                "timestamp": datetime.now()
            })

        mock.info.side_effect = lambda msg, ctx: capture_log("INFO", msg, ctx)
        mock.error.side_effect = lambda msg, ctx: capture_log("ERROR", msg, ctx)
        mock.warning.side_effect = lambda msg, ctx: capture_log("WARNING", msg, ctx)
        mock.debug.side_effect = lambda msg, ctx: capture_log("DEBUG", msg, ctx)

        return mock

# Test fixtures
@pytest.fixture
def mock_user_service():
    """Provide mock user service."""
    return ProtocolMockFactory.create_mock_user_service()

@pytest.fixture
def mock_logger():
    """Provide mock logger."""
    return ProtocolMockFactory.create_mock_logger()

@pytest.fixture
def test_container(mock_user_service, mock_logger):
    """Provide test service container."""
    container = ServiceContainer()
    container.register_singleton(ProtocolUserService, mock_user_service)
    container.register_singleton(ProtocolLogger, mock_logger)
    return container

# Integration tests
@pytest.mark.asyncio
async def test_user_creation_workflow(test_container):
    """Test complete user creation workflow."""
    user_service = test_container.get(ProtocolUserService)
    logger = test_container.get(ProtocolLogger)

    # Test user creation
    user = await user_service.create_user("test@example.com", "Test User")

    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.status == "active"

    # Test duplicate creation fails
    with pytest.raises(ValueError, match="already exists"):
        await user_service.create_user("test@example.com", "Duplicate User")

@pytest.mark.asyncio
async def test_logging_integration(test_container):
    """Test logging integration."""
    logger = test_container.get(ProtocolLogger)

    await logger.info("Test message", context={"key": "value"})
    await logger.error("Error message", context={"error_code": "E001"})

    # Verify logs were captured
    assert len(logger.log_entries) == 2

    info_log = logger.log_entries[0]
    assert info_log["level"] == "INFO"
    assert info_log["message"] == "Test message"
    assert info_log["context"]["key"] == "value"

    error_log = logger.log_entries[1]
    assert error_log["level"] == "ERROR"
    assert error_log["message"] == "Error message"

# FastAPI test integration
from fastapi.testclient import TestClient

def test_fastapi_integration():
    """Test FastAPI endpoint with mocked protocols."""
    # Override dependencies with mocks
    mock_user_service = ProtocolMockFactory.create_mock_user_service()
    mock_logger = ProtocolMockFactory.create_mock_logger()

    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_logger] = lambda: mock_logger

    client = TestClient(app)

    # Test user creation
    response = client.post("/users", json={
        "email": "test@example.com",
        "name": "Test User"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"

    # Verify logger was called
    assert len(mock_logger.log_entries) >= 2  # Request start and success

    # Clean up overrides
    app.dependency_overrides.clear()
```

### Test Database Integration

```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Setup test database."""
    # Use in-memory SQLite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()

@pytest.fixture
async def db_session(test_db):
    """Provide database session for tests."""
    async_session = sessionmaker(
        test_db, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback after each test

@pytest.fixture
def db_user_service(db_session):
    """Provide database user service for testing."""
    return DatabaseUserService(db_session)

# Database integration tests
@pytest.mark.asyncio
async def test_database_user_service_integration(db_user_service):
    """Test user service with real database."""
    # Create user
    user = await db_user_service.create_user("db@example.com", "DB User")

    assert user.id is not None
    assert user.email == "db@example.com"
    assert user.name == "DB User"

    # Retrieve user
    retrieved = await db_user_service.get_user(user.id)
    assert retrieved is not None
    assert retrieved.email == user.email

    # Test duplicate email
    with pytest.raises(ValueError):
        await db_user_service.create_user("db@example.com", "Duplicate")
```

## Production Deployment

### Configuration Management

```python
from typing import Optional
import os
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    """Configuration for protocol services."""

    # Database
    database_url: str
    database_pool_size: int = 10

    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Kafka Event Bus
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_security_protocol: str = "PLAINTEXT"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # MCP Integration
    mcp_registry_url: Optional[str] = None
    mcp_api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> 'ServiceConfig':
        """Load configuration from environment variables."""
        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///app.db"),
            database_pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            kafka_bootstrap_servers=os.getenv("KAFKA_SERVERS", "localhost:9092"),
            kafka_security_protocol=os.getenv("KAFKA_SECURITY", "PLAINTEXT"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            mcp_registry_url=os.getenv("MCP_REGISTRY_URL"),
            mcp_api_key=os.getenv("MCP_API_KEY")
        )

class ProductionServiceFactory:
    """Factory for production service implementations."""

    def __init__(self, config: ServiceConfig):
        self.config = config

    def create_logger(self) -> ProtocolLogger:
        """Create production logger."""
        if self.config.log_format == "json":
            return StructuredJSONLogger(
                level=self.config.log_level,
                include_correlation_ids=True
            )
        else:
            return ConsoleLogger(level=self.config.log_level)

    def create_cache_service(self) -> ProtocolCacheService:
        """Create Redis cache service."""
        return RedisCache(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            max_connections=20
        )

    def create_user_service(self) -> ProtocolUserService:
        """Create database user service."""
        return DatabaseUserService(
            connection_string=self.config.database_url,
            pool_size=self.config.database_pool_size
        )

    def create_event_bus(self) -> ProtocolWorkflowEventBus:
        """Create Kafka event bus."""
        return KafkaWorkflowEventBus(
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            security_protocol=self.config.kafka_security_protocol
        )

    def create_mcp_registry(self) -> Optional[ProtocolMCPRegistry]:
        """Create MCP registry if configured."""
        if self.config.mcp_registry_url:
            return HTTPMCPRegistry(
                registry_url=self.config.mcp_registry_url,
                api_key=self.config.mcp_api_key
            )
        return None

def setup_production_container(config: ServiceConfig) -> ServiceContainer:
    """Setup service container for production."""
    container = ScopedServiceContainer()
    factory = ProductionServiceFactory(config)

    # Register production services
    container.register(
        ProtocolLogger,
        factory.create_logger(),
        ServiceScope.SINGLETON
    )

    container.register(
        ProtocolCacheService,
        factory.create_cache_service(),
        ServiceScope.SINGLETON
    )

    container.register(
        ProtocolUserService,
        factory.create_user_service,  # Factory function
        ServiceScope.SCOPED
    )

    container.register(
        ProtocolWorkflowEventBus,
        factory.create_event_bus(),
        ServiceScope.SINGLETON
    )

    mcp_registry = factory.create_mcp_registry()
    if mcp_registry:
        container.register(
            ProtocolMCPRegistry,
            mcp_registry,
            ServiceScope.SINGLETON
        )

    return container
```

### Health Checks

```python
from typing import Dict, Any
import asyncio
import time

class HealthChecker:
    """Health check manager for protocol services."""

    def __init__(self, container: ServiceContainer):
        self.container = container
        self.health_checks = {}
        self.last_check_results = {}

    def register_health_check(
        self,
        name: str,
        check_func,
        timeout_seconds: float = 5.0
    ):
        """Register a health check function."""
        self.health_checks[name] = {
            'func': check_func,
            'timeout': timeout_seconds
        }

    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'checks': {}
        }

        for name, check_config in self.health_checks.items():
            try:
                check_result = await asyncio.wait_for(
                    check_config['func'](),
                    timeout=check_config['timeout']
                )

                results['checks'][name] = {
                    'status': 'healthy',
                    'response_time_ms': check_result.get('response_time_ms', 0),
                    'details': check_result.get('details', {})
                }

            except asyncio.TimeoutError:
                results['checks'][name] = {
                    'status': 'unhealthy',
                    'error': 'Health check timeout',
                    'timeout_seconds': check_config['timeout']
                }
                results['overall_status'] = 'unhealthy'

            except Exception as e:
                results['checks'][name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                results['overall_status'] = 'unhealthy'

        self.last_check_results = results
        return results

    async def check_database(self) -> Dict[str, Any]:
        """Health check for database connectivity."""
        start_time = time.time()

        try:
            user_service = self.container.get(ProtocolUserService)
            # Attempt a simple database operation
            await user_service.get_user(uuid.uuid4())  # Expected to return None

            response_time = (time.time() - start_time) * 1000
            return {
                'response_time_ms': round(response_time, 2),
                'details': {'connection': 'ok'}
            }

        except Exception as e:
            return {
                'response_time_ms': (time.time() - start_time) * 1000,
                'details': {'error': str(e)}
            }

    async def check_cache(self) -> Dict[str, Any]:
        """Health check for cache service."""
        start_time = time.time()

        try:
            cache = self.container.get(ProtocolCacheService)

            # Test cache operations
            test_key = f"health_check_{int(time.time())}"
            test_value = "health_check_value"

            await cache.set(test_key, test_value, ttl_seconds=10)
            retrieved_value = await cache.get(test_key)

            if retrieved_value != test_value:
                raise Exception("Cache set/get mismatch")

            response_time = (time.time() - start_time) * 1000
            return {
                'response_time_ms': round(response_time, 2),
                'details': {'cache_operations': 'ok'}
            }

        except Exception as e:
            return {
                'response_time_ms': (time.time() - start_time) * 1000,
                'details': {'error': str(e)}
            }

    async def check_event_bus(self) -> Dict[str, Any]:
        """Health check for event bus connectivity."""
        start_time = time.time()

        try:
            event_bus = self.container.get(ProtocolWorkflowEventBus)

            # Create test event
            test_event = ProtocolWorkflowEvent(
                event_id=uuid.uuid4(),
                event_type="health.check",
                workflow_type="health_check",
                instance_id=uuid.uuid4(),
                sequence_number=1,
                timestamp=datetime.now(),
                data={"test": True},
                metadata={"source": "health_check"},
                idempotency_key=f"health_check_{int(time.time())}",
                source_node_id="health_checker"
            )

            await event_bus.publish_workflow_event(test_event)

            response_time = (time.time() - start_time) * 1000
            return {
                'response_time_ms': round(response_time, 2),
                'details': {'event_publishing': 'ok'}
            }

        except Exception as e:
            return {
                'response_time_ms': (time.time() - start_time) * 1000,
                'details': {'error': str(e)}
            }

# Setup health checks
def setup_health_checks(container: ServiceContainer) -> HealthChecker:
    """Setup health checker with standard checks."""
    health_checker = HealthChecker(container)

    # Register standard health checks
    health_checker.register_health_check(
        'database',
        health_checker.check_database,
        timeout_seconds=5.0
    )

    health_checker.register_health_check(
        'cache',
        health_checker.check_cache,
        timeout_seconds=3.0
    )

    health_checker.register_health_check(
        'event_bus',
        health_checker.check_event_bus,
        timeout_seconds=10.0
    )

    return health_checker

# Health check endpoint for FastAPI
@app.get("/health")
async def health_check_endpoint(
    health_checker: HealthChecker = Depends(lambda: app.state.health_checker)
):
    """Health check endpoint."""
    results = await health_checker.check_all()

    status_code = 200 if results['overall_status'] == 'healthy' else 503
    return JSONResponse(content=results, status_code=status_code)
```

## Performance Optimization

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool
from redis.connection import ConnectionPool
import asyncio

class OptimizedServiceFactory:
    """Service factory with performance optimizations."""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self._db_engine = None
        self._redis_pool = None

    async def get_db_engine(self):
        """Get database engine with connection pooling."""
        if not self._db_engine:
            self._db_engine = create_async_engine(
                self.config.database_url,
                poolclass=QueuePool,
                pool_size=self.config.database_pool_size,
                max_overflow=20,
                pool_pre_ping=True,  # Validate connections
                pool_recycle=3600,   # Recycle connections every hour
                echo=self.config.log_level == "DEBUG"
            )
        return self._db_engine

    async def get_redis_pool(self):
        """Get Redis connection pool."""
        if not self._redis_pool:
            self._redis_pool = ConnectionPool(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                max_connections=50,
                retry_on_timeout=True,
                health_check_interval=30
            )
        return self._redis_pool

    async def create_optimized_user_service(self) -> ProtocolUserService:
        """Create optimized user service."""
        engine = await self.get_db_engine()
        return OptimizedDatabaseUserService(
            engine=engine,
            query_cache_ttl=300,  # Cache queries for 5 minutes
            enable_batch_operations=True
        )
```

### Caching Strategies

```python
from functools import wraps
import hashlib
import pickle

def cache_result(ttl_seconds: int = 3600, cache_key_prefix: str = ""):
    """Decorator to cache method results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Generate cache key from method and arguments
            cache_key_data = f"{cache_key_prefix}:{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()

            # Try to get from cache
            if hasattr(self, '_cache_service'):
                cached_result = await self._cache_service.get(cache_key)
                if cached_result is not None:
                    return cached_result

            # Execute method
            result = await func(self, *args, **kwargs)

            # Cache result
            if hasattr(self, '_cache_service') and result is not None:
                await self._cache_service.set(cache_key, result, ttl_seconds)

            return result
        return wrapper
    return decorator

class CachedUserService:
    """User service with caching optimization."""

    def __init__(
        self,
        user_service: ProtocolUserService,
        cache_service: ProtocolCacheService
    ):
        self._user_service = user_service
        self._cache_service = cache_service

    @cache_result(ttl_seconds=600, cache_key_prefix="user")
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user with caching."""
        return await self._user_service.get_user(user_id)

    async def create_user(self, email: str, name: str) -> User:
        """Create user and invalidate relevant caches."""
        user = await self._user_service.create_user(email, name)

        # Invalidate list caches
        await self._invalidate_list_caches()

        return user

    async def _invalidate_list_caches(self):
        """Invalidate caches that might be affected by user creation."""
        # Implementation depends on cache service capabilities
        pass
```

## Summary

This integration guide provides comprehensive patterns for:

1. **Dependency Injection**: Simple and advanced containers with scoping
2. **Framework Integration**: FastAPI, Django, and Flask integration patterns
3. **Testing**: Mock frameworks, database testing, and integration test strategies
4. **Production**: Configuration management, health checks, and monitoring
5. **Performance**: Connection pooling, caching, and optimization strategies

**Key Integration Principles:**

- **Protocol-First**: Always depend on protocols, not implementations
- **Scoped Services**: Use appropriate service scopes for different contexts
- **Health Monitoring**: Implement comprehensive health checks
- **Performance**: Optimize with caching and connection pooling
- **Testing**: Create comprehensive test strategies with mocks and real services

These patterns enable robust, scalable integration of omnibase-spi protocols into production systems while maintaining the benefits of type safety, dependency inversion, and testability.

---

*For specific protocol documentation, see the [API Reference](../api-reference/). For implementation examples, see the [Developer Guide](../developer-guide/).*
