# Integration Guide

## Overview

This guide covers how to integrate omnibase-spi into your projects, whether you're building new applications, extending existing systems, or creating framework integrations. Learn how to effectively use protocol-based architecture in real-world scenarios.

## Quick Integration Checklist

- [ ] Install omnibase-spi package
- [ ] Configure type checking (MyPy, Pylance, etc.)
- [ ] Choose dependency injection strategy  
- [ ] Implement core protocols for your domain
- [ ] Set up testing infrastructure
- [ ] Configure CI/CD validation

## Installation and Setup

### Package Installation

```bash
# Install latest version
pip install omnibase-spi

# Or with Poetry
poetry add omnibase-spi

# Development installation
git clone https://github.com/OmniNode-ai/omnibase-spi.git
cd omnibase-spi
poetry install
```

### Environment Configuration

#### MyPy Configuration

Create or update `.mypy.ini`:

```ini
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
show_error_codes = True
namespace_packages = True
explicit_package_bases = True

# Enable omnibase-spi protocols
follow_imports = normal
ignore_missing_imports = False

[mypy-omnibase.protocols.*]
ignore_missing_imports = False
```

#### VS Code Configuration

Update `.vscode/settings.json`:

```json
{
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true,
    "python.analysis.typeCheckingMode": "strict",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.autoSearchPaths": true,
    "python.analysis.extraPaths": ["src"]
}
```

#### Pre-commit Hooks

Add `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [omnibase-spi]
        args: [--strict]
        
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=88]
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0  
    hooks:
      - id: isort
        args: [--profile=black]
```

## Framework Integration Patterns

### 1. FastAPI Integration

```python
# app/dependencies.py
from typing import Annotated
from fastapi import Depends, FastAPI
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer
)

# Protocol implementations
class FastAPILogger(ProtocolSimpleLogger):
    def log(self, level: str, message: str, **kwargs) -> None:
        # FastAPI logging integration
        import logging
        logger = logging.getLogger("fastapi")
        getattr(logger, level.lower())(message, extra=kwargs)
    
    def is_enabled(self, level: str) -> bool:
        return True

class JSONSerializer(ProtocolSimpleSerializer):
    def serialize(self, data) -> str:
        import json
        return json.dumps(data, default=str)
    
    def deserialize(self, data: str):
        import json
        return json.loads(data)
    
    def get_format(self) -> str:
        return "json"

# Dependency injection setup
def get_logger() -> ProtocolSimpleLogger:
    return FastAPILogger()

def get_serializer() -> ProtocolSimpleSerializer:
    return JSONSerializer()

# app/main.py
from fastapi import FastAPI, Depends
from typing import Annotated

app = FastAPI()

@app.post("/process")
async def process_data(
    data: dict,
    logger: Annotated[ProtocolSimpleLogger, Depends(get_logger)],
    serializer: Annotated[ProtocolSimpleSerializer, Depends(get_serializer)]
):
    """Process data using protocol-based dependencies."""
    logger.log("INFO", "Processing request", request_data=data)
    
    try:
        result = {"processed": data, "status": "success"}
        serialized = serializer.serialize(result)
        logger.log("INFO", "Request processed successfully")
        return result
        
    except Exception as e:
        logger.log("ERROR", f"Processing failed: {e}")
        raise
```

### 2. Django Integration

