"""
Protocol interfaces for agent configuration management.

This module defines pure protocol interfaces for agent configuration operations,
replacing concrete model dependencies with protocol abstractions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolAgentConfig(Protocol):
    """
    Protocol for agent configuration data structure and security operations.

    Defines the complete configuration contract for AI agent instances
    including identity, capabilities, permissions, resource constraints,
    and security operations for sensitive data handling.

    Example:
        ```python
        async def configure_agent(config: ProtocolAgentConfig) -> bool:
            # Validate configuration security
            if not config.is_valid:
                return False

            # Check security requirements
            violations = await config.validate_security()
            if violations:
                print(f"Security issues: {violations}")
                return False

            # Encrypt sensitive data before storage
            encrypted = await config.encrypt_sensitive_data()
            await save_configuration(encrypted)

            return True
        ```

    Key Features:
        - **Identity Management**: Agent ID and naming for tracking
        - **Capability Control**: Explicit capability declarations
        - **Permission System**: Fine-grained permission management
        - **Resource Limits**: CPU, memory, and I/O constraints
        - **Security Operations**: Built-in encryption/decryption
        - **Validation Support**: Comprehensive security validation

    See Also:
        - ProtocolAgentValidationResult: Validation result structure
        - ProtocolAgentConfiguration: Configuration management operations
        - ProtocolMemoryAgentInstance: Agent instance runtime state
    """

    agent_id: str
    name: str
    model: str
    capabilities: list[str]
    permissions: list[str]
    resource_limits: dict[str, int]
    configuration: dict[str, ContextValue]

    @property
    def is_valid(self) -> bool: ...

    @property
    def security_level(self) -> str: ...

    async def validate_security(self) -> list[str]: ...

    async def encrypt_sensitive_data(self) -> ProtocolAgentConfig: ...

    async def decrypt_sensitive_data(self) -> ProtocolAgentConfig: ...


@runtime_checkable
class ProtocolAgentValidationResult(Protocol):
    """
    Protocol for agent configuration validation results.

    Provides comprehensive validation feedback including errors,
    warnings, recommendations, and a quantitative quality score
    for agent configuration validation operations.

    Example:
        ```python
        async def validate_and_report(
            config: ProtocolAgentConfig,
            validator: ProtocolAgentConfiguration
        ) -> str:
            result = await validator.validate_configuration(config)

            if result.has_errors:
                print(f"Validation failed with {len(result.errors)} errors")
                for error in result.errors:
                    print(f"  ERROR: {error}")
                return "failed"

            if result.has_warnings:
                print(f"Warnings: {len(result.warnings)}")

            print(f"Configuration score: {result.score:.2f}")
            return "success" if result.is_valid else "warnings"
        ```

    Key Features:
        - **Binary Validation**: Clear valid/invalid status
        - **Error Tracking**: Comprehensive error collection
        - **Warning System**: Non-blocking warning notifications
        - **Recommendations**: Actionable improvement suggestions
        - **Quality Scoring**: Quantitative configuration quality metric
        - **Incremental Building**: Add errors/warnings dynamically

    See Also:
        - ProtocolAgentConfig: Configuration data structure
        - ProtocolAgentConfiguration: Validation operations
        - ProtocolComplianceValidator: Compliance validation protocol
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    recommendations: list[str]
    score: float

    @property
    def has_errors(self) -> bool: ...

    @property
    def has_warnings(self) -> bool: ...

    def add_error(self, error: str) -> None: ...

    def add_warning(self, warning: str) -> None: ...

    def add_recommendation(self, recommendation: str) -> None: ...


