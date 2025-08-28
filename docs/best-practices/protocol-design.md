# Protocol Design Guidelines

## Overview

This guide covers best practices for designing effective, maintainable, and scalable protocols within the omnibase-spi ecosystem. Following these guidelines ensures protocol consistency, type safety, and long-term maintainability.

## Core Design Principles

### 1. Single Responsibility Principle

Each protocol should have **one clear purpose** and reason to change:

```python
# ✅ GOOD - Single responsibility
class ProtocolLogger(Protocol):
    """Handles only logging operations."""
    
    def log(self, level: LogLevel, message: str, **kwargs) -> None: ...
    def is_enabled(self, level: LogLevel) -> bool: ...

class ProtocolSerializer(Protocol):
    """Handles only serialization operations."""
    
    def serialize(self, obj: Any) -> str: ...
    def deserialize(self, data: str) -> Any: ...

# ❌ AVOID - Multiple responsibilities
class ProtocolLoggerSerializer(Protocol):
    """Mixing logging and serialization concerns."""
    
    def log(self, level: str, message: str) -> None: ...
    def serialize(self, obj: Any) -> str: ...  # Different concern
    def send_notification(self, msg: str) -> None: ...  # Another concern
```

### 2. Interface Segregation

Clients should not depend on protocols they don't use:

```python
# ✅ GOOD - Segregated interfaces
class ProtocolBasicLogger(Protocol):
    """Minimal logging interface."""
    def log(self, level: LogLevel, message: str) -> None: ...

class ProtocolAdvancedLogger(ProtocolBasicLogger, Protocol):
    """Extended logging with additional features."""
    def log_structured(self, level: LogLevel, data: Dict[str, Any]) -> None: ...
    def get_log_history(self) -> List[str]: ...

# ❌ AVOID - Forcing all clients to implement unused methods
class ProtocolHeavyLogger(Protocol):
    """Forces all implementations to handle complex features."""
    def log(self, level: str, message: str) -> None: ...
    def log_structured(self, level: str, data: Dict[str, Any]) -> None: ...
    def export_logs(self, format: str, destination: str) -> None: ...
    def configure_rotation(self, size: int, count: int) -> None: ...
    def set_compression(self, enabled: bool) -> None: ...
```

### 3. Liskov Substitution Principle

Protocol implementations should be substitutable without breaking functionality:

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleSerializer

# ✅ GOOD - All implementations behave consistently
class JSONSerializer(ProtocolSimpleSerializer):
    def serialize(self, data: Any) -> str:
        import json
        return json.dumps(data)
    
    def deserialize(self, data: str) -> Any:
        import json
        return json.loads(data)
    
    def get_format(self) -> str:
        return "json"

class XMLSerializer(ProtocolSimpleSerializer):
    def serialize(self, data: Any) -> str:
        # Convert to XML format
        return self._to_xml(data)
    
    def deserialize(self, data: str) -> Any:
        # Parse XML format
        return self._from_xml(data)
    
    def get_format(self) -> str:
        return "xml"

# ❌ AVOID - Inconsistent behavior
class BrokenSerializer(ProtocolSimpleSerializer):
    def serialize(self, data: Any) -> str:
        # Violates contract - sometimes returns bytes instead of str
        if isinstance(data, dict):
            return json.dumps(data).encode()  # Returns bytes!
        return str(data)
    
    def deserialize(self, data: str) -> Any:
        # Violates contract - raises different exceptions
        raise NotImplementedError("Deserialization not supported")
    
    def get_format(self) -> str:
        return None  # Violates return type contract
```

## Protocol Naming Conventions

### 1. Protocol Class Names

Use clear, descriptive names with `Protocol` prefix:

```python
# ✅ GOOD - Clear naming
class ProtocolEventBus(Protocol): ...
class ProtocolUserRepository(Protocol): ...
class ProtocolPaymentProcessor(Protocol): ...
class ProtocolEmailSender(Protocol): ...

# ❌ AVOID - Unclear or inconsistent naming  
class Bus(Protocol): ...           # Too generic
class IEventBus(Protocol): ...     # Don't use "I" prefix
class EventBusInterface(Protocol): ...  # Redundant "Interface"
class EventBusProto(Protocol): ... # Abbreviated
```

### 2. Method Names

Use descriptive verb-based names:

```python
class ProtocolUserService(Protocol):
    # ✅ GOOD - Clear action-oriented names
    def create_user(self, user_data: Dict[str, Any]) -> str: ...
    def find_user_by_email(self, email: str) -> Optional[User]: ...
    def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> None: ...
    def deactivate_user(self, user_id: str) -> None: ...
    
    # ❌ AVOID - Unclear or inconsistent naming
    def user(self, data: Dict[str, Any]) -> str: ...  # Ambiguous
    def get(self, email: str) -> Optional[User]: ...  # Too generic
    def modify(self, user_id: str, data: Dict[str, Any]) -> None: ...  # Vague
    def remove(self, user_id: str) -> None: ...  # Inconsistent with "deactivate"
