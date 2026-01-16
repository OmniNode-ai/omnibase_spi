"""
Validation and compatibility protocol types for ONEX SPI interfaces.

Domain: Validation, compatibility checking, and model serialization.

This module contains protocols for:
- Object validation (ProtocolValidatable, ProtocolModelValidatable)
- Version compatibility (ProtocolVersionInfo, ProtocolCompatibilityCheck)
- Model serialization (ProtocolHasModelDump, ProtocolModelJsonSerializable)
- Code pattern checking (ProtocolPatternChecker)
"""

from typing import Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    ProtocolDateTime,
    ProtocolSemVer,
)

# ==============================================================================
# Version and Compatibility Protocols
# ==============================================================================


@runtime_checkable
class ProtocolVersionInfo(Protocol):
    """
    Protocol for version metadata and compatibility information.

    Provides comprehensive version information for protocols including
    current version, minimum compatible version, retirement scheduling,
    and migration guidance. Enables version negotiation and compatibility
    checking in distributed ONEX systems.

    Attributes:
        protocol_name: Name of the protocol this version info describes.
        version: Current semantic version of the protocol.
        compatibility_version: Minimum compatible version for interoperability.
        retirement_date: Scheduled retirement date; None if not planned.
        migration_guide_url: URL to migration documentation; None if not available.

    Example:
        ```python
        class MemoryProtocolVersionInfo:
            protocol_name: str = "ProtocolMemoryOperation"
            version: ProtocolSemVer = SemVer(2, 1, 0)
            compatibility_version: ProtocolSemVer = SemVer(2, 0, 0)
            retirement_date: ProtocolDateTime | None = None
            migration_guide_url: str | None = "https://docs.onex.ai/migration/memory-v2"

            async def validate_version_info(self) -> bool:
                return self.version >= self.compatibility_version

            def is_compatible(self) -> bool:
                return self.retirement_date is None

        info = MemoryProtocolVersionInfo()
        assert isinstance(info, ProtocolVersionInfo)
        assert info.is_compatible()
        ```
    """

    protocol_name: str
    version: "ProtocolSemVer"
    compatibility_version: "ProtocolSemVer"
    retirement_date: "ProtocolDateTime | None"
    migration_guide_url: str | None

    async def validate_version_info(self) -> bool: ...

    def is_compatible(self) -> bool: ...


@runtime_checkable
class ProtocolCompatibilityCheck(Protocol):
    """
    Protocol for compatibility checking results between protocol versions.

    Captures the result of a compatibility check between two protocol
    versions, including compatibility status, version details, list of
    breaking changes, and migration requirements. Enables informed
    decisions about protocol upgrades and interoperability.

    Attributes:
        is_compatible: Whether the versions are compatible for interoperation.
        required_version: The version required by the dependent component.
        current_version: The version currently available or installed.
        breaking_changes: List of breaking changes between versions.
        migration_required: Whether data or code migration is necessary.

    Example:
        ```python
        class IncompatibleCheckResult:
            is_compatible: bool = False
            required_version: ProtocolSemVer = SemVer(3, 0, 0)
            current_version: ProtocolSemVer = SemVer(2, 5, 0)
            breaking_changes: list[str] = [
                "Removed deprecated method 'get_legacy_data'",
                "Changed return type of 'execute' from dict to Result"
            ]
            migration_required: bool = True

            async def validate_compatibility(self) -> bool:
                return len(self.breaking_changes) == 0 or not self.migration_required

        check = IncompatibleCheckResult()
        assert isinstance(check, ProtocolCompatibilityCheck)
        assert not check.is_compatible
        assert len(check.breaking_changes) == 2
        ```
    """

    is_compatible: bool
    required_version: "ProtocolSemVer"
    current_version: "ProtocolSemVer"
    breaking_changes: list[str]
    migration_required: bool

    async def validate_compatibility(self) -> bool: ...


# ==============================================================================
# Validation Protocols
# ==============================================================================


@runtime_checkable
class ProtocolValidatable(Protocol):
    """
    Base protocol for objects that can be validated.

    This protocol defines the minimal interface that validation targets
    should implement to provide context and metadata for validation
    operations. By implementing this protocol, objects become compatible
    with the ONEX validation framework while maintaining type safety.

    Key Features:
        - Validation context extraction for rule applicability
        - Object identification for validation reporting
        - Type safety for validation operations
        - Minimal interface requirements for broad compatibility

    Usage:
        class ConfigurationData(ProtocolValidatable):
            def get_validation_context(self) -> dict[str, "ContextValue"]:
                return {"type": "config", "version": self.version}

            def get_validation_id(self) -> str:
                return f"config_{self.name}"
    """

    async def get_validation_context(self) -> dict[str, "ContextValue"]: ...

    async def get_validation_id(self) -> str: ...

    ...


@runtime_checkable
class ProtocolModelValidatable(Protocol):
    """
    Protocol for values that can validate themselves.

    Provides self-validation interface for objects with built-in
    validation logic. Used across ONEX for data validation before
    processing or persistence.

    Key Features:
        - Self-validation capability
        - Error collection and reporting
        - Boolean validation result
        - Detailed error messages

    Usage:
        def process_data(data: ProtocolModelValidatable):
            if data.is_valid():
                process(data)
            else:
                log_errors(data.get_errors())
    """

    def is_valid(self) -> bool:
        """Check if the value is valid."""
        ...

    async def get_errors(self) -> list[str]:
        """Get validation errors."""
        ...


# ==============================================================================
# Model Serialization Protocols
# ==============================================================================


@runtime_checkable
class ProtocolHasModelDump(Protocol):
    """
    Protocol for objects that support Pydantic model_dump method.

    This protocol ensures compatibility with Pydantic models and other
    objects that provide dictionary serialization via model_dump.
    Used for consistent serialization across ONEX services.

    Key Features:
        - Pydantic model compatibility
        - Mode-based serialization (json, python)
        - Consistent serialization interface
        - Type-safe dictionary output

    Usage:
        def serialize_object(obj: ProtocolHasModelDump) -> dict[str, "ContextValue"]:
            return obj.model_dump(mode="json")
    """

    def model_dump(self, mode: str | None = None) -> dict[str, ContextValue]: ...


@runtime_checkable
class ProtocolModelJsonSerializable(Protocol):
    """
    Protocol for values that can be JSON serialized.

    Marker protocol for objects that can be safely serialized to JSON.
    Used throughout ONEX for data interchange and persistence.
    Built-in types that implement this: str, int, float, bool,
    list, dict, None. Use JsonType from omnibase_core.types for type hints.

    Key Features:
        - JSON serialization guarantee
        - Marker interface pattern
        - Runtime type checking support
        - Safe for data interchange

    Usage:
        def store_json(value: ProtocolModelJsonSerializable):
            json_data = json.dumps(value)
            save_to_storage(json_data)
    """

    __omnibase_json_serializable_marker__: Literal[True]


# ==============================================================================
# Pattern Checking Protocol
# ==============================================================================


@runtime_checkable
class ProtocolPatternChecker(Protocol):
    """
    Protocol for AST pattern checker objects.

    Defines the interface for pattern checkers used in code validation
    and AST analysis. Pattern checkers traverse AST nodes to identify
    and validate code patterns.

    Key Features:
        - AST node traversal support
        - Issue collection and reporting
        - Pattern validation framework
        - Code quality checking

    Usage:
        checker = create_pattern_checker()
        checker.visit(ast_node)
        if checker.issues:
            report_violations(checker.issues)
    """

    issues: list[str]

    def visit(self, node: object) -> None: ...  # ast.AST type
