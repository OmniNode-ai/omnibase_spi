"""
ONEX Workflow Testing Protocol Interfaces

This module defines protocol interfaces for the ONEX workflow testing system,
ensuring consistent behavior across different implementations with strict SPI purity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


# Protocol-compatible literal types for testing strategies
LiteralAccommodationStrategy = str
LiteralTestContext = str


@runtime_checkable
class ProtocolWorkflowTestingExecutor(Protocol):
    """Protocol for workflow testing execution orchestration"""

    async def execute_workflow_testing(
        self,
        configuration: dict[str, ContextValue],
        test_context: LiteralTestContext = "LOCAL_DEVELOPMENT",
    ) -> dict[str, ContextValue]:
        """
        Execute complete workflow testing based on configuration.

        Args:
            configuration: Complete workflow testing configuration
            test_context: Context in which tests are being executed

        Returns:
            Comprehensive testing results with success metrics and detailed outputs
        """
        ...

    def validate_test_configuration(
        self,
        configuration: dict[str, ContextValue],
    ) -> list[str]:
        """
        Validate workflow testing configuration for completeness and correctness.

        Args:
            configuration: Testing configuration to validate

        Returns:
            List of validation errors (empty if valid)
        """
        ...

    async def get_supported_test_types(self) -> list[str]:
        """
        Get list of supported test types.

        Returns:
            List of supported test type identifiers
        """
        ...

    def health_check(self) -> dict[str, ContextValue]:
        """
        Perform health check for the workflow testing executor.

        Returns:
            Health check result with status and capabilities
        """
        ...


@runtime_checkable
class ProtocolMockEventBus(Protocol):
    """Protocol for mock event bus implementations in testing"""

    def configure_mock_event_bus(
        self,
        config: dict[str, ContextValue],
    ) -> bool:
        """
        Configure mock event bus for testing scenarios.

        Args:
            config: Mock event bus configuration

        Returns:
            True if configuration was successful
        """
        ...

    def simulate_event_sequence(
        self,
        events: list[dict[str, ContextValue]],
    ) -> bool:
        """
        Simulate a sequence of events for testing.

        Args:
            events: List of events to simulate

        Returns:
            True if simulation was successful
        """
        ...

    async def get_published_events(self) -> list[dict[str, ContextValue]]:
        """
        Get list of events published during testing.

        Returns:
            List of published events with metadata
        """
        ...


@runtime_checkable
class ProtocolMockRegistry(Protocol):
    """Protocol for mock service registry implementations in testing"""

    def configure_mock_registry(
        self,
        config: dict[str, ContextValue],
    ) -> bool:
        """
        Configure mock service registry for testing scenarios.

        Args:
            config: Mock registry configuration

        Returns:
            True if configuration was successful
        """
        ...

    def register_mock_service(
        self,
        service_name: str,
        service_config: dict[str, ContextValue],
    ) -> bool:
        """
        Register a mock service for testing.

        Args:
            service_name: Name of the mock service
            service_config: Configuration for the mock service

        Returns:
            True if registration was successful
        """
        ...

    async def get_mock_service(
        self,
        service_name: str,
    ) -> dict[str, ContextValue] | None:
        """
        Get mock service configuration.

        Args:
            service_name: Name of the mock service

        Returns:
            Mock service configuration or None if not found
        """
        ...


@runtime_checkable
class ProtocolAccommodationManager(Protocol):
    """
    Protocol for test dependency accommodation management.

    Manages test accommodation strategies for handling unavailable or
    complex dependencies during workflow testing. Provides mocking,
    stubbing, and override capabilities to enable testing in isolation
    without requiring full infrastructure availability.

    Example:
        ```python
        def setup_test_accommodations(
            manager: ProtocolAccommodationManager,
            dependencies: list[str]
        ) -> dict:
            # Define accommodation strategy
            strategy = "mock"  # or "stub", "real", "proxy"

            # Configure accommodations
            config = {
                "mock_mode": "simulated",
                "response_time": 100,
                "failure_rate": 0.0
            }

            # Apply strategy to dependencies
            results = manager.apply_accommodation_strategy(
                strategy=strategy,
                dependencies=dependencies,
                configuration=config
            )

            # Create specific overrides
            for dep in dependencies:
                override_config = {"mode": "mock", "data": "test_data"}
                manager.create_accommodation_override(dep, override_config)

            # Validate final configuration
            errors = manager.validate_accommodation(config)
            if errors:
                print(f"Validation errors: {errors}")

            return results
        ```

    Key Features:
        - **Strategy Application**: Mock, stub, proxy, or real dependencies
        - **Dependency Overrides**: Fine-grained per-dependency configuration
        - **Validation Support**: Configuration correctness checking
        - **Isolation Testing**: Test workflows without full infrastructure
        - **Flexible Accommodation**: Multiple accommodation strategies
        - **Configuration Management**: Centralized accommodation config

    See Also:
        - ProtocolMockEventBus: Mock event bus for testing
        - ProtocolMockRegistry: Mock service registry
        - ProtocolServiceAvailabilityManager: Service availability control
        - ProtocolWorkflowTestingExecutor: Test execution orchestration
    """

    def apply_accommodation_strategy(
        self,
        strategy: LiteralAccommodationStrategy,
        dependencies: list[str],
        configuration: dict[str, ContextValue],
    ) -> dict[str, ContextValue]:
        """
        Apply accommodation strategy for test dependencies.

        Args:
            strategy: Accommodation strategy to apply
            dependencies: List of dependencies to accommodate
            configuration: Accommodation configuration

        Returns:
            Accommodation results with applied strategies
        """
        ...

    def create_accommodation_override(
        self,
        dependency_name: str,
        override_config: dict[str, ContextValue],
    ) -> bool:
        """
        Create accommodation override for specific dependency.

        Args:
            dependency_name: Name of dependency to override
            override_config: Override configuration

        Returns:
            True if override was created successfully
        """
        ...

    def validate_accommodation(
        self,
        accommodation_config: dict[str, ContextValue],
    ) -> list[str]:
        """
        Validate accommodation configuration.

        Args:
            accommodation_config: Accommodation configuration to validate

        Returns:
            List of validation errors (empty if valid)
        """
        ...


@runtime_checkable
class ProtocolServiceAvailabilityManager(Protocol):
    """Protocol for service availability management in testing"""

    def configure_service_availability(
        self,
        availability_map: dict[str, ContextValue],
    ) -> bool:
        """
        Configure service availability for testing scenarios.

        Args:
            availability_map: Service availability configuration

        Returns:
            True if configuration was successful
        """
        ...

    def set_service_availability(
        self,
        service_name: str,
        available: bool,
        response_time: float | None = None,
    ) -> bool:
        """
        Set availability for a specific service.

        Args:
            service_name: Name of the service
            available: Whether the service is available
            response_time: Optional response time simulation

        Returns:
            True if availability was set successfully
        """
        ...

    async def get_service_status(
        self,
        service_name: str,
    ) -> dict[str, ContextValue]:
        """
        Get current status of a service.

        Args:
            service_name: Name of the service

        Returns:
            Service status information
        """
        ...


@runtime_checkable
class ProtocolWorkflowTestingOrchestrator(Protocol):
    """Protocol for complete workflow testing orchestration"""

    def setup_test_environment(
        self,
        test_configuration: dict[str, ContextValue],
    ) -> bool:
        """
        Set up complete test environment.

        Args:
            test_configuration: Complete test environment configuration

        Returns:
            True if environment setup was successful
        """
        ...

    async def execute_test_workflow(
        self,
        workflow_config: dict[str, ContextValue],
        test_context: LiteralTestContext,
    ) -> dict[str, ContextValue]:
        """
        Execute a specific test workflow.

        Args:
            workflow_config: Workflow configuration to test
            test_context: Context for test execution

        Returns:
            Test execution results
        """
        ...

    def cleanup_test_environment(self) -> bool:
        """
        Clean up test environment after execution.

        Returns:
            True if cleanup was successful
        """
        ...

    def generate_test_report(
        self,
        test_results: dict[str, ContextValue],
    ) -> dict[str, ContextValue]:
        """
        Generate comprehensive test report.

        Args:
            test_results: Test execution results

        Returns:
            Formatted test report
        """
        ...
