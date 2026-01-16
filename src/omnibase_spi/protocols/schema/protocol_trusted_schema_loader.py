"""Protocols for secure schema loading with path safety validation."""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


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

    def to_dict(self) -> "JsonType":
        """Convert the validation result to a JSON-compatible dictionary.

        Serializes the validation result including success status and all
        message categories for logging, reporting, or API responses.

        Returns:
            JSON-compatible dictionary containing 'success', 'errors',
            'warnings', and 'info' keys with their respective values.

        Raises:
            SPIError: When serialization fails due to invalid message content.
        """
        ...


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
        """Check if a path is safe for schema loading.

        Validates that the given path does not attempt path traversal
        attacks and is within approved root directories. Returns safety
        status via tuple rather than raising exceptions, allowing callers
        to handle unsafe paths gracefully.

        Args:
            path_str: The path to validate for safety.

        Returns:
            Tuple of (is_safe, message) where is_safe indicates whether
            the path is safe to load, and message provides details about
            any security concerns if unsafe.

        Raises:
            SPIError: When path validation fails due to system errors.
        """
        ...

    async def load_schema_safely(
        self, schema_path: str
    ) -> "ProtocolSchemaValidationResult":
        """Safely load a schema file with security validation.

        Loads the schema from the given path after validating that
        the path is within approved roots and does not contain
        path traversal attempts.

        Args:
            schema_path: Path to the schema file to load.

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages.

        Raises:
            SecurityError: If the path fails safety validation.
        """
        ...

    async def resolve_ref_safely(
        self, ref_string: str
    ) -> "ProtocolSchemaValidationResult":
        """Safely resolve a $ref string with security validation.

        Resolves JSON Schema $ref references while ensuring the
        referenced paths are within approved roots.

        Args:
            ref_string: The $ref string to resolve (e.g., "#/definitions/User").

        Returns:
            Validation result containing success status and any
            errors, warnings, or informational messages.

        Raises:
            SecurityError: If the reference points to an unapproved location.
        """
        ...

    async def get_security_audit(self) -> "list[JsonType]":
        """Get security audit trail.

        Retrieves the audit log of all security-related operations
        performed by this loader, including path validations and
        access attempts.

        Returns:
            List of audit entries as JSON-compatible dictionaries, each
            containing timestamp, operation type, and result. Returns
            empty list if no audit entries exist.

        Raises:
            SPIError: When audit retrieval fails due to storage errors.
        """
        ...

    def clear_cache(self) -> None:
        """Clear schema cache.

        Removes all cached schemas from memory, forcing subsequent
        loads to read from disk. Use when schemas may have changed
        on disk or to free memory.

        Raises:
            SPIError: When cache clearing fails due to concurrent access
                or resource cleanup errors.
        """
        ...

    async def get_approved_roots(self) -> list[str]:
        """Get list of approved schema root paths.

        Returns the list of directory paths that are approved for
        schema loading. Only schemas within these roots can be loaded.
        Returns empty list if no roots are configured.

        Returns:
            List of absolute paths to approved schema root directories.
        """
        ...
