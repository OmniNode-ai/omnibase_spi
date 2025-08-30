#!/usr/bin/env python3
"""
Integration Test for Protocol Validation Utilities.

This script tests the validation utilities with real protocol implementations
to ensure they work correctly in the omnibase-spi environment.
"""

import sys
from typing import List, Optional

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


def test_artifact_container_validation():
    """Test artifact container validation with complete implementation."""
    print("=== Testing Artifact Container Validation ===")

    class TestArtifactContainer:
        """Complete test implementation of ProtocolArtifactContainer."""

        def __init__(self):
            self.artifacts = []

        def get_status(self) -> ProtocolArtifactContainerStatus:
            class Status:
                status = "ACTIVE"
                message = "Test container is active"
                artifact_count = len(self.artifacts)
                valid_artifact_count = len(self.artifacts)
                invalid_artifact_count = 0
                wip_artifact_count = 0
                artifact_types_found = []

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
        container, ProtocolArtifactContainer, strict_mode=True, print_results=False
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

    return result.is_valid


def test_handler_discovery_validation():
    """Test handler discovery validation."""
    print("\n=== Testing Handler Discovery Validation ===")

    class TestHandlerDiscovery:
        """Complete test implementation of ProtocolHandlerDiscovery."""

        def __init__(self):
            self.source_name = "TestDiscovery"

        def discover_nodes(self) -> List[ProtocolHandlerInfo]:
            # Create mock handler info objects
            handlers = []

            class MockHandlerInfo:
                def __init__(self, name: str):
                    self.node_class = type(f"Handler{name}", (), {})  # Mock class
                    self.name = name
                    self.source = "test_discovery"
                    self.priority = 100
                    self.extensions = [".test", ".mock"]
                    self.special_files = ["test.config", "mock.yaml"]
                    self.metadata = {"test": True, "mock": True}

            handlers.append(MockHandlerInfo("TestHandler"))
            handlers.append(MockHandlerInfo("MockHandler"))

            return handlers

        def get_source_name(self) -> str:
            return self.source_name

    print("\n--- Handler Discovery Validation ---")
    discovery = TestHandlerDiscovery()
    validator = HandlerDiscoveryValidator(strict_mode=True)
    result = validator.validate_implementation(discovery, ProtocolHandlerDiscovery)

    print(f"Result: {'✓ PASSED' if result.is_valid else '✗ FAILED'}")
    print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning.error_type}: {warning.message}")

    return result.is_valid


def test_validation_decorator():
    """Test validation decorator functionality."""
    print("\n=== Testing Validation Decorator ===")

    @validation_decorator(ProtocolArtifactContainer, raise_on_error=False)
    class DecoratedContainer:
        """Container with validation decorator."""

        def get_status(self):
            class Status:
                status = "ACTIVE"
                message = "Decorated container active"
                artifact_count = 0
                valid_artifact_count = 0
                invalid_artifact_count = 0
                wip_artifact_count = 0
                artifact_types_found = []

            return Status()

        def get_artifacts(self):
            return []

        def get_artifacts_by_type(self, artifact_type):
            return []

        def get_artifact_by_name(self, name, artifact_type=None):
            raise ValueError("Not found")

        def has_artifact(self, name, artifact_type=None):
            return False

    print("\n--- Creating Decorated Container ---")
    try:
        container = DecoratedContainer()
        print("✓ Decorated container created successfully")
        print("  Validation occurred automatically during instantiation")
        return True
    except Exception as e:
        print(f"✗ Decorated container creation failed: {e}")
        return False


def test_error_scenarios():
    """Test validation with intentionally broken implementations."""
    print("\n=== Testing Error Scenarios ===")

    class BrokenContainer:
        """Intentionally broken container implementation."""

        def get_status(self):
            return "just a string"  # Wrong return type

        # Missing all other required methods

    print("\n--- Broken Container Validation ---")
    container = BrokenContainer()
    result = validate_protocol_implementation(
        container, ProtocolArtifactContainer, strict_mode=True, print_results=False
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

    # This should fail, so return True if it properly detected errors
    return not result.is_valid


def run_integration_tests():
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
            result = test_func()
            results.append((test_name, result))
            print(f"\n{'✓ PASSED' if result else '✗ FAILED'}: {test_name}")
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
        return True
    else:
        print("❌ Some tests failed - check output above")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