```

### 3. Parameter Names

Use clear, descriptive parameter names:

```python
class ProtocolFileProcessor(Protocol):
    # ✅ GOOD - Descriptive parameters
    def process_file(
        self,
        file_path: Path,
        output_directory: Path,
        processing_options: Dict[str, Any],
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> ProcessingResult: ...
    
    # ❌ AVOID - Unclear parameters
    def process_file(
        self, 
        fp: Path,           # Abbreviated
        dir: Path,          # Generic
        opts: Dict,         # Abbreviated and untyped
        cb = None           # Abbreviated and untyped
    ) -> Any: ...           # Untyped return
```

## Type Safety Best Practices

### 1. Use Strong Typing

Prefer specific types over generic ones:

```python
from omnibase.protocols.types.core_types import LogLevel, ContextValue
from typing import Dict, List, Optional, Union
from datetime import datetime
from uuid import UUID

class ProtocolAuditLog(Protocol):
    # ✅ GOOD - Strong typing
    def log_event(
        self,
        event_type: Literal["user.login", "user.logout", "data.access", "system.error"],
        user_id: UUID,
        timestamp: datetime,
        metadata: Dict[str, ContextValue],
        severity: Literal["low", "medium", "high", "critical"]
    ) -> None: ...
    
    def get_events_by_user(
        self, 
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[str]] = None
    ) -> List[AuditEvent]: ...

# ❌ AVOID - Weak typing
class ProtocolWeakAuditLog(Protocol):
    def log_event(
        self,
        event_type: Any,        # Too generic
        user_id: str,          # Should be UUID
        timestamp: str,        # Should be datetime
        metadata: dict,        # Untyped dict
        severity: str          # Should be Literal
    ) -> None: ...
    
    def get_events_by_user(self, user_id, start_date, end_date, event_types=None):
        # No type hints at all
        ...
```

### 2. Handle Optional Values Explicitly

Make optional parameters and return values explicit:

```python
from typing import Optional, List

class ProtocolUserLookup(Protocol):
    # ✅ GOOD - Explicit optional handling
    def find_user_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID, returns None if not found."""
        ...
    
    def find_users_by_role(
        self, 
        role: str,
        active_only: bool = True,
        limit: Optional[int] = None
    ) -> List[User]:
        """Find users by role, returns empty list if none found."""
        ...
    
    def get_user_permissions(
        self, 
        user_id: str
    ) -> Optional[List[str]]:
        """Get user permissions, None if user doesn't exist."""
        ...

# ❌ AVOID - Unclear optional handling
class ProtocolUnclearUserLookup(Protocol):
    def find_user_by_id(self, user_id: str) -> User:
        """What happens if user not found? Exception? None?"""
        ...
    
    def find_users_by_role(self, role: str, active_only=True, limit=None):
        """Unclear types and default behavior."""
        ...
```

### 3. Use Type Guards and Validation

Include type validation methods in protocols:

```python
from typing import TypeGuard
from omnibase.protocols.types.core_types import ProtocolSemVer

class ProtocolVersionValidator(Protocol):
    """Protocol for version validation and type guards."""
    
    def is_valid_version(self, obj: Any) -> TypeGuard[ProtocolSemVer]:
        """Type guard to validate semantic version objects."""
        ...
    
    def validate_version_string(self, version: str) -> bool:
        """Validate version string format (e.g., '1.2.3')."""
        ...
    
    def parse_version(self, version: str) -> Optional[ProtocolSemVer]:
        """Parse version string to semantic version object."""
        ...
    
    def compare_versions(
        self, 
        version1: ProtocolSemVer, 
        version2: ProtocolSemVer
    ) -> Literal["less", "equal", "greater"]:
        """Compare two semantic versions."""
        ...

# Implementation example
class VersionValidator(ProtocolVersionValidator):
    def is_valid_version(self, obj: Any) -> TypeGuard[ProtocolSemVer]:
        return (
            hasattr(obj, 'major') and isinstance(obj.major, int) and
            hasattr(obj, 'minor') and isinstance(obj.minor, int) and
            hasattr(obj, 'patch') and isinstance(obj.patch, int) and
            hasattr(obj, '__str__') and callable(obj.__str__)
        )
