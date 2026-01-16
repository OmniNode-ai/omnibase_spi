"""Protocol for dashboard service abstraction.

This module defines the contract for dashboard services that manage
dashboard configuration, registration, and lifecycle within the
ONEX platform's user interface layer.

Architecture Context:
    Dashboard services provide the interface between the ONEX runtime
    and visualization/monitoring components:

    1. Dashboards register with the dashboard service on startup
    2. Configuration is retrieved to determine layout and data sources
    3. Dashboards can be dynamically registered/unregistered at runtime
    4. Service tracks registration state for discovery and health checks

Core Responsibilities:
    - Dashboard configuration management
    - Registration lifecycle (register/unregister)
    - Registration state tracking
    - Dashboard identity management

Usage Pattern:
    Dashboard services are typically injected via dependency injection
    into dashboard components that need to manage their lifecycle:

    ```
    Application         DashboardService        Registry
        |                    |                     |
        |-- get_config ----->|                     |
        |<-- config ---------|                     |
        |-- register ------->|                     |
        |                    |-- register -------->|
        |                    |<-- ack -------------|
        |<-- success --------|                     |
    ```

Related tickets:
    - OMN-1285: Implement dashboard protocols for omnibase_spi
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.dashboard import ModelDashboardConfig


@runtime_checkable
class ProtocolDashboardService(Protocol):
    """Interface for dashboard service operations.

    Defines the contract for services that manage dashboard
    configuration and lifecycle within the ONEX platform.
    Implementations handle the specifics of configuration
    storage, registration mechanisms, and state management.

    Dashboard services MUST:
        - Provide stable dashboard identifiers
        - Track registration state accurately
        - Return valid configuration on request
        - Handle registration/unregistration idempotently

    Dashboard services MUST NOT:
        - Persist configuration without explicit request
        - Allow duplicate registrations
        - Expose internal implementation details

    Example Usage:
        ```python
        class MetricsDashboardService:
            def __init__(self, config: ModelDashboardConfig) -> None:
                self._config = config
                self._dashboard_id = "metrics-dashboard-v1"
                self._is_registered = False

            @property
            def dashboard_id(self) -> str:
                return self._dashboard_id

            @property
            def is_registered(self) -> bool:
                return self._is_registered

            async def get_dashboard_config(self) -> ModelDashboardConfig:
                return self._config

            async def register_dashboard(self) -> None:
                if self._is_registered:
                    return  # Idempotent - already registered
                await self._registry.register(self._dashboard_id, self._config)
                self._is_registered = True

            async def unregister_dashboard(self) -> None:
                if not self._is_registered:
                    return  # Idempotent - not registered
                await self._registry.unregister(self._dashboard_id)
                self._is_registered = False


        # Usage in application code
        async def setup_dashboard(service: ProtocolDashboardService) -> None:
            config = await service.get_dashboard_config()
            print(f"Dashboard: {service.dashboard_id}")
            print(f"Title: {config.title}")

            await service.register_dashboard()
            assert service.is_registered
        ```

    Implementation Notes:
        - Concrete implementations live in omnibase_infra
        - Services are typically instantiated via factory functions
        - Registration state should be persisted across restarts
    """

    @property
    def dashboard_id(self) -> str:
        """Unique identifier for this dashboard.

        Used for:
            - Registration in dashboard registries
            - Routing and discovery
            - Logging and metrics identification
            - Deduplication of registrations

        The identifier should be stable across restarts and
        unique within the application context.

        Returns:
            A stable string identifier for this dashboard instance.
            Should follow the pattern: "{name}-v{version}" for
            versioned dashboards.

        Example:
            ```python
            @property
            def dashboard_id(self) -> str:
                return "metrics-dashboard-v1"
            ```
        """
        ...

    @property
    def is_registered(self) -> bool:
        """Whether this dashboard is currently registered.

        Indicates the current registration state of the dashboard
        with the underlying registry. Used for:
            - Health check status reporting
            - Conditional registration logic
            - State validation before operations

        Returns:
            True if the dashboard is currently registered,
            False otherwise.

        Example:
            ```python
            @property
            def is_registered(self) -> bool:
                return self._is_registered

            # Usage
            if not service.is_registered:
                await service.register_dashboard()
            ```
        """
        ...

    async def get_dashboard_config(self) -> ModelDashboardConfig:
        """Retrieve the dashboard configuration.

        Returns the complete configuration for this dashboard,
        including layout, data sources, refresh intervals, and
        any dashboard-specific settings.

        The configuration is typically loaded once at service
        initialization but may be refreshed dynamically in
        some implementations.

        Returns:
            ModelDashboardConfig containing the dashboard configuration
            with fields such as:
                - title: Display name for the dashboard
                - layout: Panel arrangement and sizing
                - data_sources: Data provider configurations
                - refresh_interval: Auto-refresh settings
                - permissions: Access control settings

            See ``omnibase_core.models.dashboard.ModelDashboardConfig``
            for the complete field specification.

        Raises:
            SPIError: If configuration is invalid or cannot be loaded.
                Implementations may raise a subclass such as a
                configuration-specific error.

        Example:
            ```python
            async def get_dashboard_config(self) -> ModelDashboardConfig:
                if self._cached_config is not None:
                    return self._cached_config

                config = await self._config_loader.load(self.dashboard_id)
                self._cached_config = config
                return config
            ```
        """
        ...

    async def register_dashboard(self) -> None:
        """Register the dashboard with the registry.

        Registers this dashboard instance with the underlying
        dashboard registry, making it discoverable and available
        for use within the platform.

        This method MUST be idempotent - calling it multiple times
        when already registered should have no effect and should
        not raise an error.

        After successful registration:
            - is_registered will return True
            - Dashboard will be discoverable via registry queries
            - Dashboard will receive lifecycle events

        Raises:
            RegistryError: If registration fails due to infrastructure
                issues (network, registry unavailable).
            SPIError: If the dashboard configuration is invalid for
                registration.

        Example:
            ```python
            async def register_dashboard(self) -> None:
                if self._is_registered:
                    return  # Idempotent

                config = await self.get_dashboard_config()
                await self._registry.register(
                    dashboard_id=self.dashboard_id,
                    config=config,
                )
                self._is_registered = True
                logger.info(f"Registered dashboard: {self.dashboard_id}")
            ```
        """
        ...

    async def unregister_dashboard(self) -> None:
        """Unregister the dashboard from the registry.

        Removes this dashboard instance from the underlying
        dashboard registry, making it no longer discoverable
        or available for use.

        This method MUST be idempotent - calling it multiple times
        when not registered should have no effect and should not
        raise an error.

        After successful unregistration:
            - is_registered will return False
            - Dashboard will no longer be discoverable
            - Dashboard will stop receiving lifecycle events

        Raises:
            RegistryError: If unregistration fails due to infrastructure
                issues (network, registry unavailable).

        Example:
            ```python
            async def unregister_dashboard(self) -> None:
                if not self._is_registered:
                    return  # Idempotent

                await self._registry.unregister(self.dashboard_id)
                self._is_registered = False
                logger.info(f"Unregistered dashboard: {self.dashboard_id}")
            ```
        """
        ...
