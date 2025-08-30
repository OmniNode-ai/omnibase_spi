#!/usr/bin/env python3
"""
Integration Test for Protocol Validation Utilities.

This script tests the validation utilities with real protocol implementations
to ensure they work correctly in the omnibase-spi environment.
"""

import sys
from typing import Any, List, Optional

import pytest

# Import protocols to test
from omnibase.protocols.container.protocol_artifact_container import (
    ContainerArtifactType,
    ProtocolArtifactContainer,
    ProtocolArtifactContainerStatus,
    ProtocolArtifactInfo,
)
from omnibase.protocols.discovery.protocol_handler_discovery import (
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
)

# Import validation utilities from utils package (concrete implementations)
try:
    from utils.omnibase_spi_validation import (
        ArtifactContainerValidator,
        HandlerDiscoveryValidator,
        validate_protocol_implementation,
        validation_decorator,
    )

    VALIDATION_AVAILABLE = True
except ImportError:
    print("Warning: Validation utilities not available. Tests will be skipped.")
    VALIDATION_AVAILABLE = False

    # Create stub implementations to allow test file to load
    def validate_protocol_implementation(*args: Any, **kwargs: Any) -> Any:
        class DummyResult:
            is_valid = True
            errors: List[Any] = []
            warnings: List[Any] = []

        return DummyResult()

    def validation_decorator(protocol: Any, *args: Any, **kwargs: Any) -> Any:
        def decorator(cls: Any) -> Any:
            return cls

        return decorator

    class DummyArtifactContainerValidator:
        pass

    class DummyHandlerDiscoveryValidator:
        pass

    # Assign to expected names
    ArtifactContainerValidator = DummyArtifactContainerValidator
    HandlerDiscoveryValidator = DummyHandlerDiscoveryValidator


@pytest.mark.skipif(
    not VALIDATION_AVAILABLE, reason="Validation utilities not available"
)  # type: ignore[misc]
def test_artifact_container_validation() -> None:
    """Test artifact container validation with complete implementation."""
    print("=== Testing Artifact Container Validation ===")

    class TestArtifactContainer:
        """Complete test implementation of ProtocolArtifactContainer."""

        def __init__(self) -> None:
            self.artifacts: List[ProtocolArtifactInfo] = []

        def get_status(self) -> ProtocolArtifactContainerStatus:
            artifacts = self.artifacts  # Capture in local scope

            class Status:
                def __init__(self) -> None:
                    from omnibase.protocols.container.protocol_artifact_container import (
                        ContainerArtifactType,
                        OnexStatus,
                    )

                    self.status: OnexStatus = "ACTIVE"
                    self.message = "Test container is active"
                    self.artifact_count = len(artifacts)
                    self.valid_artifact_count = len(artifacts)
                    self.invalid_artifact_count = 0
                    self.wip_artifact_count = 0
                    self.artifact_types_found: List[ContainerArtifactType] = []

            return Status()

        def get_artifacts(self) -> List[ProtocolArtifactInfo]:
            return self.artifacts

        def get_artifacts_by_type(
            self, artifact_type: ContainerArtifactType
        ) -> List[ProtocolArtifactInfo]:
            return [a for a in self.artifacts if a.artifact_type == artifact_type]

        def get_artifact_by_name(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> ProtocolArtifactInfo:
            for artifact in self.artifacts:
                if artifact.name == name:
                    if artifact_type is None or artifact.artifact_type == artifact_type:
                        return artifact
            raise ValueError(f"Artifact '{name}' not found")

        def has_artifact(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> bool:
            try:
                self.get_artifact_by_name(name, artifact_type)
                return True
            except ValueError:
                return False

    # Test with basic validator
    print("\n--- Basic Protocol Validation ---")
    container = TestArtifactContainer()
    result = validate_protocol_implementation(
        container, ProtocolArtifactContainer, True, False
    )

    print(f"Result: {'✓ PASSED' if result.is_valid else '✗ FAILED'}")
    print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

    # Test with specialized validator
    print("\n--- Specialized Container Validation ---")
    validator = ArtifactContainerValidator(strict_mode=True)
    result = validator.validate_implementation(container, ProtocolArtifactContainer)

    print(f"Result: {'✓ PASSED' if result.is_valid else '✗ FAILED'}")
    print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning.error_type}: {warning.message}")

    # Use assertion instead of returning value
    assert (
        result.is_valid
    ), f"Artifact container validation failed with {len(result.errors)} errors"


@pytest.mark.skipif(
    not VALIDATION_AVAILABLE, reason="Validation utilities not available"
)  # type: ignore[misc]
def test_handler_discovery_validation() -> None:
    """Test handler discovery validation."""
    print("\n=== Testing Handler Discovery Validation ===")

    class TestHandlerDiscovery:
        """Complete test implementation of ProtocolHandlerDiscovery."""

        def __init__(self) -> None:
            self.source_name = "TestDiscovery"

        def discover_nodes(self) -> List[ProtocolHandlerInfo]:
            # Create mock handler info objects
            class MockHandlerInfo:
                def __init__(self, name: str) -> None:
                    self.node_class = type(f"Handler{name}", (), {})  # Mock class
                    self.name = name
                    self.source = "test_discovery"
                    self.priority = 100
                    self.extensions = [".test", ".mock"]
                    self.special_files = ["test.config", "mock.yaml"]
                    self.metadata = {"test": True, "mock": True}

            mock1 = MockHandlerInfo("TestHandler")
            mock2 = MockHandlerInfo("MockHandler")
            return [mock1, mock2]

        def get_source_name(self) -> str:
            return self.source_name

    print("\n--- Handler Discovery Validation ---")
    discovery = TestHandlerDiscovery()
    validator = HandlerDiscoveryValidator()
    result = validator.validate_implementation(discovery, ProtocolHandlerDiscovery)

    print(f"Result: {'✓ PASSED' if result.is_valid else '✗ FAILED'}")
    print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning.error_type}: {warning.message}")

    # Use assertion instead of returning value
    assert (
        result.is_valid
    ), f"Handler discovery validation failed with {len(result.errors)} errors"