```

## Forward Reference Patterns

### 1. Basic Forward References

Use `TYPE_CHECKING` for external model references:

```python
from typing import TYPE_CHECKING, Protocol, List, Dict, Optional
from omnibase.protocols.types.core_types import ContextValue

if TYPE_CHECKING:
    from external.models import UserModel, OrderModel, PaymentModel

class ProtocolOrderService(Protocol):
    """Order service with forward references to external models."""
    
    def create_order(
        self, 
        user: "UserModel", 
        items: List[Dict[str, ContextValue]]
    ) -> "OrderModel":
        """Create new order for user."""
        ...
    
    def process_payment(
        self, 
        order: "OrderModel", 
        payment_info: Dict[str, ContextValue]
    ) -> "PaymentModel":
        """Process payment for order."""
        ...
    
    def get_order_history(self, user: "UserModel") -> List["OrderModel"]:
        """Get user's order history."""
        ...
```

### 2. Complex Forward References

Handle nested or generic forward references:

```python
from typing import TYPE_CHECKING, Protocol, Generic, TypeVar, List, Dict, Callable

if TYPE_CHECKING:
    from external.models import BaseModel, ProcessingResult
    from external.validators import ValidationRule

T = TypeVar('T', bound='BaseModel')
R = TypeVar('R', bound='ProcessingResult')