```python
# myapp/protocols.py
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
from omnibase.protocols.types.core_types import LogLevel
import logging

class DjangoLogger(ProtocolSimpleLogger):
    """Django-integrated logger implementation."""
    
    def __init__(self, name: str = "django"):
        self.logger = logging.getLogger(name)
    
    def log(self, level: LogLevel, message: str, **kwargs) -> None:
        # Convert to Django logging
        django_level = getattr(logging, level)
        self.logger.log(django_level, message, extra=kwargs)
    
    def is_enabled(self, level: LogLevel) -> bool:
        django_level = getattr(logging, level)
        return self.logger.isEnabledFor(django_level)

# myapp/services.py
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
from .protocols import DjangoLogger

class UserService:
    """Django service using protocol dependencies."""
    
    def __init__(self, logger: ProtocolSimpleLogger = None):
        self.logger = logger or DjangoLogger("myapp.users")
    
    def create_user(self, user_data: dict) -> dict:
        self.logger.log("INFO", "Creating user", **user_data)
        
        # Django ORM operations
        from .models import User
        user = User.objects.create(**user_data)
        
        self.logger.log("INFO", "User created", user_id=user.id)
        return {"id": user.id, "email": user.email}

# myapp/views.py
from django.http import JsonResponse
from django.views import View
from .services import UserService

class CreateUserView(View):
    def post(self, request):
        service = UserService()  # Uses default Django logger
        result = service.create_user(request.POST.dict())
        return JsonResponse(result)
```

### 3. Flask Integration

```python
# app/protocols.py
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
from flask import current_app
import logging

class FlaskLogger(ProtocolSimpleLogger):
    """Flask-integrated logger."""
    
    def log(self, level: str, message: str, **kwargs) -> None:
        flask_logger = current_app.logger
        log_method = getattr(flask_logger, level.lower())
        log_method(f"{message} - {kwargs}")
    
    def is_enabled(self, level: str) -> bool:
        return current_app.logger.isEnabledFor(getattr(logging, level))

# app/services.py
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleEventHandler
)
from typing import Dict, Any, Optional

class OrderEventHandler(ProtocolSimpleEventHandler):
    """Handle order-related events in Flask app."""
    
    def __init__(self, logger: ProtocolSimpleLogger):
        self.logger = logger
        self.supported_events = {"order.created", "order.updated", "order.cancelled"}
    
    def handle_event(
        self, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if not self.can_handle(event_type):
            return None
        
        self.logger.log("INFO", f"Handling {event_type}", **event_data)
        
        if event_type == "order.created":
            return self._handle_order_created(event_data)
        elif event_type == "order.updated":
            return self._handle_order_updated(event_data)
        elif event_type == "order.cancelled":
            return self._handle_order_cancelled(event_data)
    
    def can_handle(self, event_type: str) -> bool:
        return event_type in self.supported_events
    
    def _handle_order_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Send confirmation email, update inventory, etc.
        return {"status": "processed", "notifications_sent": True}
    
    def _handle_order_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Update order status, notify customer, etc.
        return {"status": "updated", "customer_notified": True}
    
    def _handle_order_cancelled(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Refund payment, restore inventory, etc.
        return {"status": "cancelled", "refund_processed": True}

# app/__init__.py
from flask import Flask
from .protocols import FlaskLogger
from .services import OrderEventHandler

def create_app():
    app = Flask(__name__)
    
    # Register protocol implementations with app
    with app.app_context():
        logger = FlaskLogger()
        event_handler = OrderEventHandler(logger)
        
        # Store in app config for later use
        app.config['LOGGER_PROTOCOL'] = logger
        app.config['EVENT_HANDLER'] = event_handler
    
    return app

# app/routes.py
from flask import Flask, request, jsonify, current_app

@app.route('/orders', methods=['POST'])
def create_order():
    event_handler = current_app.config['EVENT_HANDLER']
    
    order_data = request.get_json()
    
    # Process order creation...
    result = event_handler.handle_event("order.created", order_data)
    
    return jsonify(result)
```

## Dependency Injection Strategies

### 1. Constructor Injection

