from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolSchemaValidationResult(Protocol):
    """
    Protocol for schema validation operation result.

    Captures the outcome of schema loading or validation operations
    including success status, categorized messages, and serialization
    support for result reporting and logging.

    Attributes:
        success: Whether the operation completed successfully
        errors: List of critical error messages
        warnings: List of warning messages
        info: List of informational messages

    Example:
        ```python
        loader: ProtocolTrustedSchemaLoader = get_trusted_loader()
        result = await loader.load_schema_safely("/path/to/schema.json")

        if result.success:
            print("Schema loaded successfully")
        else:
            for error in result.errors:
                print(f"Error: {error}")

        result_dict = result.to_dict()
        ```

    See Also:
        - ProtocolTrustedSchemaLoader: Schema loading operations
        - ProtocolModelRegistryValidator: Registry validation
    """

    success: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolTrustedSchemaLoader(Protocol):
    """
    Protocol for secure schema loading with path safety validation.

    Provides security-hardened schema loading operations including
    path traversal prevention, approved root validation, reference
    resolution with security checks, and audit trail maintenance.

    Example:
        ```python
        loader: ProtocolTrustedSchemaLoader = get_trusted_loader()

        # Check path safety before loading
        is_safe, message = loader.is_path_safe("/etc/passwd")
        if not is_safe:
            print(f"Unsafe path: {message}")
            return

        # Load schema with security validation
        result = await loader.load_schema_safely("/approved/schemas/model.json")
        if result.success:
            print("Schema loaded securely")

        # Resolve $ref with security checks
        ref_result = await loader.resolve_ref_safely("#/definitions/User")

        # Get security audit trail
        audit = await loader.get_security_audit()
        for entry in audit:
            print(f"Audit: {entry}")

        # Get approved schema roots
        roots = await loader.get_approved_roots()
        print(f"Approved roots: {roots}")
        ```

    See Also:
        - ProtocolSchemaValidationResult: Loading results
        - ProtocolSchemaLoader: Basic schema loading
    """

    def is_path_safe(self, path_str: str) -> tuple[bool, str]:
        """Check if a path is safe for schema loading"""
        ...

    async def load_schema_safely(
        self, schema_path: str
    ) -> "ProtocolSchemaValidationResult":
        """Safely load a schema file with security validation"""
        ...

    async def resolve_ref_safely(
        self, ref_string: str
    ) -> "ProtocolSchemaValidationResult":
        """Safely resolve a $ref string with security validation"""
        ...

    async def get_security_audit(self) -> list[dict[str, Any]]:
        """Get security audit trail"""
        ...

    def clear_cache(self) -> None:
        """Clear schema cache"""
        ...

    async def get_approved_roots(self) -> list[str]:
        """Get list[Any]of approved schema root paths"""
        ...
