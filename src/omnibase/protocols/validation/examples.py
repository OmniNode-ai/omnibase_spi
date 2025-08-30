# type: ignore
"""
Usage Examples for ONEX SPI Protocol Validation.

This module provides comprehensive examples of how to use the protocol validation
utilities in the omnibase-spi project. These examples demonstrate both correct
and incorrect implementations to help developers understand validation patterns.

Examples Include:
- Basic protocol implementation validation
- Using validation decorators
- Specialized validator usage
- Common validation patterns
- Error handling and debugging
"""

from datetime import datetime
from typing import Dict, List, Optional

# Import protocols for examples
from omnibase.protocols.container.protocol_artifact_container import (
    ContainerArtifactType,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
    ProtocolArtifactMetadata,
)
from omnibase.protocols.core.protocol_node_registry import (
    ProtocolNodeInfo,
    ProtocolNodeRegistry,
)
from omnibase.protocols.discovery.protocol_handler_discovery import (
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
)
from omnibase.protocols.types.core_types import ProtocolSemVer

# Import validation utilities
from omnibase.protocols.validation import (
    ArtifactContainerValidator,
    HandlerDiscoveryValidator,
    NodeRegistryValidator,
    ProtocolValidator,
    ValidationResult,
    validate_protocol_implementation,
    validation_decorator,
)

# =============================================================================
# Example 1: Basic Protocol Implementation Validation
# =============================================================================


