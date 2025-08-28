# Core Protocols API Reference

## Overview

Core protocols provide the fundamental interfaces for system-level operations in the ONEX ecosystem. These protocols cover logging, serialization, validation, workflow management, and node operations.

## Module: `omnibase.protocols.core`

### Simple Example Protocols

#### ProtocolSimpleSerializer

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleSerializer
```

**Purpose**: Basic serialization operations with no external dependencies.

**Methods**:

- `serialize(self, data: Any) -> str`
  - Serialize data to string representation
  - **Parameters**: `data` - Any data object to serialize
  - **Returns**: String representation of the data
  - **Raises**: Implementation-specific serialization errors

- `deserialize(self, data: str) -> Any`
  - Deserialize string back to original data
  - **Parameters**: `data` - String representation to deserialize
  - **Returns**: Original data object
  - **Raises**: Implementation-specific deserialization errors

- `get_format(self) -> str`
  - Get the serialization format name
  - **Returns**: Format identifier (e.g., "json", "xml", "yaml")

**Example Usage**:
```python
class JSONSerializer(ProtocolSimpleSerializer):
    def serialize(self, data: Any) -> str:
        import json
        return json.dumps(data)
    
    def deserialize(self, data: str) -> Any:
        import json
        return json.loads(data)
    
    def get_format(self) -> str:
        return "json"

serializer: ProtocolSimpleSerializer = JSONSerializer()
json_data = serializer.serialize({"key": "value"})
original_data = serializer.deserialize(json_data)
```

#### ProtocolSimpleLogger

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleLogger
```

**Purpose**: Basic logging operations using only built-in types.

**Methods**:

- `log(self, level: str, message: str, **kwargs: Any) -> None`
  - Log a message with given level
  - **Parameters**: 
    - `level` - Log level string (e.g., "INFO", "ERROR")
    - `message` - Log message text
    - `**kwargs` - Additional context data
  - **Returns**: None

- `is_enabled(self, level: str) -> bool`
  - Check if logging level is enabled
  - **Parameters**: `level` - Log level to check
  - **Returns**: True if level is enabled, False otherwise

**Example Usage**:
```python
class FileLogger(ProtocolSimpleLogger):
    def __init__(self, filepath: str):
        self.filepath = filepath
    
    def log(self, level: str, message: str, **kwargs: Any) -> None:
        with open(self.filepath, "a") as f:
            extras = " ".join(f"{k}={v}" for k, v in kwargs.items())
            f.write(f"[{level}] {message} {extras}\n")
    
    def is_enabled(self, level: str) -> bool:
        return level in ["INFO", "WARNING", "ERROR", "CRITICAL"]

logger: ProtocolSimpleLogger = FileLogger("/var/log/app.log")
logger.log("INFO", "Application started", user_id="123")
```

#### ProtocolSimpleEventHandler

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleEventHandler
```

**Purpose**: Simple event handling protocol for event-driven architectures.

**Methods**:

- `handle_event(self, event_type: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]`
  - Handle an event and optionally return response data
  - **Parameters**:
    - `event_type` - Type identifier for the event
    - `event_data` - Event payload data
  - **Returns**: Optional response data dictionary, None if no response
  - **Raises**: Implementation-specific event handling errors

- `can_handle(self, event_type: str) -> bool`
  - Check if this handler can process the given event type
  - **Parameters**: `event_type` - Event type to check
  - **Returns**: True if handler supports this event type

**Example Usage**:
```python
class UserEventHandler(ProtocolSimpleEventHandler):
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if event_type == "user.created":
            user_id = event_data.get("user_id")
            return {"status": "welcome_email_sent", "user_id": user_id}
        elif event_type == "user.deleted":
            return {"status": "cleanup_scheduled"}
        return None
    
    def can_handle(self, event_type: str) -> bool:
        return event_type in ["user.created", "user.updated", "user.deleted"]