```python
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer
)
from typing import Optional

class DataProcessor:
    """Service using constructor injection."""
    
    def __init__(
        self,
        logger: ProtocolSimpleLogger,
        serializer: ProtocolSimpleSerializer,
        cache_enabled: bool = True
    ):
        self._logger = logger
        self._serializer = serializer
        self._cache_enabled = cache_enabled
        self._cache = {}
    
    def process(self, data: dict) -> str:
        """Process data with logging and serialization."""
        key = str(hash(str(sorted(data.items()))))
        
        if self._cache_enabled and key in self._cache:
            self._logger.log("DEBUG", "Cache hit", cache_key=key)
            return self._cache[key]
        
        self._logger.log("INFO", "Processing data", record_count=len(data))
        
        # Process data
        processed = self._transform_data(data)
        result = self._serializer.serialize(processed)
        
        if self._cache_enabled:
            self._cache[key] = result
        
        self._logger.log("INFO", "Processing complete")
        return result
    
    def _transform_data(self, data: dict) -> dict:
        """Transform data - business logic here."""
        return {k: str(v).upper() for k, v in data.items()}

# Usage
logger = MyLogger()
serializer = JSONSerializer()
processor = DataProcessor(logger, serializer)
result = processor.process({"name": "test"})
```

### 2. Property-Based Injection

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
from typing import Optional

class ConfigurableService:
    """Service with property-based protocol injection."""
    
    def __init__(self):
        self._logger: Optional[ProtocolSimpleLogger] = None
        self._config = {}
    
    @property
    def logger(self) -> ProtocolSimpleLogger:
        if self._logger is None:
            raise ValueError("Logger protocol not configured")
        return self._logger
    
    @logger.setter
    def logger(self, logger: ProtocolSimpleLogger) -> None:
        self._logger = logger
    
    def configure(self, config: dict) -> None:
        """Configure service with logger validation."""
        if self._logger is None:
            raise ValueError("Logger must be set before configuration")
        
        self.logger.log("INFO", "Configuring service", config_keys=list(config.keys()))
        self._config = config
        self.logger.log("INFO", "Service configured")
    
    def process(self, data: str) -> str:
        """Process data with configured logger."""
        self.logger.log("DEBUG", "Processing started", data_length=len(data))
        result = data.upper()
        self.logger.log("DEBUG", "Processing completed", result_length=len(result))
        return result

# Usage
service = ConfigurableService()
service.logger = MyLogger()  # Inject protocol implementation
service.configure({"debug": True})
result = service.process("hello world")
```

### 3. Dependency Injection Container

```python
from typing import Dict, TypeVar, Callable, Any
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer,
    ProtocolSimpleEventHandler
)

T = TypeVar('T')

class DIContainer:
    """Simple dependency injection container for protocols."""
    
    def __init__(self):
        self._services: Dict[type, Callable[[], Any]] = {}
        self._instances: Dict[type, Any] = {}
        self._singletons: set[type] = set()
    
    def register(
        self, 
        protocol_type: type[T], 
        factory: Callable[[], T],
        singleton: bool = True
    ) -> None:
        """Register a protocol implementation factory."""
        self._services[protocol_type] = factory
        if singleton:
            self._singletons.add(protocol_type)
    
    def get(self, protocol_type: type[T]) -> T:
        """Get instance of protocol implementation."""
        if protocol_type in self._instances:
            return self._instances[protocol_type]
        
        if protocol_type not in self._services:
            raise ValueError(f"No implementation registered for {protocol_type}")
        
        instance = self._services[protocol_type]()
        
        if protocol_type in self._singletons:
            self._instances[protocol_type] = instance
        
        return instance
    
    def create_with_dependencies(self, cls: type[T]) -> T:
        """Create instance with automatic dependency injection."""
        import inspect
        
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation in self._services:
                kwargs[param_name] = self.get(param.annotation)
        
        return cls(**kwargs)

# Usage
def create_logger() -> ProtocolSimpleLogger:
    return MyLogger()

def create_serializer() -> ProtocolSimpleSerializer:
    return JSONSerializer()

def create_event_handler(container: DIContainer) -> ProtocolSimpleEventHandler:
    logger = container.get(ProtocolSimpleLogger)
    return MyEventHandler(logger)

# Set up container
container = DIContainer()
container.register(ProtocolSimpleLogger, create_logger)
container.register(ProtocolSimpleSerializer, create_serializer)
container.register(
    ProtocolSimpleEventHandler, 
    lambda: create_event_handler(container)
)

