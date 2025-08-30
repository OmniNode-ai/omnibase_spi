"""
Specialized Protocol Validators for ONEX SPI.

This module provides specialized validators for key ONEX protocols. These validators
extend the basic protocol validation with domain-specific checks and validation
logic tailored to each protocol's requirements.

Key Features:
- Protocol-specific validation logic
- Domain-aware error messages and guidance
- Integration with core protocol validator
- Business rule validation beyond type checking
- Clear development guidance for protocol implementations
"""

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from typing_extensions import Protocol
else:
    try:
        from typing import Protocol
    except ImportError:
        pass

from omnibase.protocols.container.protocol_artifact_container import (
    ProtocolArtifactContainer,
)
from omnibase.protocols.core.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocols.discovery.protocol_handler_discovery import (
    ProtocolHandlerDiscovery,
)

from .protocol_validator import ProtocolValidator, ValidationError, ValidationResult


class ArtifactContainerValidator(ProtocolValidator):
    """
    Specialized validator for ProtocolArtifactContainer implementations.

    This validator provides domain-specific validation for artifact containers,
    including business rule validation, data consistency checks, and usage pattern
    validation beyond basic protocol compliance.
    """

    def validate_implementation(
        self, implementation: Any, protocol: Any = None
    ) -> ValidationResult:
        """
        Validate artifact container implementation with domain-specific checks.

        Args:
            implementation: Artifact container implementation to validate
            protocol: Protocol to validate against (defaults to ProtocolArtifactContainer)

        Returns:
            ValidationResult with artifact container specific validation
        """
        if protocol is None:
            protocol = ProtocolArtifactContainer

        # Perform basic protocol validation
        result = super().validate_implementation(implementation, protocol)

        # Add artifact container specific validations
        self._validate_artifact_container_business_rules(implementation, result)

        return result

    def _validate_artifact_container_business_rules(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate artifact container business rules and data consistency."""

        # Test basic functionality if methods are available
        if hasattr(implementation, "get_status"):
            try:
                status = implementation.get_status()
                self._validate_container_status(status, result)
            except Exception as e:
                result.add_error(
                    ValidationError(
                        "status_method_error",
                        f"get_status() method failed: {str(e)}",
                        {"error": str(e)},
                    )
                )

        if hasattr(implementation, "get_artifacts") and hasattr(
            implementation, "get_status"
        ):
            try:
                artifacts = implementation.get_artifacts()
                status = implementation.get_status()
                self._validate_artifact_consistency(artifacts, status, result)
            except Exception as e:
                result.add_error(
                    ValidationError(
                        "artifact_consistency_error",
                        f"Artifact consistency check failed: {str(e)}",
                        {"error": str(e)},
                    )
                )

        # Validate artifact type filtering if method exists
        if hasattr(implementation, "get_artifacts_by_type"):
            self._validate_artifact_type_filtering(implementation, result)

    def _validate_container_status(self, status: Any, result: ValidationResult) -> None:
        """Validate artifact container status object."""
        required_attrs = [
            "status",
            "message",
            "artifact_count",
            "valid_artifact_count",
            "invalid_artifact_count",
            "wip_artifact_count",
            "artifact_types_found",
        ]

        for attr in required_attrs:
            if not hasattr(status, attr):
                result.add_error(
                    ValidationError(
                        "missing_status_attribute",
                        f"Container status missing required attribute '{attr}'",
                        {"attribute": attr},
                    )
                )

        # Validate status consistency
        if (
            hasattr(status, "artifact_count")
            and hasattr(status, "valid_artifact_count")
            and hasattr(status, "invalid_artifact_count")
        ):
            try:
                total = status.valid_artifact_count + status.invalid_artifact_count
                if hasattr(status, "wip_artifact_count"):
                    total += status.wip_artifact_count

                if status.artifact_count != total:
                    result.add_warning(
                        ValidationError(
                            "status_count_inconsistency",
                            f"Total artifact count ({status.artifact_count}) doesn't match sum of valid ({status.valid_artifact_count}) + invalid ({status.invalid_artifact_count}) + wip ({getattr(status, 'wip_artifact_count', 0)})",
                            {"total": status.artifact_count, "calculated": total},
                            severity="warning",
                        )
                    )
            except (AttributeError, TypeError) as e:
                result.add_warning(
                    ValidationError(
                        "status_count_validation_error",
                        f"Could not validate status count consistency: {str(e)}",
                        {"error": str(e)},
                        severity="warning",
                    )
                )

    def _validate_artifact_consistency(
        self, artifacts: List[Any], status: Any, result: ValidationResult
    ) -> None:
        """Validate consistency between artifacts list and status."""
        try:
            actual_count = len(artifacts) if artifacts else 0

            if (
                hasattr(status, "artifact_count")
                and status.artifact_count != actual_count
            ):
                result.add_warning(
                    ValidationError(
                        "artifact_count_mismatch",
                        f"Status reports {status.artifact_count} artifacts but get_artifacts() returns {actual_count}",
                        {
                            "status_count": status.artifact_count,
                            "actual_count": actual_count,
                        },
                        severity="warning",
                    )
                )

            # Validate artifact types consistency
            if hasattr(status, "artifact_types_found") and artifacts:
                artifact_types_in_list = set()
                for artifact in artifacts:
                    if hasattr(artifact, "artifact_type"):
                        artifact_types_in_list.add(artifact.artifact_type)

                status_types = set(status.artifact_types_found)
                if artifact_types_in_list != status_types:
                    result.add_warning(
                        ValidationError(
                            "artifact_types_mismatch",
                            f"Artifact types in status ({status_types}) don't match types in artifacts list ({artifact_types_in_list})",
                            {
                                "status_types": list(status_types),
                                "actual_types": list(artifact_types_in_list),
                            },
                            severity="warning",
                        )
                    )

        except Exception as e:
            result.add_warning(
                ValidationError(
                    "artifact_consistency_validation_error",
                    f"Could not validate artifact consistency: {str(e)}",
                    {"error": str(e)},
                    severity="warning",
                )
            )

    def _validate_artifact_type_filtering(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate artifact type filtering functionality."""
        try:
            # Test with a known artifact type
            artifact_types = [
                "nodes",
                "cli_tools",
                "runtimes",
                "adapters",
                "contracts",
                "packages",
            ]

            for artifact_type in artifact_types[:2]:  # Test first two types only
                try:
                    filtered_artifacts = implementation.get_artifacts_by_type(
                        artifact_type
                    )

                    # Verify all returned artifacts have the correct type
                    for artifact in filtered_artifacts:
                        if (
                            hasattr(artifact, "artifact_type")
                            and artifact.artifact_type != artifact_type
                        ):
                            result.add_error(
                                ValidationError(
                                    "artifact_type_filter_error",
                                    f"get_artifacts_by_type('{artifact_type}') returned artifact with type '{artifact.artifact_type}'",
                                    {
                                        "requested_type": artifact_type,
                                        "actual_type": artifact.artifact_type,
                                    },
                                )
                            )

                except Exception as e:
                    result.add_warning(
                        ValidationError(
                            "artifact_type_filter_test_error",
                            f"Could not test artifact type filtering for '{artifact_type}': {str(e)}",
                            {"artifact_type": artifact_type, "error": str(e)},
                            severity="warning",
                        )
                    )

        except Exception as e:
            result.add_warning(
                ValidationError(
                    "artifact_type_filtering_validation_error",
                    f"Could not validate artifact type filtering: {str(e)}",
                    {"error": str(e)},
                    severity="warning",
                )
            )


class NodeRegistryValidator(ProtocolValidator):
    """
    Specialized validator for ProtocolNodeRegistry implementations.

    This validator provides domain-specific validation for node registries,
    including validation of node information, discovery patterns, and
    registry consistency checks.
    """

    def validate_implementation(
        self, implementation: Any, protocol: Any = None
    ) -> ValidationResult:
        """
        Validate node registry implementation with domain-specific checks.

        Args:
            implementation: Node registry implementation to validate
            protocol: Protocol to validate against (defaults to ProtocolNodeRegistry)

        Returns:
            ValidationResult with node registry specific validation
        """
        if protocol is None:
            protocol = ProtocolNodeRegistry

        # Perform basic protocol validation
        result = super().validate_implementation(implementation, protocol)

        # Add node registry specific validations
        self._validate_node_registry_business_rules(implementation, result)

        return result

    def _validate_node_registry_business_rules(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate node registry business rules and functionality."""

        # Check if registry has proper initialization
        if hasattr(implementation, "__init__"):
            self._validate_registry_initialization(implementation, result)

        # Validate async method signatures
        self._validate_async_methods(implementation, result)

        # Test basic discovery functionality if available
        if hasattr(implementation, "discover_nodes"):
            self._validate_discovery_functionality(implementation, result)

    def _validate_registry_initialization(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate registry initialization parameters."""
        init_method = getattr(implementation.__class__, "__init__", None)
        if init_method:
            import inspect

            try:
                sig = inspect.signature(init_method)
                params = list(sig.parameters.keys())

                expected_params = ["self", "environment", "consul_endpoint", "config"]
                for param in expected_params[1:]:  # Skip 'self'
                    if param not in params:
                        result.add_warning(
                            ValidationError(
                                "missing_init_parameter",
                                f"Registry initialization missing expected parameter '{param}'",
                                {"parameter": param},
                                severity="warning",
                            )
                        )

            except Exception as e:
                result.add_warning(
                    ValidationError(
                        "init_validation_error",
                        f"Could not validate initialization parameters: {str(e)}",
                        {"error": str(e)},
                        severity="warning",
                    )
                )

    def _validate_async_methods(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate that registry methods are properly async."""
        async_methods = [
            "register_node",
            "unregister_node",
            "update_node_health",
            "heartbeat",
            "discover_nodes",
            "get_node",
            "get_nodes_by_group",
            "get_gateway_for_group",
            "watch_node_changes",
            "stop_watch",
        ]

        import inspect

        for method_name in async_methods:
            if hasattr(implementation, method_name):
                method = getattr(implementation, method_name)
                if not inspect.iscoroutinefunction(method):
                    result.add_warning(
                        ValidationError(
                            "non_async_method",
                            f"Method '{method_name}' should be async but is not",
                            {"method": method_name},
                            severity="warning",
                        )
                    )

    def _validate_discovery_functionality(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate node discovery functionality."""
        # This is a basic structural validation - actual functionality testing
        # would require a running registry backend

        import inspect

        if hasattr(implementation, "discover_nodes"):
            try:
                method = getattr(implementation, "discover_nodes")
                sig = inspect.signature(method)

                expected_params = ["node_type", "environment", "group", "health_filter"]
                for param in expected_params:
                    if param not in sig.parameters:
                        result.add_warning(
                            ValidationError(
                                "missing_discovery_parameter",
                                f"discover_nodes method missing expected parameter '{param}'",
                                {"parameter": param},
                                severity="warning",
                            )
                        )

            except Exception as e:
                result.add_warning(
                    ValidationError(
                        "discovery_validation_error",
                        f"Could not validate discovery functionality: {str(e)}",
                        {"error": str(e)},
                        severity="warning",
                    )
                )


class HandlerDiscoveryValidator(ProtocolValidator):
    """
    Specialized validator for ProtocolHandlerDiscovery implementations.

    This validator provides domain-specific validation for handler discovery
    implementations, including validation of discovery sources, handler info
    objects, and discovery consistency.
    """

    def validate_implementation(
        self, implementation: Any, protocol: Any = None
    ) -> ValidationResult:
        """
        Validate handler discovery implementation with domain-specific checks.

        Args:
            implementation: Handler discovery implementation to validate
            protocol: Protocol to validate against (defaults to ProtocolHandlerDiscovery)

        Returns:
            ValidationResult with handler discovery specific validation
        """
        if protocol is None:
            protocol = ProtocolHandlerDiscovery

        # Perform basic protocol validation
        result = super().validate_implementation(implementation, protocol)

        # Add handler discovery specific validations
        self._validate_handler_discovery_business_rules(implementation, result)

        return result

    def _validate_handler_discovery_business_rules(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate handler discovery business rules."""

        # Test discovery functionality
        if hasattr(implementation, "discover_nodes"):
            try:
                discovered = implementation.discover_nodes()
                self._validate_discovered_handlers(discovered, result)
            except Exception as e:
                result.add_warning(
                    ValidationError(
                        "discovery_execution_error",
                        f"discover_nodes() method failed during validation: {str(e)}",
                        {"error": str(e)},
                        severity="warning",
                    )
                )

        # Validate source name functionality
        if hasattr(implementation, "get_source_name"):
            try:
                source_name = implementation.get_source_name()
                if not isinstance(source_name, str) or not source_name.strip():
                    result.add_error(
                        ValidationError(
                            "invalid_source_name",
                            "get_source_name() must return a non-empty string",
                            {"returned_value": str(source_name)},
                        )
                    )
            except Exception as e:
                result.add_error(
                    ValidationError(
                        "source_name_error",
                        f"get_source_name() method failed: {str(e)}",
                        {"error": str(e)},
                    )
                )

    def _validate_discovered_handlers(
        self, handlers: List[Any], result: ValidationResult
    ) -> None:
        """Validate discovered handler info objects."""
        if not isinstance(handlers, list):
            result.add_error(
                ValidationError(
                    "invalid_discovery_return_type",
                    f"discover_nodes() must return a list, got {type(handlers).__name__}",
                    {"returned_type": type(handlers).__name__},
                )
            )
            return

        for i, handler_info in enumerate(handlers):
            self._validate_handler_info(handler_info, i, result)

    def _validate_handler_info(
        self, handler_info: Any, index: int, result: ValidationResult
    ) -> None:
        """Validate individual handler info object."""
        required_attrs = [
            "node_class",
            "name",
            "source",
            "priority",
            "extensions",
            "special_files",
            "metadata",
        ]

        for attr in required_attrs:
            if not hasattr(handler_info, attr):
                result.add_error(
                    ValidationError(
                        "missing_handler_info_attribute",
                        f"Handler info at index {index} missing required attribute '{attr}'",
                        {"index": index, "attribute": attr},
                    )
                )

        # Validate specific attribute types
        if hasattr(handler_info, "priority"):
            try:
                priority = handler_info.priority
                if not isinstance(priority, int):
                    result.add_warning(
                        ValidationError(
                            "invalid_priority_type",
                            f"Handler info at index {index} has non-integer priority: {type(priority).__name__}",
                            {"index": index, "priority_type": type(priority).__name__},
                            severity="warning",
                        )
                    )
            except Exception:
                pass

        if hasattr(handler_info, "extensions"):
            try:
                extensions = handler_info.extensions
                if not isinstance(extensions, list):
                    result.add_warning(
                        ValidationError(
                            "invalid_extensions_type",
                            f"Handler info at index {index} has non-list extensions: {type(extensions).__name__}",
                            {
                                "index": index,
                                "extensions_type": type(extensions).__name__,
                            },
                            severity="warning",
                        )
                    )
            except Exception:
                pass


class ServiceRegistryValidator(ProtocolValidator):
    """
    Generic service registry validator for protocol implementations that
    follow registry patterns but may not have specific protocols defined yet.

    This validator provides common validation patterns for registry-like
    implementations and can be extended for specific registry types.
    """

    def validate_implementation(
        self, implementation: Any, protocol: Any = None
    ) -> ValidationResult:
        """
        Validate service registry implementation.

        Args:
            implementation: Registry implementation to validate
            protocol: Protocol to validate against (optional)

        Returns:
            ValidationResult with service registry validation
        """
        if protocol:
            # Perform basic protocol validation if protocol provided
            result = super().validate_implementation(implementation, protocol)
        else:
            # Create a basic validation result for generic registry validation
            impl_name = (
                implementation.__class__.__name__
                if hasattr(implementation, "__class__")
                else str(type(implementation))
            )
            result = ValidationResult("generic_registry", impl_name)

        # Add generic registry validations
        self._validate_generic_registry_patterns(implementation, result)

        return result

    def _validate_generic_registry_patterns(
        self, implementation: Any, result: ValidationResult
    ) -> None:
        """Validate common registry patterns."""

        # Check for common registry methods
        common_registry_methods = [
            "register",
            "unregister",
            "get",
            "list",
            "find",
            "discover",
            "lookup",
            "resolve",
        ]

        found_methods = []
        for method_name in common_registry_methods:
            if hasattr(implementation, method_name):
                found_methods.append(method_name)

        if not found_methods:
            result.add_warning(
                ValidationError(
                    "no_registry_methods",
                    f"Implementation does not have any common registry methods ({', '.join(common_registry_methods)})",
                    {"implementation": result.implementation_name},
                    severity="warning",
                )
            )

        # Validate registry has some form of storage or backend
        storage_indicators = [
            "_registry",
            "_storage",
            "_cache",
            "_backend",
            "_data",
            "registry",
            "storage",
            "cache",
            "backend",
            "data",
        ]

        has_storage = any(hasattr(implementation, attr) for attr in storage_indicators)
        if not has_storage:
            result.add_warning(
                ValidationError(
                    "no_storage_backend",
                    "Registry implementation does not appear to have a storage backend",
                    {"checked_attributes": storage_indicators},
                    severity="warning",
                )
            )
