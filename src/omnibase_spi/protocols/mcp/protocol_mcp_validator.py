"""
MCP Validator Protocol - ONEX SPI Interface.

Protocol definition for MCP validation operations.
Provides comprehensive validation for registrations, tool definitions, and execution parameters.

Domain: MCP validation and quality assurance
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue
from omnibase_spi.protocols.types.protocol_mcp_types import (
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPToolDefinition,
    ProtocolMCPValidationError,
    ProtocolMCPValidationResult,
)
from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
)


@runtime_checkable
class ProtocolMCPToolValidator(Protocol):
    """
    Protocol for MCP tool validation operations.

    Handles validation of tool definitions, parameters,
    and execution requests for security and correctness.
    """

    async def validate_tool_definition(
        self, tool_def: ProtocolMCPToolDefinition
    ) -> ProtocolMCPValidationResult: ...

    async def validate_tool_parameters(
        self, tool_def: ProtocolMCPToolDefinition, parameters: dict[str, ContextValue]
    ) -> ProtocolValidationResult: ...

    async def validate_parameter_schema(
        self, schema: dict[str, ContextValue]
    ) -> ProtocolMCPValidationResult: ...

    async def sanitize_parameters(
        self, tool_def: ProtocolMCPToolDefinition, parameters: dict[str, ContextValue]
    ) -> dict[str, ContextValue]: ...


@runtime_checkable
class ProtocolMCPValidator(Protocol):
    """
    Comprehensive MCP validation protocol for all MCP operations.

    Provides validation for subsystem registrations, tool definitions,
    execution parameters, and system configurations.

    Key Features:
        - **Schema Validation**: Validate against JSON schemas and type definitions
        - **Security Validation**: Detect potential security issues in parameters
        - **Business Rule Validation**: Enforce business rules and constraints
        - **Performance Validation**: Check for performance-impacting configurations
        - **Compatibility Validation**: Ensure compatibility across versions
        - **Sanitization**: Clean and normalize input data
        - **Detailed Error Reporting**: Provide actionable error messages and suggestions
    """

    @property
    def tool_validator(self) -> ProtocolMCPToolValidator: ...

    async def validate_subsystem_registration(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
        api_key: str,
    ) -> ProtocolMCPValidationResult: ...

    async def validate_execution_request(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        subsystem_id: str | None,
    ) -> ProtocolValidationResult: ...

    async def validate_api_key(
        self, api_key: str, subsystem_id: str | None = None
    ) -> bool: ...

    async def validate_configuration(
        self, configuration: dict[str, ContextValue]
    ) -> ProtocolMCPValidationResult: ...

    async def validate_network_access(
        self, base_url: str, endpoints: list[str]
    ) -> ProtocolMCPValidationResult: ...

    async def sanitize_subsystem_metadata(
        self, metadata: ProtocolMCPSubsystemMetadata
    ) -> ProtocolMCPSubsystemMetadata: ...

    async def detect_security_issues(
        self,
        parameters: dict[str, ContextValue],
        tool_definition: ProtocolMCPToolDefinition | None,
    ) -> list[ProtocolMCPValidationError]: ...

    async def validate_compatibility(
        self,
        subsystem_version: str,
        registry_version: str,
        tools: list[ProtocolMCPToolDefinition],
    ) -> ProtocolMCPValidationResult: ...

    async def validate_performance_constraints(
        self,
        tools: list[ProtocolMCPToolDefinition],
        expected_load: dict[str, ContextValue] | None,
    ) -> ProtocolMCPValidationResult: ...

    async def get_validation_rules(self) -> dict[str, ContextValue]: ...

    async def update_validation_rules(self, rules: dict[str, ContextValue]) -> bool: ...