handler: ProtocolSimpleEventHandler = UserEventHandler()
result = handler.handle_event("user.created", {"user_id": "user_123", "email": "user@example.com"})
```

### Advanced Core Protocols

#### ProtocolCanonicalSerializer

```python
from omnibase.protocols.core.protocol_canonical_serializer import ProtocolCanonicalSerializer
```

**Purpose**: Advanced serialization with canonical formatting and hash support.

**Methods**:

- `serialize(self, obj: Any) -> ProtocolSerializationResult`
  - Serialize object with result metadata
  - **Parameters**: `obj` - Object to serialize
  - **Returns**: `ProtocolSerializationResult` with success status, data, and error information

- `deserialize(self, data: str, expected_type: type[Any]) -> Any`
  - Deserialize with type expectations
  - **Parameters**:
    - `data` - Serialized string data
    - `expected_type` - Expected type of deserialized object
  - **Returns**: Deserialized object of expected type
  - **Raises**: Deserialization errors for invalid data

- `get_canonical_hash(self, obj: Any) -> str`
  - Get canonical hash of object
  - **Parameters**: `obj` - Object to hash
  - **Returns**: Canonical hash string (e.g., SHA-256 hex digest)
  - **Raises**: Serialization errors if object cannot be serialized

#### ProtocolLogger

```python
from omnibase.protocols.core.protocol_logger import ProtocolLogger
```

**Purpose**: Advanced logging with structured context and correlation support.

**Methods**:

- `log(self, level: LogLevel, message: str, correlation_id: Optional[UUID] = None, context: Optional[Dict[str, ContextValue]] = None) -> None`
  - Log message with structured context
  - **Parameters**:
    - `level` - Log level from `LogLevel` type
    - `message` - Log message text
    - `correlation_id` - Optional correlation UUID for tracing
    - `context` - Optional structured context data
  - **Returns**: None

- `log_structured(self, level: LogLevel, data: Dict[str, ContextValue], correlation_id: Optional[UUID] = None) -> None`
  - Log structured data directly
  - **Parameters**:
    - `level` - Log level
    - `data` - Structured log data
    - `correlation_id` - Optional correlation UUID
  - **Returns**: None

- `is_enabled(self, level: LogLevel) -> bool`
  - Check if logging level is enabled
  - **Parameters**: `level` - Log level to check
  - **Returns**: True if level is enabled

#### ProtocolSchemaLoader

```python
from omnibase.protocols.core.protocol_schema_loader import ProtocolSchemaLoader
```

**Purpose**: Load and validate schema definitions for data structures.

**Methods**:

- `load_schema(self, schema_id: str) -> ProtocolSchemaModel`
  - Load schema by identifier
  - **Parameters**: `schema_id` - Unique schema identifier
  - **Returns**: Schema model object
  - **Raises**: Schema loading errors for missing or invalid schemas

- `validate_against_schema(self, data: Dict[str, Any], schema_id: str) -> ProtocolValidationResult`
  - Validate data against schema
  - **Parameters**:
    - `data` - Data to validate
    - `schema_id` - Schema identifier for validation rules
  - **Returns**: Validation result with success status and error details

- `register_schema(self, schema_id: str, schema_definition: Dict[str, Any]) -> None`
  - Register new schema definition
  - **Parameters**:
    - `schema_id` - Unique identifier for schema
    - `schema_definition` - Schema definition data
  - **Returns**: None
  - **Raises**: Registration errors for invalid schemas

#### ProtocolWorkflowReducer

```python
from omnibase.protocols.core.protocol_workflow_reducer import ProtocolWorkflowReducer
```

**Purpose**: Workflow state management using reducer patterns.

**Methods**:

- `reduce(self, current_state: ProtocolState, action: ProtocolAction) -> ProtocolState`
  - Apply action to current state and return new state
  - **Parameters**:
    - `current_state` - Current workflow state
    - `action` - Action to apply
  - **Returns**: New state after applying action
  - **Raises**: Invalid action or state transition errors

- `get_initial_state(self) -> ProtocolState`
  - Get initial state for new workflows
  - **Returns**: Initial state object

- `is_valid_transition(self, state: ProtocolState, action: ProtocolAction) -> bool`
  - Check if action is valid for current state
  - **Parameters**:
    - `state` - Current state
    - `action` - Proposed action
  - **Returns**: True if transition is valid

#### ONEX-Specific Protocols

#### ProtocolOnexEnvelope

```python
from omnibase.protocols.core.protocol_onex_envelope import ProtocolOnexEnvelope
```

**Purpose**: Message envelope handling for ONEX communication.

**Methods**:

- `create_envelope(self, payload: Any, envelope_type: str, correlation_id: UUID) -> Dict[str, Any]`
  - Create message envelope
  - **Parameters**:
    - `payload` - Message payload data
    - `envelope_type` - Type of envelope/message
    - `correlation_id` - Correlation identifier
  - **Returns**: Envelope dictionary with metadata and payload

- `extract_payload(self, envelope: Dict[str, Any]) -> Any`
  - Extract payload from envelope
  - **Parameters**: `envelope` - Envelope dictionary
  - **Returns**: Payload data
  - **Raises**: Invalid envelope format errors

- `get_envelope_metadata(self, envelope: Dict[str, Any]) -> Dict[str, ContextValue]`
  - Get envelope metadata
  - **Parameters**: `envelope` - Envelope dictionary
  - **Returns**: Metadata dictionary

#### ProtocolOnexNode

```python
from omnibase.protocols.core.protocol_onex_node import ProtocolOnexNode
```

**Purpose**: ONEX node operations and lifecycle management.

**Methods**:

- `initialize_node(self, node_metadata: ProtocolNodeMetadataBlock) -> None`
  - Initialize node with metadata
  - **Parameters**: `node_metadata` - Node metadata and configuration
  - **Returns**: None
  - **Raises**: Node initialization errors

- `process_request(self, request_data: Dict[str, Any], correlation_id: UUID) -> ProtocolNodeResult`
  - Process incoming request
  - **Parameters**:
    - `request_data` - Request payload data
    - `correlation_id` - Request correlation identifier
  - **Returns**: Processing result with success/failure status

- `get_node_status(self) -> NodeStatus`
  - Get current node status
  - **Returns**: Node status ("active", "inactive", "error", "pending")

- `shutdown_node(self) -> None`
  - Gracefully shutdown node
  - **Returns**: None

#### ProtocolOnexValidation

```python
from omnibase.protocols.core.protocol_onex_validation import ProtocolOnexValidation
```

**Purpose**: ONEX-specific validation and verification operations.

**Methods**:

- `validate_node_metadata(self, metadata: ProtocolNodeMetadataBlock) -> ProtocolValidationResult`
  - Validate node metadata structure and content
  - **Parameters**: `metadata` - Node metadata to validate
  - **Returns**: Validation result with details

- `validate_message_envelope(self, envelope: Dict[str, Any]) -> ProtocolValidationResult`
  - Validate message envelope format
  - **Parameters**: `envelope` - Message envelope to validate
  - **Returns**: Validation result

- `verify_protocol_compliance(self, implementation: Any, protocol_version: ProtocolSemVer) -> ProtocolValidationResult`
  - Verify implementation complies with protocol version
  - **Parameters**:
    - `implementation` - Implementation to verify
    - `protocol_version` - Expected protocol version
  - **Returns**: Compliance validation result

## Usage Examples

### Complete Service Implementation

```python
from omnibase.protocols.core.protocol_logger import ProtocolLogger
from omnibase.protocols.core.protocol_canonical_serializer import ProtocolCanonicalSerializer
from omnibase.protocols.types.core_types import LogLevel, ProtocolSerializationResult
from uuid import UUID, uuid4
import json