# Service that depends on multiple protocols
class OrderService:
    def __init__(
        self,
        logger: ProtocolSimpleLogger,
        serializer: ProtocolSimpleSerializer,
        event_handler: ProtocolSimpleEventHandler
    ):
        self.logger = logger
        self.serializer = serializer
        self.event_handler = event_handler

# Automatic dependency injection
order_service = container.create_with_dependencies(OrderService)
```

## Testing Integration

### 1. Protocol Mocking

```python
import pytest
from unittest.mock import Mock
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer
)
from myapp.services import DataProcessor

class MockLogger(ProtocolSimpleLogger):
    """Test double for logger protocol."""
    
    def __init__(self):
        self.logged_messages = []
    
    def log(self, level: str, message: str, **kwargs) -> None:
        self.logged_messages.append({
            'level': level,
            'message': message,
            'kwargs': kwargs
        })
    
    def is_enabled(self, level: str) -> bool:
        return True

class MockSerializer(ProtocolSimpleSerializer):
    """Test double for serializer protocol."""
    
    def serialize(self, data) -> str:
        return f"serialized:{data}"
    
    def deserialize(self, data: str):
        if data.startswith("serialized:"):
            return data[11:]  # Remove prefix
        return data
    
    def get_format(self) -> str:
        return "mock"

def test_data_processor_with_mocks():
    """Test DataProcessor using protocol mocks."""
    # Arrange
    mock_logger = MockLogger()
    mock_serializer = MockSerializer()
    processor = DataProcessor(mock_logger, mock_serializer)
    
    test_data = {"key": "value"}
    
    # Act
    result = processor.process(test_data)
    
    # Assert
    assert result == "serialized:{'KEY': 'VALUE'}"
    
    # Verify logger interactions
    assert len(mock_logger.logged_messages) == 2
    assert mock_logger.logged_messages[0]['level'] == 'INFO'
    assert mock_logger.logged_messages[0]['message'] == 'Processing data'
    assert mock_logger.logged_messages[1]['level'] == 'INFO'
    assert mock_logger.logged_messages[1]['message'] == 'Processing complete'

def test_data_processor_with_unittest_mock():
    """Test using unittest.mock for protocols."""
    # Create mocks
    mock_logger = Mock(spec=ProtocolSimpleLogger)
    mock_serializer = Mock(spec=ProtocolSimpleSerializer)
    
    # Configure mock behavior
    mock_serializer.serialize.return_value = "mocked_result"
    mock_logger.is_enabled.return_value = True
    
    # Test
    processor = DataProcessor(mock_logger, mock_serializer, cache_enabled=False)
    result = processor.process({"test": "data"})
    
    # Verify
    assert result == "mocked_result"
    mock_logger.log.assert_called()
    mock_serializer.serialize.assert_called_once_with({'TEST': 'DATA'})
```

### 2. Protocol Testing Helpers

```python
from typing import TypeVar, Protocol, Type
from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer
)

T = TypeVar('T', bound=Protocol)

def test_protocol_implementation(
    protocol_type: Type[T], 
    implementation: T,
    test_cases: list[dict]
) -> None:
    """Generic protocol implementation tester."""
    
    # Verify implementation satisfies protocol
    assert isinstance(implementation, protocol_type)
    
    # Test protocol methods exist and are callable
    for method_name in protocol_type.__dict__:
        if not method_name.startswith('_') and hasattr(implementation, method_name):
            method = getattr(implementation, method_name)
            assert callable(method), f"{method_name} must be callable"
    
    # Run specific test cases
    for test_case in test_cases:
        method_name = test_case['method']
        args = test_case.get('args', [])
        kwargs = test_case.get('kwargs', {})
        expected = test_case.get('expected')
        
        method = getattr(implementation, method_name)
        result = method(*args, **kwargs)
        
        if expected is not None:
            assert result == expected, f"{method_name} failed test case"

