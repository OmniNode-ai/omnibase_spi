from typing import Any, Protocol, runtime_checkable

from omnibase_spi.protocols.types import ProtocolOnexResult


@runtime_checkable
class ProtocolValidationResult(Protocol):
    """Protocol for validation results."""

    success: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolTrustedSchemaLoader(Protocol):
    """Protocol for secure schema loading and validation"""

    def is_path_safe(self, path_str: str) -> tuple[bool, str]:
        """Check if a path is safe for schema loading"""
        ...

    async def load_schema_safely(self, schema_path: str) -> "ProtocolValidationResult":
        """Safely load a schema file with security validation"""
        ...

    async def resolve_ref_safely(self, ref_string: str) -> "ProtocolValidationResult":
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