class ProtocolModelProcessor(Protocol, Generic[T, R]):
    """Generic model processor with forward references."""
    
    def process_single(
        self, 
        model: T, 
        rules: List["ValidationRule"]
    ) -> R:
        """Process single model with validation rules."""
        ...
    
    def process_batch(
        self, 
        models: List[T],
        rules: List["ValidationRule"],
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[R]:
        """Process batch of models."""
        ...
    
    def validate_model(self, model: T) -> List["ValidationRule"]:
        """Get applicable validation rules for model."""
        ...
```

### 3. Avoiding Circular References

Structure protocols to minimize circular dependencies:

```python
# ✅ GOOD - Clear dependency direction
from omnibase.protocols.types.core_types import ContextValue

class ProtocolEventData(Protocol):
    """Base event data protocol."""
    event_type: str
    timestamp: float
    metadata: Dict[str, ContextValue]

class ProtocolEventPublisher(Protocol):
    """Event publisher depends on event data."""
    def publish(self, event: ProtocolEventData) -> str: ...

class ProtocolEventSubscriber(Protocol):
    """Event subscriber depends on event data."""
    def handle_event(self, event: ProtocolEventData) -> None: ...

class ProtocolEventBus(Protocol):
    """Event bus composes publisher and subscriber."""
    def get_publisher(self) -> ProtocolEventPublisher: ...
    def get_subscriber(self) -> ProtocolEventSubscriber: ...

# ❌ AVOID - Circular dependencies
class ProtocolCircularEventBus(Protocol):
    def register_handler(self, handler: "ProtocolCircularEventHandler") -> None: ...

class ProtocolCircularEventHandler(Protocol):
    def set_event_bus(self, bus: "ProtocolCircularEventBus") -> None: ...  # Circular!
```

## Documentation Standards

### 1. Protocol Docstrings

Provide comprehensive documentation for protocols:

```python
class ProtocolFileStorage(Protocol):
    """
    Protocol for file storage operations.
    
    This protocol defines the contract for storing, retrieving, and managing
    files in various storage backends (local filesystem, cloud storage, etc.).
    
    All implementations must ensure:
    - Thread safety for concurrent access
    - Proper error handling and reporting
    - Consistent path handling across platforms
    - Atomic operations where possible
    
    Example:
        storage: ProtocolFileStorage = S3FileStorage(bucket="my-bucket")
        
        # Store a file
        file_id = storage.store_file(
            file_path=Path("./document.pdf"),
            storage_key="documents/2023/document.pdf",
            metadata={"content-type": "application/pdf"}
        )
        
        # Retrieve a file
        content = storage.get_file_content("documents/2023/document.pdf")
    """
    
    def store_file(
        self,
        file_path: Path,
        storage_key: str,
        metadata: Optional[Dict[str, ContextValue]] = None
    ) -> str:
        """
        Store a file in the storage backend.
        
        Args:
            file_path: Local path to the file to store
            storage_key: Unique key for the file in storage
            metadata: Optional metadata to associate with the file
            
        Returns:
            Unique identifier for the stored file
            
        Raises:
            FileNotFoundError: If the source file doesn't exist
            StorageError: If storage operation fails
            PermissionError: If access is denied
        """
        ...
    
    def get_file_content(self, storage_key: str) -> bytes:
        """
        Retrieve file content by storage key.
        
        Args:
            storage_key: Unique key for the file in storage
            
        Returns:
            File content as bytes
            
        Raises:
            FileNotFoundError: If the file doesn't exist in storage
            StorageError: If retrieval operation fails
        """
        ...
```

### 2. Method Documentation

Document method contracts clearly:

```python
class ProtocolDataValidator(Protocol):
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Checks if the provided email address follows RFC 5322 standards
        and has a valid domain format.
        
        Args:
            email: Email address string to validate
            
        Returns:
            True if email is valid, False otherwise
            
        Note:
            This method performs format validation only.
            It does not verify that the email address actually exists.
        """
        ...
    
    def validate_phone(
        self, 
        phone: str, 
        country_code: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Validate phone number format and optionally check country code.
        
        Args:
            phone: Phone number string to validate
            country_code: Optional ISO 3166-1 alpha-2 country code (e.g., "US")
                         If provided, validates against country-specific format
            
        Returns:
            Dictionary with validation results:
            - "format_valid": True if basic format is valid
            - "country_valid": True if country code format matches (if provided)
            - "length_valid": True if length is appropriate for country (if provided)
            
        Example:
            result = validator.validate_phone("+1-555-123-4567", "US")
            # Returns: {"format_valid": True, "country_valid": True, "length_valid": True}
        """
        ...
```

## Error Handling Patterns

### 1. Result Pattern

Use result types for operations that can fail:

```python
from typing import Protocol, Union, Optional
from dataclasses import dataclass

@dataclass
class OperationResult:
    """Result of an operation with success/failure indication."""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None

class ProtocolResilientService(Protocol):
    """Service protocol with robust error handling."""
    
    def process_data(self, data: Dict[str, ContextValue]) -> OperationResult:
        """
        Process data and return result with error handling.
        
        Returns:
            OperationResult with success/failure indication and details
        """
        ...
    
    def batch_process(
        self, 
        data_list: List[Dict[str, ContextValue]]
    ) -> List[OperationResult]:
        """
        Process batch of data items.
        
        Returns:
            List of results, one for each input item.
            Failed items are marked with success=False.
        """
        ...
```

### 2. Exception Documentation

Document expected exceptions in protocols:

```python
class ProtocolUserAuthentication(Protocol):
    """User authentication protocol with documented exceptions."""
    
    def authenticate_user(self, username: str, password: str) -> str:
        """
        Authenticate user credentials.
        
        Args:
            username: User's username or email
            password: User's password
            
        Returns:
            Authentication token for successful login
            
        Raises:
            AuthenticationError: When credentials are invalid
            AccountLockedError: When account is temporarily locked
            AccountDisabledError: When account is permanently disabled
            RateLimitError: When too many login attempts detected
            SystemError: When authentication system is unavailable
        """
        ...
    
    def validate_token(self, token: str) -> bool:
        """
        Validate authentication token.
        
        Args:
            token: Authentication token to validate
            
        Returns:
            True if token is valid and not expired
            
        Raises:
            TokenFormatError: When token format is invalid
            SystemError: When token validation system is unavailable
            
        Note:
            This method should not raise exceptions for expired or
            invalid tokens - it should return False instead.
        """
        ...
```

## Performance Considerations

### 1. Lazy Loading Protocols

Design protocols to support lazy loading:

```python
class ProtocolLazyDataLoader(Protocol):
    """Protocol for lazy data loading operations."""
    
    def is_loaded(self) -> bool:
        """Check if data is already loaded."""
        ...
    
    def load_metadata(self) -> Dict[str, ContextValue]:
        """Load only metadata (fast operation)."""
        ...
    
    def load_full_data(self) -> Any:
        """Load complete data (potentially expensive)."""
        ...
    
    def load_partial_data(self, fields: List[str]) -> Dict[str, Any]:
        """Load only specified fields (optimized operation)."""
        ...
    
    def prefetch_related(self, relations: List[str]) -> None:
        """Prefetch related data to avoid N+1 queries."""
        ...
```

### 2. Streaming Protocols

Support streaming for large data operations:

```python
from typing import Iterator, AsyncIterator

class ProtocolStreamProcessor(Protocol):
    """Protocol for streaming data processing."""
    
    def process_stream(
        self, 
        data_stream: Iterator[Dict[str, Any]]
    ) -> Iterator[Dict[str, Any]]:
        """Process data stream item by item."""
        ...
    
    def process_batch_stream(
        self,
        data_stream: Iterator[Dict[str, Any]],
        batch_size: int = 100
    ) -> Iterator[List[Dict[str, Any]]]:
        """Process data in batches for efficiency."""
        ...

class ProtocolAsyncStreamProcessor(Protocol):
    """Async protocol for streaming data processing."""
    
    async def process_async_stream(
        self, 
        data_stream: AsyncIterator[Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Asynchronously process data stream."""
        ...
```

## Testing-Friendly Design

### 1. Test Double Support

Design protocols to support easy testing:

```python
class ProtocolTestableService(Protocol):
    """Service protocol designed for easy testing."""
    
    def set_test_mode(self, enabled: bool) -> None:
        """Enable/disable test mode for deterministic behavior."""
        ...
    
    def get_operation_count(self) -> Dict[str, int]:
        """Get count of operations performed (for test verification)."""
        ...
    
    def reset_state(self) -> None:
        """Reset service state (for test cleanup)."""
        ...
    
    def process_data(self, data: Dict[str, Any]) -> Any:
        """Main business operation."""
        ...

# Test implementation
class TestServiceDouble(ProtocolTestableService):
    """Test double implementation for testing."""
    
    def __init__(self):
        self._test_mode = False
        self._operation_counts = {"process_data": 0}
        self._responses = {}
    
    def set_test_mode(self, enabled: bool) -> None:
        self._test_mode = enabled
    
    def get_operation_count(self) -> Dict[str, int]:
        return self._operation_counts.copy()
    
    def reset_state(self) -> None:
        self._operation_counts = {"process_data": 0}
        self._responses.clear()
    
    def set_response(self, method: str, response: Any) -> None:
        """Test helper to set predetermined responses."""
        self._responses[method] = response
    
    def process_data(self, data: Dict[str, Any]) -> Any:
        self._operation_counts["process_data"] += 1
        
        if "process_data" in self._responses:
            return self._responses["process_data"]
        
        # Default test behavior
        return {"test_result": True, "input": data}
```

## Protocol Evolution Strategies

### 1. Versioning Protocols

Design protocols for evolution:

```python
from omnibase.protocols.types.core_types import ProtocolSemVer

class ProtocolVersionedService(Protocol):
    """Service protocol with version support."""
    
    def get_protocol_version(self) -> ProtocolSemVer:
        """Get the protocol version implemented by this service."""
        ...
    
    def is_compatible_with(self, version: ProtocolSemVer) -> bool:
        """Check if this implementation is compatible with given version."""
        ...

# Version 1.0 protocol
class ProtocolUserServiceV1(ProtocolVersionedService, Protocol):
    """User service protocol version 1.0."""
    
    def create_user(self, name: str, email: str) -> str: ...
    def get_user(self, user_id: str) -> Optional[Dict[str, str]]: ...

# Version 2.0 protocol (backwards compatible)
class ProtocolUserServiceV2(ProtocolUserServiceV1, Protocol):
    """User service protocol version 2.0 - extends v1.0."""
    
    # New methods in v2.0
    def update_user_profile(
        self, 
        user_id: str, 
        profile_data: Dict[str, ContextValue]
    ) -> bool: ...
    
    def get_user_preferences(self, user_id: str) -> Dict[str, ContextValue]: ...
```

### 2. Deprecation Patterns

Handle protocol deprecation gracefully:

```python
import warnings
from typing import deprecated

class ProtocolLegacyService(Protocol):
    """Service protocol with deprecated methods."""
    
    def new_process_method(self, data: Dict[str, Any]) -> Any:
        """New preferred method for processing data."""
        ...
    
    @deprecated("Use new_process_method() instead. Will be removed in v3.0.")
    def old_process_method(self, data: Dict[str, Any]) -> Any:
        """Legacy method - use new_process_method() instead."""
        ...
    
    def process_with_options(
        self, 
        data: Dict[str, Any],
        legacy_option: Optional[bool] = None  # Deprecated parameter
    ) -> Any:
        """
        Process data with options.
        
        Args:
            data: Data to process
            legacy_option: Deprecated parameter, ignored in v2.0+
        """
        ...
```

Following these protocol design guidelines ensures that your protocols are maintainable, type-safe, testable, and ready for evolution as your system grows.