# Usage
def test_my_logger_implementation():
    """Test custom logger implementation."""
    logger = MyLogger()
    
    test_cases = [
        {
            'method': 'is_enabled',
            'args': ['INFO'],
            'expected': True
        },
        {
            'method': 'is_enabled', 
            'args': ['DEBUG'],
            'expected': False  # Assuming DEBUG is disabled
        }
    ]
    
    test_protocol_implementation(ProtocolSimpleLogger, logger, test_cases)
    
    # Test logging doesn't raise exceptions
    logger.log('INFO', 'Test message', extra_data='test')
    logger.log('ERROR', 'Error message')
```

### 3. Integration Testing

```python
import pytest
from myapp.main import create_app
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger

class TestLogger(ProtocolSimpleLogger):
    """Logger for integration tests."""
    
    def __init__(self):
        self.messages = []
    
    def log(self, level: str, message: str, **kwargs) -> None:
        self.messages.append((level, message, kwargs))
    
    def is_enabled(self, level: str) -> bool:
        return True

@pytest.fixture
def app_with_test_protocols():
    """Create app with test protocol implementations."""
    app = create_app()
    
    # Replace protocols with test versions
    test_logger = TestLogger()
    app.config['LOGGER_PROTOCOL'] = test_logger
    app.config['TEST_LOGGER'] = test_logger  # For test access
    
    return app

def test_order_creation_integration(app_with_test_protocols):
    """Integration test for order creation with protocol verification."""
    app = app_with_test_protocols
    client = app.test_client()
    
    # Make request
    response = client.post('/orders', json={
        'customer_id': 'cust_123',
        'items': [{'id': 'item_1', 'quantity': 2}],
        'total': 29.99
    })
    
    # Verify response
    assert response.status_code == 200
    
    # Verify protocol interactions through test logger
    test_logger = app.config['TEST_LOGGER']
    log_messages = [msg[1] for msg in test_logger.messages]
    
    assert any('Handling order.created' in msg for msg in log_messages)
    assert any('Processing request' in msg for msg in log_messages)
```

## Configuration Management

### 1. Protocol-Based Configuration

```python
from omnibase.protocols.types.core_types import ProtocolConfigValue, ContextValue
from typing import Dict, Optional, Any

class ConfigValue(ProtocolConfigValue):
    """Implementation of config value protocol."""
    
    def __init__(
        self,
        key: str,
        value: ContextValue,
        config_type: str,
        default_value: Optional[ContextValue] = None
    ):
        self.key = key
        self.value = value
        self.config_type = config_type
        self.default_value = default_value

class ProtocolConfigManager:
    """Configuration manager using protocol types."""
    
    def __init__(self):
        self._config: Dict[str, ProtocolConfigValue] = {}
    
    def set(
        self, 
        key: str, 
        value: ContextValue, 
        config_type: str,
        default: Optional[ContextValue] = None
    ) -> None:
        """Set configuration value."""
        self._config[key] = ConfigValue(key, value, config_type, default)
    
    def get(self, key: str) -> Optional[ContextValue]:
        """Get configuration value."""
        config_value = self._config.get(key)
        return config_value.value if config_value else None
    
    def get_string(self, key: str, default: str = "") -> str:
        """Get string configuration value."""
        value = self.get(key)
        return str(value) if value is not None else default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = self.get(key)
        if isinstance(value, int):
            return value
        elif isinstance(value, str) and value.isdigit():
            return int(value)
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(key)
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return default

# Usage
config = ProtocolConfigManager()
config.set("database_host", "localhost", "string", "127.0.0.1")
config.set("database_port", 5432, "int", 5432)
config.set("debug_mode", True, "bool", False)

