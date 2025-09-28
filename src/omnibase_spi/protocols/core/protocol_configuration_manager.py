"""
Protocol definition for configuration management and runtime reconfiguration.

This protocol defines the interface for configuration managers that handle
loading, validation, merging, and runtime updates of configuration data
across multiple sources following ONEX infrastructure standards.
"""

from typing import Any, Literal, Protocol, runtime_checkable

LiteralConfigurationEnvironment = Literal[
    "development", "staging", "production", "test"
]


@runtime_checkable
class ProtocolConfigurationManager(Protocol):
    """
    Protocol for configuration management implementations.

    Configuration managers provide centralized configuration loading, validation,
    merging from multiple sources, and runtime reconfiguration capabilities for
    ONEX infrastructure components.

    Example:
        class MyConfigurationManager:
            async def load_configuration(self, config_name: str) -> dict[str, Any]:
                # Load from multiple sources and merge
                return self._merge_configuration_sources(config_name)

            async def validate_configuration(self, config_data: dict[str, Any]) -> bool:
                # Validate against schema and constraints
                return self._apply_validation_rules(config_data)

            async def update_configuration_runtime(
                self, config_name: str, updates: dict[str, Any]
            ) -> bool:
                # Apply runtime configuration updates
                return await self._apply_runtime_updates(config_name, updates)
    """

    async def load_configuration(
        self,
        config_name: str,
        *,
        environment: "LiteralConfigurationEnvironment | None" = None,
        force_reload: bool = False,
    ) -> dict[str, Any]: ...

    async def validate_configuration(
        self,
        config_data: dict[str, Any],
        *,
        config_name: str | None = None,
        environment: "LiteralConfigurationEnvironment | None" = None,
        strict: bool = True,
    ) -> bool: ...

    async def get_configuration_value(
        self,
        config_name: str,
        key: str,
        default: object | None = None,
        environment: str | None = None,
    ) -> object: ...

    async def set_configuration_value(
        self,
        config_name: str,
        key: str,
        value: object,
        *,
        validate: bool = True,
        persist: bool = False,
    ) -> bool: ...

    async def update_configuration_runtime(
        self,
        config_name: str,
        updates: dict[str, Any],
        *,
        validate: bool = True,
        backup: bool = True,
    ) -> bool: ...

    async def reload_configuration(
        self, config_name: str, *, source_type: str | None = None
    ) -> bool: ...

    async def backup_configuration(
        self, config_name: str, *, version_label: str | None = None
    ) -> str | None: ...

    async def restore_configuration(
        self, config_name: str, backup_path: str, *, validate: bool = True
    ) -> bool: ...

    async def get_configuration_sources(
        self, config_name: str
    ) -> list[dict[str, Any]]: ...

    def add_configuration_source(
        self,
        config_name: str,
        source_type: str,
        source_path: str | None = None,
        *,
        priority: int,
        required: bool = False,
        watch_for_changes: bool = False,
    ) -> bool: ...

    def remove_configuration_source(
        self, config_name: str, source_type: str, source_path: str | None = None
    ) -> bool: ...

    def is_configuration_valid(
        self,
        config_name: str,
        *,
        environment: "LiteralConfigurationEnvironment | None" = None,
    ) -> bool: ...

    async def get_configuration_health(self, config_name: str) -> dict[str, Any]: ...

    def list_configurations(self) -> list[str]: ...

    async def get_sensitive_keys(self, config_name: str) -> list[str]: ...

    def mask_sensitive_values(
        self, config_data: dict[str, object], config_name: str
    ) -> dict[str, object]: ...


@runtime_checkable
class ProtocolConfigurationManagerFactory(Protocol):
    """
    Protocol for configuration manager factory implementations.

    Factories create and configure configuration managers with different
    validation levels, source types, and runtime capabilities.
    """

    async def create_default(self) -> ProtocolConfigurationManager: ...