def example_basic_validation():
    """
    Example of basic protocol validation using validate_protocol_implementation.
    """
    print("=== Example 1: Basic Protocol Validation ===")

    # Example implementation (correct)
    class GoodArtifactContainer:
        def get_status(self) -> ProtocolArtifactContainerStatus:
            return self._create_mock_status()

        def get_artifacts(self) -> List[ProtocolArtifactInfo]:
            return []

        def get_artifacts_by_type(
            self, artifact_type: ContainerArtifactType
        ) -> List[ProtocolArtifactInfo]:
            return []

        def get_artifact_by_name(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> ProtocolArtifactInfo:
            raise NotImplementedError("Artifact not found")

        def has_artifact(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> bool:
            return False

        def _create_mock_status(self):
            class MockStatus:
                status = "ACTIVE"
                message = "Container is active"
                artifact_count = 0
                valid_artifact_count = 0
                invalid_artifact_count = 0
                wip_artifact_count = 0
                artifact_types_found = []

            return MockStatus()

    # Example implementation (incorrect - missing methods)
    class BadArtifactContainer:
        def get_status(self):
            return "active"  # Wrong return type

        # Missing required methods: get_artifacts, get_artifacts_by_type, etc.

    print("\n--- Validating Good Implementation ---")
    good_container = GoodArtifactContainer()
    result = validate_protocol_implementation(
        good_container,
        ProtocolArtifactContainer,
        strict_mode=True,
        print_results=False,  # We'll handle printing ourselves
    )

    print(f"Valid: {result.is_valid}")
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    print("\n--- Validating Bad Implementation ---")
    bad_container = BadArtifactContainer()
    result = validate_protocol_implementation(
        bad_container, ProtocolArtifactContainer, strict_mode=True, print_results=False
    )

    print(f"Valid: {result.is_valid}")
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")

    print()


# =============================================================================
# Example 2: Using Validation Decorators
# =============================================================================


def example_validation_decorators():
    """
    Example of using validation decorators for automatic validation.
    """
    print("=== Example 2: Validation Decorators ===")

    # Correct implementation with decorator
    @validation_decorator(ProtocolArtifactContainer, raise_on_error=False)
    class DecoratedGoodContainer:
        def get_status(self) -> ProtocolArtifactContainerStatus:
            class Status:
                status = "ACTIVE"
                message = "All good"
                artifact_count = 2
                valid_artifact_count = 2
                invalid_artifact_count = 0
                wip_artifact_count = 0
                artifact_types_found = ["nodes", "cli_tools"]

            return Status()

        def get_artifacts(self) -> List[ProtocolArtifactInfo]:
            return [
                self._mock_artifact("test1", "nodes"),
                self._mock_artifact("test2", "cli_tools"),
            ]

        def get_artifacts_by_type(
            self, artifact_type: ContainerArtifactType
        ) -> List[ProtocolArtifactInfo]:
            all_artifacts = self.get_artifacts()
            return [a for a in all_artifacts if a.artifact_type == artifact_type]

        def get_artifact_by_name(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> ProtocolArtifactInfo:
            for artifact in self.get_artifacts():
                if artifact.name == name:
                    if artifact_type is None or artifact.artifact_type == artifact_type:
                        return artifact
            raise ValueError(f"Artifact {name} not found")

        def has_artifact(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> bool:
            try:
                self.get_artifact_by_name(name, artifact_type)
                return True
            except ValueError:
                return False

        def _mock_artifact(self, name: str, artifact_type: str):
            class MockArtifact:
                def __init__(self, name: str, artifact_type: str):
                    self.name = name
                    self.artifact_type = artifact_type
                    self.version = self._mock_version()
                    self.path = f"/mock/path/{name}"
                    self.metadata = self._mock_metadata()
                    self.is_wip = False

                def _mock_version(self):
                    class Version:
                        major, minor, patch = 1, 0, 0

                        def __str__(self):
                            return "1.0.0"

                    return Version()

                def _mock_metadata(self):
                    class Metadata:
                        description = f"Mock {name}"
                        author = "Test"
                        created_at = "2025-01-01"
                        last_modified_at = "2025-01-01"

                    return Metadata()

            return MockArtifact(name, artifact_type)

    # Incorrect implementation with decorator (will show validation errors)
    @validation_decorator(ProtocolArtifactContainer, raise_on_error=False)
    class DecoratedBadContainer:
        def get_status(self):
            return "just a string"  # Wrong type

        # Missing most required methods
        pass

    print("\n--- Creating Good Container (with validation) ---")
    try:
        good_container = DecoratedGoodContainer()
        print("✓ Good container created successfully")
    except Exception as e:
        print(f"✗ Error creating good container: {e}")

    print("\n--- Creating Bad Container (with validation) ---")
    try:
        bad_container = DecoratedBadContainer()
        print("✗ Bad container created (should have shown warnings)")
    except Exception as e:
        print(f"✗ Error creating bad container: {e}")

    print()


# =============================================================================
# Example 3: Using Specialized Validators
# =============================================================================


def example_specialized_validators():
    """
    Example of using specialized validators for domain-specific validation.
    """
    print("=== Example 3: Specialized Validators ===")

    # Example using ArtifactContainerValidator
    class TestContainer:
        def __init__(self):
            self.artifacts = [
                self._create_artifact("node1", "nodes"),
                self._create_artifact("tool1", "cli_tools"),
            ]

        def get_status(self):
            class Status:
                status = "ACTIVE"
                message = "Test container active"
                artifact_count = len(self.artifacts)
                valid_artifact_count = len(self.artifacts)
                invalid_artifact_count = 0
                wip_artifact_count = 0
                artifact_types_found = ["nodes", "cli_tools"]

            return Status()

        def get_artifacts(self):
            return self.artifacts

        def get_artifacts_by_type(self, artifact_type: ContainerArtifactType):
            return [a for a in self.artifacts if a.artifact_type == artifact_type]

        def get_artifact_by_name(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ):
            for artifact in self.artifacts:
                if artifact.name == name and (
                    artifact_type is None or artifact.artifact_type == artifact_type
                ):
                    return artifact
            raise ValueError(f"Artifact {name} not found")

        def has_artifact(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ):
            try:
                self.get_artifact_by_name(name, artifact_type)
                return True
            except ValueError:
                return False

        def _create_artifact(self, name: str, artifact_type: str):
            class Artifact:
                def __init__(self, name: str, artifact_type: str):
                    self.name = name
                    self.artifact_type = artifact_type
                    self.version = type(
                        "Version",
                        (),
                        {
                            "major": 1,
                            "minor": 0,
                            "patch": 0,
                            "__str__": lambda s: "1.0.0",
                        },
                    )()
                    self.path = f"/test/{name}"
                    self.metadata = type(
                        "Metadata",
                        (),
                        {
                            "description": f"Test {name}",
                            "author": "Test Author",
                            "created_at": "2025-01-01",
                            "last_modified_at": "2025-01-01",
                        },
                    )()
                    self.is_wip = False

            return Artifact(name, artifact_type)

    print("\n--- Using ArtifactContainerValidator ---")
    container = TestContainer()
    validator = ArtifactContainerValidator(strict_mode=True)
    result = validator.validate_implementation(container, ProtocolArtifactContainer)

    print(f"Validation result: {'PASSED' if result.is_valid else 'FAILED'}")
    print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    print()


# =============================================================================
# Example 4: Handler Discovery Validation
# =============================================================================


def example_handler_discovery_validation():
    """
    Example of validating handler discovery implementations.
    """
    print("=== Example 4: Handler Discovery Validation ===")

    class TestHandlerDiscovery:
        def __init__(self, source_name: str = "TestDiscovery"):
            self.source_name = source_name

        def discover_nodes(self) -> List[ProtocolHandlerInfo]:
            # Return mock handler info objects
            handlers = []

            # Mock handler info
            class MockHandlerInfo:
                def __init__(self, name: str):
                    self.node_class = type(f"Mock{name}Handler", (), {})  # Mock class
                    self.name = name
                    self.source = "test"
                    self.priority = 50
                    self.extensions = [".test"]
                    self.special_files = ["test.config"]
                    self.metadata = {"test": True}

            handlers.append(MockHandlerInfo("TestHandler1"))
            handlers.append(MockHandlerInfo("TestHandler2"))

            return handlers

        def get_source_name(self) -> str:
            return self.source_name

    # Test with HandlerDiscoveryValidator
    print("\n--- Using HandlerDiscoveryValidator ---")
    discovery = TestHandlerDiscovery("TestSource")
    validator = HandlerDiscoveryValidator()
    result = validator.validate_implementation(discovery, ProtocolHandlerDiscovery)

    print(f"Validation result: {'PASSED' if result.is_valid else 'FAILED'}")
    print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    print()


# =============================================================================
# Example 5: Error Handling and Debugging
# =============================================================================


def example_error_handling():
    """
    Example of error handling and debugging with validation.
    """
    print("=== Example 5: Error Handling and Debugging ===")

    # Implementation with various errors
    class ProblematicContainer:
        def get_status(self):
            # Wrong return type
            return "active"

        def get_artifacts(self):
            # Returns wrong type
            return "not a list"

        # Missing required methods

    print("\n--- Comprehensive Error Analysis ---")
    container = ProblematicContainer()

    # Use specialized validator for detailed analysis
    validator = ArtifactContainerValidator(strict_mode=True)
    result = validator.validate_implementation(container, ProtocolArtifactContainer)

    print("Full validation summary:")
    print(result.get_summary())

    # Analyze specific error types
    error_types = {}
    for error in result.errors:
        error_type = error.error_type
        if error_type not in error_types:
            error_types[error_type] = []
        error_types[error_type].append(error)

    print(f"\nError type breakdown:")
    for error_type, errors in error_types.items():
        print(f"  {error_type}: {len(errors)} occurrences")
        for error in errors[:2]:  # Show first 2 of each type
            print(f"    - {error.message}")
        if len(errors) > 2:
            print(f"    ... and {len(errors) - 2} more")

    print()


# =============================================================================
# Example 6: Development Workflow Integration
# =============================================================================


def example_development_workflow():
    """
    Example of integrating validation into development workflow.
    """
    print("=== Example 6: Development Workflow Integration ===")

    # Step 1: Start with protocol interface
    print("\n--- Step 1: Define Protocol Implementation ---")

    class DevelopmentContainer:
        """Container implementation in development."""

        def __init__(self):
            self._artifacts = []
            self._status = "INACTIVE"

        def get_status(self):
            # Start with basic implementation
            class Status:
                status = "INACTIVE"
                message = "Development container"
                artifact_count = 0
                valid_artifact_count = 0
                invalid_artifact_count = 0
                wip_artifact_count = 0
                artifact_types_found = []

            return Status()

        # TODO: Implement remaining methods

    # Step 2: Early validation to identify missing pieces
    print("\n--- Step 2: Early Validation Check ---")
    container = DevelopmentContainer()
    result = validate_protocol_implementation(
        container,
        ProtocolArtifactContainer,
        strict_mode=False,  # Less strict during development
        print_results=False,
    )

    print(f"Implementation completeness: {100 - len(result.errors) * 10}%")
    print(
        f"Missing methods: {len([e for e in result.errors if e.error_type == 'missing_method'])}"
    )

    # Step 3: Iterative improvement
    print("\n--- Step 3: Implementation Guidance ---")
    missing_methods = [e for e in result.errors if e.error_type == "missing_method"]
    if missing_methods:
        print("Next methods to implement:")
        for error in missing_methods[:3]:  # Show first 3
            method_name = error.context.get("method", "unknown")
            print(f"  - {method_name}()")

    # Step 4: Final validation
    print("\n--- Step 4: Ready for Production Check ---")
    print("Before deploying, run:")
    print("  result = ArtifactContainerValidator().validate_implementation(container)")
    print("  if result.is_valid: deploy_container(container)")

    print()


# =============================================================================
# Main Example Runner
# =============================================================================


def run_all_examples():
    """Run all validation examples."""
    print("ONEX SPI Protocol Validation Examples")
    print("=" * 50)

    try:
        example_basic_validation()
        example_validation_decorators()
        example_specialized_validators()
        example_handler_discovery_validation()
        example_error_handling()
        example_development_workflow()

        print("All examples completed successfully!")

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
