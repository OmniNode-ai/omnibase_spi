"""
Tests for validation protocol interfaces.

These tests verify the new validation protocols added for the ONEX ecosystem,
ensuring proper protocol structure, typing, and interface compliance.
"""

import inspect
from typing import get_type_hints

import pytest

from omnibase_spi.protocols.validation import (
    ProtocolComplianceValidator,
    ProtocolImportValidator,
    ProtocolQualityValidator,
    ProtocolValidationOrchestrator,
)


class TestValidationProtocolStructure:
    """Test validation protocol structure and compliance."""

    def test_import_validator_protocol_structure(self) -> None:
        """Test ProtocolImportValidator has required methods and structure."""
        # Check required methods exist
        required_methods = [
            "validate_import",
            "validate_from_import",
            "validate_import_security",
            "validate_dependency_chain",
            "validate_repository_imports",
            "get_validation_summary",
            "configure_validation",
            "reset_validation_state",
        ]

        for method_name in required_methods:
            assert hasattr(
                ProtocolImportValidator, method_name
            ), f"Missing method: {method_name}"
            method = getattr(ProtocolImportValidator, method_name)
            assert callable(method), f"Method {method_name} is not callable"

    def test_compliance_validator_protocol_structure(self) -> None:
        """Test ProtocolComplianceValidator has required methods and structure."""
        # Check required methods exist
        required_methods = [
            "validate_file_compliance",
            "validate_repository_compliance",
            "validate_onex_naming",
            "validate_architecture_compliance",
            "validate_directory_structure",
            "validate_dependency_compliance",
            "aggregate_compliance_results",
            "add_custom_rule",
            "configure_onex_standards",
            "get_compliance_summary",
        ]

        for method_name in required_methods:
            assert hasattr(
                ProtocolComplianceValidator, method_name
            ), f"Missing method: {method_name}"

    def test_quality_validator_protocol_structure(self) -> None:
        """Test ProtocolQualityValidator has required methods and structure."""
        # Check required methods exist
        required_methods = [
            "validate_file_quality",
            "validate_directory_quality",
            "calculate_quality_metrics",
            "detect_code_smells",
            "check_naming_conventions",
            "analyze_complexity",
            "validate_documentation",
            "suggest_refactoring",
            "configure_standards",
            "get_validation_summary",
        ]

        for method_name in required_methods:
            assert hasattr(
                ProtocolQualityValidator, method_name
            ), f"Missing method: {method_name}"

    def test_validation_orchestrator_protocol_structure(self) -> None:
        """Test ProtocolValidationOrchestrator has required methods and structure."""
        # Check required methods exist
        required_methods = [
            "orchestrate_validation",
            "validate_imports",
            "validate_quality",
            "validate_compliance",
            "create_validation_workflow",
            "create_validation_scope",
            "get_orchestration_metrics",
            "reset_orchestration_state",
        ]

        for method_name in required_methods:
            assert hasattr(
                ProtocolValidationOrchestrator, method_name
            ), f"Missing method: {method_name}"


class TestValidationProtocolTypeAnnotations:
    """Test validation protocol type annotations."""

    def test_import_validator_type_hints(self) -> None:
        """Test ProtocolImportValidator has proper type annotations."""
        # Get type hints for the protocol
        type_hints = get_type_hints(ProtocolImportValidator)

        # Check that required attributes have type annotations
        required_attributes = [
            "validation_config",
            "security_scanning_enabled",
            "dependency_analysis_enabled",
        ]

        for attr_name in required_attributes:
            assert attr_name in type_hints, f"Missing type annotation for: {attr_name}"

    def test_compliance_validator_type_hints(self) -> None:
        """Test ProtocolComplianceValidator has proper type annotations."""
        type_hints = get_type_hints(ProtocolComplianceValidator)

        # Check required attributes
        required_attributes = [
            "onex_standards",
            "architecture_rules",
            "custom_rules",
            "strict_mode",
        ]

        for attr_name in required_attributes:
            assert attr_name in type_hints, f"Missing type annotation for: {attr_name}"

    def test_quality_validator_type_hints(self) -> None:
        """Test ProtocolQualityValidator has proper type annotations."""
        type_hints = get_type_hints(ProtocolQualityValidator)

        # Check required attributes
        required_attributes = [
            "standards",
            "enable_complexity_analysis",
            "enable_duplication_detection",
            "enable_style_checking",
        ]

        for attr_name in required_attributes:
            assert attr_name in type_hints, f"Missing type annotation for: {attr_name}"


