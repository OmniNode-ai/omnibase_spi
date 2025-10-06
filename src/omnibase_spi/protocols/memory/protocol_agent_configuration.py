"""
Protocol for Agent Configuration Management.

This protocol defines the interface for managing Claude Code agent configurations,
including validation, persistence, versioning, and security.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward references for configuration and validation types
    class ModelValidationResult:
        """Protocol for validation results."""

        is_valid: bool
        errors: list[str]
        warnings: list[str]

    class ModelAgentConfig:
        """Protocol for agent configuration."""

        agent_id: str
        agent_type: str
        configuration: dict[str, Any]
        security_context: dict[str, Any]


@runtime_checkable
class ProtocolAgentConfigurationLegacy(Protocol):
    """Legacy protocol for Claude Code agent configuration management.

    This protocol provides basic configuration management capabilities.
    For new implementations, use ProtocolAgentConfiguration from protocol_agent_config_interfaces.py
    which provides more comprehensive functionality including template management and security features.
    """

    async def validate_configuration(
        self,
        config: "ModelAgentConfig",
    ) -> "ModelValidationResult":
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

    async def save_configuration(self, config: "ModelAgentConfig") -> bool:
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

    async def load_configuration(self, agent_id: str) -> "ModelAgentConfig" | None:
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
        updates: dict[str, Any],
    ) -> "ModelAgentConfig":
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
        base_config: "ModelAgentConfig",
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
        overrides: dict[str, Any] | None = None,
    ) -> "ModelAgentConfig":
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

    async def get_configuration_history(self, agent_id: str) -> list[dict[str, Any]]:
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
    ) -> "ModelAgentConfig":
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

    async def validate_security_policies(self, config: "ModelAgentConfig") -> list[str]:
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
        config: "ModelAgentConfig",
    ) -> "ModelAgentConfig":
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
        config: "ModelAgentConfig",
    ) -> "ModelAgentConfig":
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
        config: "ModelAgentConfig",
    ) -> "ModelAgentConfig":
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
        base_config: "ModelAgentConfig",
        override_config: "ModelAgentConfig",
    ) -> "ModelAgentConfig":
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
        format_type: str = "yaml",
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
        format_type: str = "yaml",
    ) -> "ModelAgentConfig":
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
