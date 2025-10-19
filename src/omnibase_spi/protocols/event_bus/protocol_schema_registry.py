"""
Schema Registry Protocol - ONEX SPI Interface

Protocol definition for schema registry integration.
Pure protocol interface following SPI zero-dependency principle.

Created: 2025-10-18
Reference: EVENT_BUS_ARCHITECTURE.md Phase 1
"""

from typing import Any, Dict, Optional, Protocol, Tuple, runtime_checkable


@runtime_checkable
class ProtocolSchemaRegistry(Protocol):
    """
    Protocol for schema registry integration.

    Defines contract for schema management and validation:
    - Schema registration (JSON Schema, Avro)
    - Schema retrieval with versioning
    - Event validation against schemas
    - Schema caching for performance
    - Compatibility checking (backward, forward, full)

    Implementations must provide:
    - HTTP client for Redpanda Schema Registry
    - JSON Schema validation
    - In-memory schema caching
    - SemVer versioning support

    Example:
        ```python
        from omnibase_spi.protocols.event_bus import ProtocolSchemaRegistry

        # Get registry implementation
        registry: ProtocolSchemaRegistry = create_schema_registry_client(
            schema_registry_url="http://redpanda:8081"
        )

        # Register schema
        schema_id = await registry.register_schema(
            subject="omninode.codegen.request.validate.v1-value",
            schema=event_schema
        )

        # Validate event
        is_valid, error = await registry.validate_event(
            subject="omninode.codegen.request.validate.v1-value",
            event_data=event_dict
        )

        if not is_valid:
            print(f"Validation error: {error}")

        await registry.close()
        ```

    Schema Naming Convention:
        Subject format: {topic}-{key|value}
        Example: "omninode.codegen.request.validate.v1-value"

    Versioning:
        Semantic versioning (SemVer) for schema evolution:
        - v1.0.0 - Initial schema
        - v1.1.0 - Backward-compatible additions
        - v2.0.0 - Breaking changes

    See Also:
        - ProtocolEventPublisher: Event publishing with validation
        - EVENT_BUS_ARCHITECTURE.md: Schema governance process
    """

    async def register_schema(
        self, subject: str, schema: Dict[str, Any], schema_type: str
    ) -> int:
        """
        Register schema with Schema Registry.

        Args:
            subject: Schema subject (e.g., "omninode.codegen.request.validate.v1-value")
            schema: JSON Schema definition
            schema_type: Schema type ("JSON", "AVRO", etc.)

        Returns:
            Schema ID from registry

        Raises:
            Exception: If registration fails

        Example:
            ```python
            schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "code_content": {"type": "string"},
                    "node_type": {"type": "string"}
                },
                "required": ["code_content", "node_type"]
            }

            schema_id = await registry.register_schema(
                subject="omninode.codegen.request.validate.v1-value",
                schema=schema
            )

            print(f"Schema registered with ID: {schema_id}")
            ```
        """
        ...

    async def get_schema(self, subject: str, version: str) -> Optional[Dict[str, Any]]:
        """
        Get schema from Schema Registry.

        Args:
            subject: Schema subject
            version: Schema version ("latest", "v1.0.0", etc.)

        Returns:
            JSON Schema definition or None if not found

        Example:
            ```python
            schema = await registry.get_schema(
                subject="omninode.codegen.request.validate.v1-value",
                version="latest"
            )

            if schema:
                print(f"Schema: {schema}")
            else:
                print("Schema not found")
            ```
        """
        ...

    async def validate_event(
        self, subject: str, event_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate event data against schema.

        Args:
            subject: Schema subject
            event_data: Event data to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, error description if invalid

        Example:
            ```python
            event_data = {
                "code_content": "class Test: pass",
                "node_type": "effect",
                "language": "python"
            }

            is_valid, error = await registry.validate_event(
                subject="omninode.codegen.request.validate.v1-value",
                event_data=event_data
            )

            if is_valid:
                print("Event is valid")
            else:
                print(f"Validation failed: {error}")
            ```
        """
        ...

    async def close(self) -> None:
        """
        Close schema registry client and release resources.

        Should be called during graceful shutdown.

        Example:
            ```python
            await registry.close()
            print("Schema registry client closed")
            ```
        """
        ...