# Type-safe retrieval
db_host = config.get_string("database_host")
db_port = config.get_int("database_port")
debug = config.get_bool("debug_mode")
```

## Performance Considerations

### 1. Protocol Implementation Performance

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
from typing import Dict, Any
import time

class BufferedLogger(ProtocolSimpleLogger):
    """High-performance buffered logger implementation."""
    
    def __init__(self, buffer_size: int = 100, flush_interval: float = 5.0):
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self._buffer: list[dict] = []
        self._last_flush = time.time()
    
    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """Buffer log messages for batch processing."""
        self._buffer.append({
            'timestamp': time.time(),
            'level': level,
            'message': message,
            'data': kwargs
        })
        
        # Auto-flush conditions
        if (len(self._buffer) >= self.buffer_size or 
            time.time() - self._last_flush >= self.flush_interval):
            self.flush()
    
    def is_enabled(self, level: str) -> bool:
        return True
    
    def flush(self) -> None:
        """Flush buffer to actual logging system."""
        if not self._buffer:
            return
        
        # Batch write to logging system
        for entry in self._buffer:
            # Actual logging implementation here
            print(f"[{entry['level']}] {entry['message']} - {entry['data']}")
        
        self._buffer.clear()
        self._last_flush = time.time()
    
    def __del__(self):
        """Ensure buffer is flushed on destruction."""
        self.flush()
```

### 2. Caching Protocol Implementations

```python
from functools import lru_cache
from omnibase.protocols.core.protocol_canonical_serializer import ProtocolCanonicalSerializer
from omnibase.protocols.types.core_types import ProtocolSerializationResult
import hashlib

class CachedSerializer(ProtocolCanonicalSerializer):
    """Cached serializer implementation for performance."""
    
    def __init__(self, cache_size: int = 128):
        self._cache_size = cache_size
        # Use lru_cache for automatic cache management
        self._serialize_cached = lru_cache(maxsize=cache_size)(self._serialize_impl)
    
    def serialize(self, obj: Any) -> ProtocolSerializationResult:
        """Serialize with caching."""
        # Create cache key from object
        cache_key = self._get_cache_key(obj)
        return self._serialize_cached(cache_key, obj)
    
    def _serialize_impl(self, cache_key: str, obj: Any) -> ProtocolSerializationResult:
        """Internal serialization implementation."""
        try:
            import json
            data = json.dumps(obj, sort_keys=True, ensure_ascii=False)
            return SerializationResult(True, data, None)
        except Exception as e:
            return SerializationResult(False, "", str(e))
    
    def _get_cache_key(self, obj: Any) -> str:
        """Generate cache key for object."""
        try:
            # Simple hash-based cache key
            obj_str = str(obj)
            return hashlib.md5(obj_str.encode()).hexdigest()
        except:
            # Fallback for non-hashable objects
            return str(id(obj))
    
    def deserialize(self, data: str, expected_type: type[Any]) -> Any:
        """Deserialize (not cached for simplicity)."""
        import json
        return json.loads(data)
    
    def get_canonical_hash(self, obj: Any) -> str:
        """Get canonical hash."""
        result = self.serialize(obj)
        if result.success:
            return hashlib.sha256(result.data.encode()).hexdigest()
        raise ValueError("Cannot hash object")
```

## Next Steps

After integrating omnibase-spi into your project:

1. **[Framework Integration](framework-integration.md)** - Detailed framework-specific integration guides
2. **[Dependency Injection](dependency-injection.md)** - Advanced DI patterns and containers
3. **[Testing Integration](testing-integration.md)** - Comprehensive testing strategies
4. **[Best Practices](../best-practices/)** - Protocol design and implementation best practices
5. **[API Reference](../api-reference/)** - Complete protocol documentation

## Common Integration Issues

### Import Errors
- **Problem**: `ModuleNotFoundError: No module named 'omnibase.protocols'`
- **Solution**: Ensure omnibase-spi is installed in your environment

### Type Checking Issues  
- **Problem**: MyPy reports protocol violations
- **Solution**: Enable strict type checking and fix implementation issues

### Performance Issues
- **Problem**: Protocol overhead impacting performance
- **Solution**: Use caching, buffering, or optimized implementations

### Testing Complexity
- **Problem**: Difficult to test protocol-based code
- **Solution**: Use protocol mocks and test doubles