class DataProcessingService:
    """Service using multiple core protocols."""
    
    def __init__(
        self,
        logger: ProtocolLogger,
        serializer: ProtocolCanonicalSerializer
    ):
        self._logger = logger
        self._serializer = serializer
    
    def process_user_data(self, user_data: Dict[str, Any]) -> str:
        """Process user data with logging and serialization."""
        correlation_id = uuid4()
        
        self._logger.log(
            LogLevel.INFO,
            "Processing user data",
            correlation_id=correlation_id,
            context={"user_id": user_data.get("id", "unknown")}
        )
        
        try:
            # Process data
            processed_data = {
                "id": user_data.get("id"),
                "name": user_data.get("name", "").title(),
                "email": user_data.get("email", "").lower(),
                "processed_at": "2025-08-28T10:00:00Z"
            }
            
            # Serialize result
            result = self._serializer.serialize(processed_data)
            
            if result.success:
                self._logger.log(
                    LogLevel.INFO,
                    "User data processed successfully",
                    correlation_id=correlation_id,
                    context={"output_size": len(result.data)}
                )
                return result.data
            else:
                self._logger.log(
                    LogLevel.ERROR,
                    f"Serialization failed: {result.error_message}",
                    correlation_id=correlation_id
                )
                raise ValueError(f"Processing failed: {result.error_message}")
                
        except Exception as e:
            self._logger.log(
                LogLevel.ERROR,
                f"Processing error: {e}",
                correlation_id=correlation_id,
                context={"error_type": type(e).__name__}
            )
            raise