@pytest.mark.skipif(
    not VALIDATION_AVAILABLE, reason="Validation utilities not available"
)  # type: ignore[misc]
def test_validation_decorator() -> None:
    """Test validation decorator functionality."""
    print("\n=== Testing Validation Decorator ===")

    @validation_decorator(ProtocolArtifactContainer, True, False, True)
    class DecoratedContainer:
        """Container with validation decorator."""

        def get_status(self) -> ProtocolArtifactContainerStatus:
            class Status:
                def __init__(self) -> None:
                    from omnibase.protocols.container.protocol_artifact_container import (
                        ContainerArtifactType,
                        OnexStatus,
                    )

                    self.status: OnexStatus = "ACTIVE"
                    self.message = "Decorated container active"
                    self.artifact_count = 0
                    self.valid_artifact_count = 0
                    self.invalid_artifact_count = 0
                    self.wip_artifact_count = 0
                    self.artifact_types_found: List[ContainerArtifactType] = []

            return Status()

        def get_artifacts(self) -> List[ProtocolArtifactInfo]:
            return []

        def get_artifacts_by_type(
            self, artifact_type: ContainerArtifactType
        ) -> List[ProtocolArtifactInfo]:
            return []

        def get_artifact_by_name(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> ProtocolArtifactInfo:
            raise ValueError("Not found")

        def has_artifact(
            self, name: str, artifact_type: Optional[ContainerArtifactType] = None
        ) -> bool:
            return False

    print("\n--- Creating Decorated Container ---")
    try:
        container = DecoratedContainer()
        print("✓ Decorated container created successfully")
        print("  Validation occurred automatically during instantiation")
    except Exception as e:
        print(f"✗ Decorated container creation failed: {e}")
        assert False, f"Decorated container creation failed: {e}"


@pytest.mark.skipif(
    not VALIDATION_AVAILABLE, reason="Validation utilities not available"
)  # type: ignore[misc]
def test_error_scenarios() -> None:
    """Test validation with intentionally broken implementations."""
    print("\n=== Testing Error Scenarios ===")

    class BrokenContainer:
        """Intentionally broken container implementation."""

        def get_status(self) -> str:
            return "just a string"  # Wrong return type

        # Missing all other required methods

    print("\n--- Broken Container Validation ---")
    container = BrokenContainer()
    result = validate_protocol_implementation(
        container, ProtocolArtifactContainer, True, False
    )

    print(
        f"Result: {'✗ FAILED (Expected)' if not result.is_valid else '✓ Unexpected Pass'}"
    )
    print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

    if result.errors:
        print("Sample errors:")
        for error in result.errors[:3]:
            print(f"  - {error.error_type}: {error.message}")
        if len(result.errors) > 3:
            print(f"  ... and {len(result.errors) - 3} more errors")

    # This should fail, so assert that it properly detected errors
    assert (
        not result.is_valid
    ), "Error scenario validation should have failed but passed"


def run_integration_tests() -> None:
    """Run all integration tests."""
    print("ONEX SPI Protocol Validation Integration Tests")
    print("=" * 60)

    tests = [
        ("Artifact Container Validation", test_artifact_container_validation),
        ("Handler Discovery Validation", test_handler_discovery_validation),
        ("Validation Decorator", test_validation_decorator),
        ("Error Scenarios", test_error_scenarios),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            test_func()  # No longer expecting return value
            results.append((test_name, True))
            print(f"\n✓ PASSED: {test_name}")
        except AssertionError as e:
            results.append((test_name, False))
            print(f"\n✗ FAILED: {test_name} - {e}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n✗ ERROR in {test_name}: {e}")
            import traceback

            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
    else:
        print("❌ Some tests failed - check output above")
        assert passed == total, f"Integration tests failed: {passed}/{total} passed"


if __name__ == "__main__":
    try:
        run_integration_tests()
        print("All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