@runtime_checkable
class ProtocolAgentConfiguration(Protocol):
    """Protocol for agent configuration management operations."""

    async def validate_configuration(
        self,
        config: ProtocolAgentConfig,
    ) -> ProtocolAgentValidationResult:
        """
        Validate agent configuration for correctness and security.

        Args:
            config: Agent configuration to validate

        Returns:
            Validation result with issues and recommendations

        Raises:
            ValidationError: If validation process fails
        """
        ...

    async def save_configuration(self, config: ProtocolAgentConfig) -> bool:
        """
        Save agent configuration to persistent storage.

        Args:
            config: Agent configuration to save

        Returns:
            True if configuration was saved successfully

        Raises:
            ConfigurationError: If saving fails
            SecurityError: If configuration violates security policies
        """
        ...

    async def load_configuration(self, agent_id: str) -> ProtocolAgentConfig | None:
        """
        Load agent configuration from persistent storage.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent configuration or None if not found

        Raises:
            ConfigurationError: If loading fails
        """
        ...

    async def delete_configuration(self, agent_id: str) -> bool:
        """
        Delete agent configuration from persistent storage.

        Args:
            agent_id: Agent identifier

        Returns:
            True if configuration was deleted successfully

        Raises:
            ConfigurationError: If deletion fails
        """
        ...

    async def list_configurations(self) -> list[str]:
        """
        List all available agent configuration IDs.

        Returns:
            List of agent IDs with saved configurations
        """
        ...

    async def update_configuration(
        self,
        agent_id: str,
        updates: dict[str, ContextValue],
    ) -> ProtocolAgentConfig:
        """
        Update specific fields in an agent configuration.

        Args:
            agent_id: Agent identifier
            updates: Dictionary of field updates

        Returns:
            Updated agent configuration

        Raises:
            ConfigurationError: If update fails
            ValidationError: If updated configuration is invalid
        """
        ...

    async def create_configuration_template(
        self,
        template_name: str,
        base_config: ProtocolAgentConfig,
    ) -> bool:
        """
        Create a reusable configuration template.

        Args:
            template_name: Name for the template
            base_config: Base configuration to use as template

        Returns:
            True if template was created successfully

        Raises:
            ConfigurationError: If template creation fails
        """
        ...

    async def apply_configuration_template(
        self,
        agent_id: str,
        template_name: str,
        overrides: dict[str, ContextValue] | None = None,
    ) -> ProtocolAgentConfig:
        """
        Apply a configuration template to create agent configuration.

        Args:
            agent_id: Agent identifier
            template_name: Name of template to apply
            overrides: Optional field overrides

        Returns:
            Generated agent configuration

        Raises:
            ConfigurationError: If template application fails
            TemplateNotFoundError: If template doesn't exist
        """
        ...

    async def list_configuration_templates(self) -> list[str]:
        """
        List all available configuration templates.

        Returns:
            List of template names
        """
        ...

    async def backup_configuration(self, agent_id: str) -> str:
        """
        Create a backup of agent configuration.

        Args:
            agent_id: Agent identifier

        Returns:
            Backup identifier for restoration

        Raises:
            ConfigurationError: If backup creation fails
        """
        ...

    async def restore_configuration(self, agent_id: str, backup_id: str) -> bool:
        """
        Restore agent configuration from backup.

        Args:
            agent_id: Agent identifier
            backup_id: Backup identifier

        Returns:
            True if restoration was successful

        Raises:
            ConfigurationError: If restoration fails
            BackupNotFoundError: If backup doesn't exist
        """
        ...

    async def get_configuration_history(self, agent_id: str) -> list[dict[str, str]]:
        """
        Get configuration change history for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of configuration changes with timestamps and changes
        """
        ...

    async def clone_configuration(
        self,
        source_agent_id: str,
        target_agent_id: str,
    ) -> ProtocolAgentConfig:
        """
        Clone configuration from one agent to another.

        Args:
            source_agent_id: Source agent identifier
            target_agent_id: Target agent identifier

        Returns:
            Cloned agent configuration

        Raises:
            ConfigurationError: If cloning fails
            SourceNotFoundError: If source configuration doesn't exist
        """
        ...

    async def validate_security_policies(
        self, config: ProtocolAgentConfig
    ) -> list[str]:
        """
        Validate configuration against security policies.

        Args:
            config: Agent configuration to validate

        Returns:
            List of security policy violations
        """
        ...

    async def encrypt_sensitive_fields(
        self,
        config: ProtocolAgentConfig,
    ) -> ProtocolAgentConfig:
        """
        Encrypt sensitive fields in agent configuration.

        Args:
            config: Agent configuration to encrypt

        Returns:
            Configuration with encrypted sensitive fields

        Raises:
            EncryptionError: If encryption fails
        """
        ...

    async def decrypt_sensitive_fields(
        self,
        config: ProtocolAgentConfig,
    ) -> ProtocolAgentConfig:
        """
        Decrypt sensitive fields in agent configuration.

        Args:
            config: Agent configuration to decrypt

        Returns:
            Configuration with decrypted sensitive fields

        Raises:
            DecryptionError: If decryption fails
        """
        ...

    async def set_configuration_defaults(
        self,
        config: ProtocolAgentConfig,
    ) -> ProtocolAgentConfig:
        """
        Apply default values to agent configuration.

        Args:
            config: Agent configuration to apply defaults to

        Returns:
            Configuration with defaults applied
        """
        ...

    async def merge_configurations(
        self,
        base_config: ProtocolAgentConfig,
        override_config: ProtocolAgentConfig,
    ) -> ProtocolAgentConfig:
        """
        Merge two configurations with override taking precedence.

        Args:
            base_config: Base agent configuration
            override_config: Configuration with override values

        Returns:
            Merged agent configuration
        """
        ...

    async def export_configuration(
        self,
        agent_id: str,
        format_type: str | None = None,
    ) -> str:
        """
        Export agent configuration to specified format.

        Args:
            agent_id: Agent identifier
            format_type: Export format (yaml, json, toml)

        Returns:
            Serialized configuration in specified format

        Raises:
            ConfigurationError: If export fails
            UnsupportedFormatError: If format is not supported
        """
        ...

    async def import_configuration(
        self,
        agent_id: str,
        config_data: str,
        format_type: str | None = None,
    ) -> ProtocolAgentConfig:
        """
        Import agent configuration from serialized data.

        Args:
            agent_id: Agent identifier
            config_data: Serialized configuration data
            format_type: Import format (yaml, json, toml)

        Returns:
            Imported and validated agent configuration

        Raises:
            ConfigurationError: If import fails
            ValidationError: If imported configuration is invalid
            UnsupportedFormatError: If format is not supported
        """
        ...
