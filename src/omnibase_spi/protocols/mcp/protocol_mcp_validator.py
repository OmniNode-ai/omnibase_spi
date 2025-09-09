#!/usr/bin/env python3
"""
MCP Validator Protocol - ONEX SPI Interface.

Protocol definition for MCP validation operations.
Provides comprehensive validation for registrations, tool definitions, and execution parameters.

Domain: MCP validation and quality assurance
"""

from typing import Any, Optional, Protocol, runtime_checkable

from omnibase_spi.protocols.types.core_types import (
    ContextValue,
    ProtocolValidationResult,
)
from omnibase_spi.protocols.types.mcp_types import (
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPToolDefinition,
    ProtocolMCPValidationError,
    ProtocolMCPValidationResult,
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
    ) -> ProtocolMCPValidationResult:
        """
        Validate a tool definition for completeness and correctness.

        Args:
            tool_def: Tool definition to validate

        Returns:
            Validation result with errors and warnings
        """
        ...

    async def validate_tool_parameters(
        self,
        tool_def: ProtocolMCPToolDefinition,
        parameters: dict[str, ContextValue],
    ) -> ProtocolValidationResult:
        """
        Validate tool execution parameters against definition.

        Args:
            tool_def: Tool definition with parameter schema
            parameters: Parameters to validate

        Returns:
            Validation result
        """
        ...

    async def validate_parameter_schema(
        self, schema: dict[str, Any]
    ) -> ProtocolMCPValidationResult:
        """
        Validate a parameter schema definition.

        Args:
            schema: Parameter schema to validate

        Returns:
            Validation result
        """
        ...

    async def sanitize_parameters(
        self,
        tool_def: ProtocolMCPToolDefinition,
        parameters: dict[str, ContextValue],
    ) -> dict[str, ContextValue]:
        """
        Sanitize and normalize tool parameters.

        Args:
            tool_def: Tool definition
            parameters: Parameters to sanitize

        Returns:
            Sanitized parameters
        """
        ...


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
    def tool_validator(self) -> ProtocolMCPToolValidator:
        """Get the tool validator implementation."""
        ...

    async def validate_subsystem_registration(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
        api_key: str,
    ) -> ProtocolMCPValidationResult:
        """
        Validate complete subsystem registration data.

        Args:
            subsystem_metadata: Subsystem metadata to validate
            tools: Tool definitions to validate
            api_key: API key to validate

        Returns:
            Comprehensive validation result
        """
        ...

    async def validate_execution_request(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        subsystem_id: Optional[str],
    ) -> ProtocolValidationResult:
        """
        Validate tool execution request.

        Args:
            tool_name: Name of tool to execute
            parameters: Execution parameters
            subsystem_id: Optional target subsystem

        Returns:
            Validation result for execution request
        """
        ...

    async def validate_api_key(
        self, api_key: str, subsystem_id: Optional[str] = None
    ) -> bool:
        """
        Validate API key format and authenticity.

        Args:
            api_key: API key to validate
            subsystem_id: Optional subsystem context

        Returns:
            True if API key is valid
        """
        ...

    async def validate_configuration(
        self, configuration: dict[str, ContextValue]
    ) -> ProtocolMCPValidationResult:
        """
        Validate system configuration.

        Args:
            configuration: Configuration to validate

        Returns:
            Configuration validation result
        """
        ...

    async def validate_network_access(
        self, base_url: str, endpoints: list[str]
    ) -> ProtocolMCPValidationResult:
        """
        Validate network accessibility of subsystem endpoints.

        Args:
            base_url: Base URL of subsystem
            endpoints: List of endpoints to validate

        Returns:
            Network validation result
        """
        ...

    async def sanitize_subsystem_metadata(
        self, metadata: ProtocolMCPSubsystemMetadata
    ) -> ProtocolMCPSubsystemMetadata:
        """
        Sanitize and normalize subsystem metadata.

        Args:
            metadata: Metadata to sanitize

        Returns:
            Sanitized metadata
        """
        ...

    async def detect_security_issues(
        self,
        parameters: dict[str, ContextValue],
        tool_definition: Optional[ProtocolMCPToolDefinition],
    ) -> list[ProtocolMCPValidationError]:
        """
        Detect potential security issues in parameters.

        Args:
            parameters: Parameters to analyze
            tool_definition: Optional tool context

        Returns:
            List of security validation errors
        """
        ...

    async def validate_compatibility(
        self,
        subsystem_version: str,
        registry_version: str,
        tools: list[ProtocolMCPToolDefinition],
    ) -> ProtocolMCPValidationResult:
        """
        Validate version compatibility.

        Args:
            subsystem_version: Version of subsystem
            registry_version: Version of registry
            tools: Tool definitions to check

        Returns:
            Compatibility validation result
        """
        ...

    async def validate_performance_constraints(
        self,
        tools: list[ProtocolMCPToolDefinition],
        expected_load: Optional[dict[str, Any]],
    ) -> ProtocolMCPValidationResult:
        """
        Validate performance constraints and limits.

        Args:
            tools: Tool definitions to validate
            expected_load: Optional expected load patterns

        Returns:
            Performance validation result
        """
        ...

    async def get_validation_rules(self) -> dict[str, Any]:
        """
        Get current validation rules and constraints.

        Returns:
            Dictionary of validation rules
        """
        ...

    async def update_validation_rules(self, rules: dict[str, Any]) -> bool:
        """
        Update validation rules dynamically.

        Args:
            rules: New validation rules

        Returns:
            True if rules updated successfully
        """
        ...