# Usage with implementations
service = DataProcessingService(
    logger=MyLogger(),
    serializer=MyCanonicalSerializer()
)

result = service.process_user_data({
    "id": "user_123",
    "name": "john doe",
    "email": "JOHN@EXAMPLE.COM"
})
```

### Event-Driven Workflow

```python
from omnibase.protocols.core.protocol_simple_example import ProtocolSimpleEventHandler
from omnibase.protocols.core.protocol_workflow_reducer import ProtocolWorkflowReducer

class WorkflowEventProcessor:
    """Combine event handling with workflow state management."""
    
    def __init__(
        self,
        event_handler: ProtocolSimpleEventHandler,
        workflow_reducer: ProtocolWorkflowReducer
    ):
        self._event_handler = event_handler
        self._workflow_reducer = workflow_reducer
        self._current_state = workflow_reducer.get_initial_state()
    
    def process_event(self, event_type: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process event and update workflow state."""
        # Handle event
        event_result = self._event_handler.handle_event(event_type, event_data)
        
        if event_result is None:
            return None
        
        # Create workflow action from event result
        action = ProtocolAction(
            type=event_type,
            payload=ProtocolActionPayload(
                target_id=event_data.get("target_id", "unknown"),
                operation=event_type,
                parameters=event_result
            ),
            timestamp=datetime.now()
        )
        
        # Update workflow state
        if self._workflow_reducer.is_valid_transition(self._current_state, action):
            self._current_state = self._workflow_reducer.reduce(self._current_state, action)
            return {
                "event_processed": True,
                "new_state": self._current_state,
                "event_result": event_result
            }
        else:
            return {
                "event_processed": False,
                "error": "Invalid state transition",
                "current_state": self._current_state
            }
```

## Type Definitions

All core protocols use types from `omnibase.protocols.types.core_types`:

- `LogLevel`: `Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]`
- `NodeStatus`: `Literal["active", "inactive", "error", "pending"]` 
- `ContextValue`: `Union[str, int, float, bool, List[str], Dict[str, str]]`
- `ProtocolSemVer`: Protocol for semantic version objects
- `ProtocolSerializationResult`: Protocol for serialization results
- `ProtocolValidationResult`: Protocol for validation results
- `ProtocolNodeMetadataBlock`: Protocol for node metadata
- `ProtocolState`: Protocol for workflow state
- `ProtocolAction`: Protocol for workflow actions