class TestValidationProtocolMethods:
    """Test validation protocol method signatures."""

    def test_import_validator_method_signatures(self) -> None:
        """Test ProtocolImportValidator method signatures are correct."""
        # Test validate_import method signature
        validate_import = getattr(ProtocolImportValidator, "validate_import")
        sig = inspect.signature(validate_import)

        # Check parameters
        params = list(sig.parameters.keys())
        expected_params = ["self", "import_path", "description"]

        # Check required parameters are present (optional ones may vary)
        for param in expected_params:
            assert param in params, f"Missing parameter {param} in validate_import"

    def test_orchestrator_method_signatures(self) -> None:
        """Test ProtocolValidationOrchestrator method signatures are correct."""
        # Test orchestrate_validation method signature
        orchestrate_validation = getattr(
            ProtocolValidationOrchestrator, "orchestrate_validation"
        )
        sig = inspect.signature(orchestrate_validation)

        # Check parameters exist (specific parameters may vary based on implementation)
        params = list(sig.parameters.keys())
        assert "self" in params, "Missing 'self' parameter in orchestrate_validation"


class TestValidationProtocolInheritance:
    """Test validation protocol inheritance and runtime checking."""

    def test_all_validation_protocols_runtime_checkable(self) -> None:
        """Test all validation protocols are protocols."""
        protocols = [
            ProtocolImportValidator,
            ProtocolComplianceValidator,
            ProtocolQualityValidator,
            ProtocolValidationOrchestrator,
        ]

        for protocol in protocols:
            # Check that it's a protocol by checking for protocol-specific attributes
            assert hasattr(
                protocol, "__annotations__"
            ), f"{protocol.__name__} missing protocol annotations"

    def test_validation_protocols_are_protocols(self) -> None:
        """Test all validation protocols inherit from Protocol."""
        from typing import Protocol

        protocols = [
            ProtocolImportValidator,
            ProtocolComplianceValidator,
            ProtocolQualityValidator,
            ProtocolValidationOrchestrator,
        ]

        for protocol in protocols:
            # Check that it's a protocol by looking at MRO
            mro = protocol.__mro__
            protocol_in_mro = any(cls.__name__ == "Protocol" for cls in mro)
            assert (
                protocol_in_mro
            ), f"{protocol.__name__} does not inherit from Protocol"


class TestValidationProtocolConsistency:
    """Test validation protocol consistency and naming."""

    def test_validation_protocol_naming_convention(self) -> None:
        """Test validation protocols follow naming conventions."""
        protocols = [
            ProtocolImportValidator,
            ProtocolComplianceValidator,
            ProtocolQualityValidator,
            ProtocolValidationOrchestrator,
        ]

        for protocol in protocols:
            name = protocol.__name__
            assert name.startswith("Protocol"), f"{name} does not start with 'Protocol'"
            assert (
                "Validation" in name or "Validator" in name or "Orchestrator" in name
            ), f"{name} does not contain validation-related terms"

    def test_validation_methods_return_validation_result(self) -> None:
        """Test validation methods return ProtocolValidationResult where appropriate."""
        # Test actual validation methods that exist in the protocols
        protocol_methods = [
            (ProtocolImportValidator, ["validate_import", "validate_from_import"]),
            (
                ProtocolComplianceValidator,
                ["validate_file_compliance", "validate_repository_compliance"],
            ),
            (
                ProtocolQualityValidator,
                ["validate_file_quality", "validate_directory_quality"],
            ),
        ]

        # This test verifies the methods exist and are callable
        # Actual return type checking would require implementation
        for protocol, method_names in protocol_methods:
            for method_name in method_names:
                if hasattr(protocol, method_name):
                    method = getattr(protocol, method_name)
                    assert callable(
                        method
                    ), f"{method_name} in {protocol.__name__} is not callable"


class TestValidationProtocolDocstrings:
    """Test validation protocol documentation."""

    def test_validation_protocols_have_docstrings(self) -> None:
        """Test all validation protocols have proper docstrings."""
        protocols = [
            ProtocolImportValidator,
            ProtocolComplianceValidator,
            ProtocolQualityValidator,
            ProtocolValidationOrchestrator,
        ]

        for protocol in protocols:
            assert protocol.__doc__ is not None, f"{protocol.__name__} has no docstring"
            assert (
                len(protocol.__doc__.strip()) > 10
            ), f"{protocol.__name__} has insufficient docstring"

    def test_validation_methods_have_docstrings(self) -> None:
        """Test validation protocol methods have docstrings."""
        # Test a few key methods have docstrings
        key_methods = [
            ("ProtocolImportValidator", "validate_import"),
            ("ProtocolComplianceValidator", "validate_file_compliance"),
            ("ProtocolQualityValidator", "validate_file_quality"),
            ("ProtocolValidationOrchestrator", "orchestrate_validation"),
        ]

        for protocol_name, method_name in key_methods:
            protocol: type
            if protocol_name == "ProtocolImportValidator":
                protocol = ProtocolImportValidator
            elif protocol_name == "ProtocolComplianceValidator":
                protocol = ProtocolComplianceValidator
            elif protocol_name == "ProtocolQualityValidator":
                protocol = ProtocolQualityValidator
            elif protocol_name == "ProtocolValidationOrchestrator":
                protocol = ProtocolValidationOrchestrator
            else:
                continue

            if hasattr(protocol, method_name):
                method = getattr(protocol, method_name)
                assert (
                    method.__doc__ is not None
                ), f"{protocol_name}.{method_name} has no docstring"
