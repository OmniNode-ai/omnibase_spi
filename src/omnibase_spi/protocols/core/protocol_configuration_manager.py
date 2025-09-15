# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-15T19:30:00.000000'
# description: Protocol definition for configuration management and runtime reconfiguration
# entrypoint: python://protocol_configuration_manager
# hash: auto-generated
# last_modified_at: '2025-01-15T19:30:00.000000+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: protocol_configuration_manager.py
# namespace: python://omnibase_spi.protocols.core.protocol_configuration_manager
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: auto-generated
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Protocol definition for configuration management and runtime reconfiguration.

This protocol defines the interface for configuration managers that handle
loading, validation, merging, and runtime updates of configuration data
across multiple sources following ONEX infrastructure standards.
"""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from omnibase_core.enums.enum_environment import EnumEnvironment


@runtime_checkable
class ProtocolConfigurationManager(Protocol):
    """
    Protocol for configuration management implementations.

    Configuration managers provide centralized configuration loading, validation,
    merging from multiple sources, and runtime reconfiguration capabilities for
    ONEX infrastructure components.

    Example:
        class MyConfigurationManager:
            def load_configuration(self, config_name: str) -> dict[str, Any]:
                # Load from multiple sources and merge
                return self._merge_configuration_sources(config_name)

            def validate_configuration(self, config_data: dict[str, Any]) -> bool:
                # Validate against schema and constraints
                return self._apply_validation_rules(config_data)

            async def update_configuration_runtime(
                self, config_name: str, updates: dict[str, Any]
            ) -> bool:
                # Apply runtime configuration updates
                return await self._apply_runtime_updates(config_name, updates)
    """

    def load_configuration(
        self,
        config_name: str,
        *,
        environment: EnumEnvironment | None = None,
        force_reload: bool = False,
    ) -> dict[str, Any]:
        """
        Load configuration from all configured sources.

        Args:
            config_name: Unique identifier for the configuration set
            environment: Target environment (uses default if not specified)
            force_reload: Whether to force reload even if cached

        Returns:
            dict: Merged configuration data from all sources

        Raises:
            ValueError: If configuration name is invalid
            RuntimeError: If required configuration sources are unavailable
        """
        ...

    def validate_configuration(
        self,
        config_data: dict[str, Any],
        *,
        config_name: str | None = None,
        environment: EnumEnvironment | None = None,
        strict: bool = True,
    ) -> bool:
        """
        Validate configuration data against defined rules and schemas.

        Args:
            config_data: Configuration data to validate
            config_name: Configuration name for context (optional)
            environment: Target environment for validation
            strict: Whether to enforce strict validation rules

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration data is invalid
        """
        ...

    def get_configuration_value(
        self,
        config_name: str,
        key: str,
        *,
        default: Any = None,
        environment: EnumEnvironment | None = None,
    ) -> Any:
        """
        Get a specific configuration value by key.

        Args:
            config_name: Configuration set identifier
            key: Configuration key to retrieve
            default: Default value if key not found
            environment: Target environment

        Returns:
            Configuration value or default if not found
        """
        ...

    def set_configuration_value(
        self,
        config_name: str,
        key: str,
        value: Any,
        *,
        validate: bool = True,
        persist: bool = False,
    ) -> bool:
        """
        Set a configuration value at runtime.

        Args:
            config_name: Configuration set identifier
            key: Configuration key to set
            value: New configuration value
            validate: Whether to validate the new value
            persist: Whether to persist the change

        Returns:
            bool: True if value was successfully set

        Raises:
            ValueError: If value is invalid or runtime updates not allowed
        """
        ...

    async def update_configuration_runtime(
        self,
        config_name: str,
        updates: dict[str, Any],
        *,
        validate: bool = True,
        backup: bool = True,
    ) -> bool:
        """
        Update multiple configuration values at runtime.

        Args:
            config_name: Configuration set identifier
            updates: Dictionary of key-value pairs to update
            validate: Whether to validate all updates before applying
            backup: Whether to create a backup before updating

        Returns:
            bool: True if all updates were successfully applied

        Raises:
            ValueError: If updates are invalid or runtime updates not allowed
        """
        ...

    def reload_configuration(
        self,
        config_name: str,
        *,
        source_type: str | None = None,
    ) -> bool:
        """
        Reload configuration from sources.

        Args:
            config_name: Configuration set identifier
            source_type: Specific source type to reload (None for all sources)

        Returns:
            bool: True if configuration was successfully reloaded
        """
        ...

    def backup_configuration(
        self,
        config_name: str,
        *,
        version_label: str | None = None,
    ) -> Path | None:
        """
        Create a backup of current configuration.

        Args:
            config_name: Configuration set identifier
            version_label: Optional label for the backup version

        Returns:
            Path to backup file or None if backup failed
        """
        ...

    def restore_configuration(
        self,
        config_name: str,
        backup_path: Path | str,
        *,
        validate: bool = True,
    ) -> bool:
        """
        Restore configuration from a backup.

        Args:
            config_name: Configuration set identifier
            backup_path: Path to backup file
            validate: Whether to validate restored configuration

        Returns:
            bool: True if configuration was successfully restored

        Raises:
            ValueError: If backup file is invalid or validation fails
        """
        ...

    def get_configuration_sources(self, config_name: str) -> list[dict[str, Any]]:
        """
        Get information about configuration sources for a given configuration.

        Args:
            config_name: Configuration set identifier

        Returns:
            list: Configuration source information including type, path, priority
        """
        ...

    def add_configuration_source(
        self,
        config_name: str,
        source_type: str,
        source_path: str | None = None,
        *,
        priority: int,
        required: bool = False,
        watch_for_changes: bool = False,
    ) -> bool:
        """
        Add a new configuration source.

        Args:
            config_name: Configuration set identifier
            source_type: Type of configuration source
            source_path: Path or identifier for the source
            priority: Priority for merging (lower = higher priority)
            required: Whether this source is required
            watch_for_changes: Whether to monitor for changes

        Returns:
            bool: True if source was successfully added

        Raises:
            ValueError: If source configuration is invalid
        """
        ...

    def remove_configuration_source(
        self,
        config_name: str,
        source_type: str,
        source_path: str | None = None,
    ) -> bool:
        """
        Remove a configuration source.

        Args:
            config_name: Configuration set identifier
            source_type: Type of configuration source to remove
            source_path: Path of source to remove (None matches any path)

        Returns:
            bool: True if source was successfully removed
        """
        ...

    def is_configuration_valid(
        self,
        config_name: str,
        *,
        environment: EnumEnvironment | None = None,
    ) -> bool:
        """
        Check if current configuration is valid.

        Args:
            config_name: Configuration set identifier
            environment: Target environment for validation

        Returns:
            bool: True if configuration is valid
        """
        ...

    def get_configuration_health(self, config_name: str) -> dict[str, Any]:
        """
        Get health status of configuration and its sources.

        Args:
            config_name: Configuration set identifier

        Returns:
            dict: Health status including source availability, validation status
        """
        ...

    def list_configurations(self) -> list[str]:
        """
        List all managed configuration names.

        Returns:
            list: Names of all managed configurations
        """
        ...

    def get_sensitive_keys(self, config_name: str) -> list[str]:
        """
        Get list of configuration keys marked as sensitive.

        Args:
            config_name: Configuration set identifier

        Returns:
            list: Configuration keys that contain sensitive data
        """
        ...

    def mask_sensitive_values(
        self,
        config_data: dict[str, Any],
        config_name: str,
    ) -> dict[str, Any]:
        """
        Mask sensitive values in configuration data for logging.

        Args:
            config_data: Configuration data to mask
            config_name: Configuration name for sensitive key lookup

        Returns:
            dict: Configuration data with sensitive values masked
        """
        ...


@runtime_checkable
class ProtocolConfigurationManagerFactory(Protocol):
    """
    Protocol for configuration manager factory implementations.

    Factories create and configure configuration managers with different
    validation levels, source types, and runtime capabilities.
    """

    def create_default(self) -> ProtocolConfigurationManager:
        """
        Create a default configuration manager with standard settings.

        Returns:
            ProtocolConfigurationManager: Default manager instance
        """
        ...

    def create_strict(self) -> ProtocolConfigurationManager:
        """
        Create a strict configuration manager with comprehensive validation.

        Returns:
            ProtocolConfigurationManager: Strict manager instance
        """
        ...

    def create_runtime_enabled(self) -> ProtocolConfigurationManager:
        """
        Create a configuration manager with runtime update capabilities.

        Returns:
            ProtocolConfigurationManager: Runtime-enabled manager instance
        """
        ...

    def create_custom(
        self,
        *,
        default_environment: EnumEnvironment = EnumEnvironment.DEVELOPMENT,
        allow_runtime_updates: bool = False,
        strict_validation: bool = True,
        auto_reload_on_change: bool = False,
        backup_enabled: bool = True,
        encryption_enabled: bool = True,
        source_types: list[str] | None = None,
    ) -> ProtocolConfigurationManager:
        """
        Create a custom configuration manager with specified settings.

        Args:
            default_environment: Default target environment
            allow_runtime_updates: Whether to allow runtime configuration updates
            strict_validation: Whether to enforce strict validation
            auto_reload_on_change: Whether to auto-reload on source changes
            backup_enabled: Whether to enable configuration backups
            encryption_enabled: Whether to encrypt sensitive values
            source_types: Supported configuration source types

        Returns:
            ProtocolConfigurationManager: Custom configured manager instance
        """
        ...
