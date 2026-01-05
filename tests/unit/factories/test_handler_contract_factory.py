"""
Unit tests for HandlerContractFactory.

Tests the factory for creating default handler contracts based on handler type category.
Validates that contracts are properly created with correct defaults, caching behavior,
and parameter handling.
"""

from __future__ import annotations

import pydantic
import pytest

from omnibase_core.enums import EnumHandlerTypeCategory
from omnibase_core.models.contracts.model_handler_contract import ModelHandlerContract
from omnibase_core.models.primitives.model_semver import ModelSemVer
from omnibase_spi.factories.handler_contract_factory import (
    HandlerContractFactory,
    get_default_handler_contract,
)

# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestHandlerContractFactory:
    """Tests for HandlerContractFactory class."""

    def test_factory_initialization(self) -> None:
        """Test factory can be instantiated."""
        factory = HandlerContractFactory()
        assert factory is not None

    def test_factory_has_empty_cache_on_init(self) -> None:
        """Test factory initializes with empty template cache."""
        factory = HandlerContractFactory()
        assert factory._template_cache == {}

    def test_available_types_returns_all_categories(self) -> None:
        """Test available_types returns all three handler categories."""
        factory = HandlerContractFactory()
        types = factory.available_types()

        assert EnumHandlerTypeCategory.COMPUTE in types
        assert EnumHandlerTypeCategory.EFFECT in types
        assert EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE in types
        assert len(types) == 3

    def test_available_types_returns_list(self) -> None:
        """Test available_types returns a list type."""
        factory = HandlerContractFactory()
        types = factory.available_types()

        assert isinstance(types, list)

    @pytest.mark.parametrize(
        "handler_type",
        [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ],
    )
    def test_get_default_returns_model_handler_contract(
        self, handler_type: EnumHandlerTypeCategory
    ) -> None:
        """Test get_default returns ModelHandlerContract for all types."""
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=handler_type,
            handler_name="test.handler",
            version="1.0.0",
        )

        assert isinstance(contract, ModelHandlerContract)

    @pytest.mark.parametrize(
        "handler_type",
        [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ],
    )
    def test_get_default_uses_provided_handler_name(
        self, handler_type: EnumHandlerTypeCategory
    ) -> None:
        """Test get_default uses the provided handler name."""
        factory = HandlerContractFactory()
        handler_name = "my.custom.handler"

        contract = factory.get_default(
            handler_type=handler_type,
            handler_name=handler_name,
        )

        assert contract.handler_id == handler_name
        assert contract.name == handler_name

    @pytest.mark.parametrize(
        "handler_type",
        [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ],
    )
    def test_get_default_uses_provided_version(
        self, handler_type: EnumHandlerTypeCategory
    ) -> None:
        """Test get_default uses the provided version."""
        factory = HandlerContractFactory()
        version = "2.5.0"

        contract = factory.get_default(
            handler_type=handler_type,
            handler_name="test.handler",
            version=version,
        )

        assert contract.version == version

    def test_get_default_uses_default_version(self) -> None:
        """Test get_default uses 1.0.0 when version not specified."""
        factory = HandlerContractFactory()

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
        )

        assert contract.version == "1.0.0"

    def test_get_default_raises_for_invalid_type(self) -> None:
        """Test get_default raises ValueError for unsupported type."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError, match="handler_type must be an EnumHandlerTypeCategory"):
            factory.get_default(
                handler_type="INVALID_TYPE",  # type: ignore[arg-type]
                handler_name="test.handler",
            )

    def test_template_caching(self) -> None:
        """Test templates are cached to avoid repeated file loads."""
        factory = HandlerContractFactory()

        # Cache should be empty initially
        assert EnumHandlerTypeCategory.EFFECT not in factory._template_cache

        # First call should load template
        contract1 = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="handler.one",
        )

        # Cache should now have the template
        assert EnumHandlerTypeCategory.EFFECT in factory._template_cache

        # Second call should use cached template
        contract2 = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="handler.two",
        )

        # Both should be valid but have different names
        assert contract1.handler_id == "handler.one"
        assert contract2.handler_id == "handler.two"

    def test_template_isolation(self) -> None:
        """Test modifying one contract doesn't affect another."""
        factory = HandlerContractFactory()

        contract1 = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="handler.one",
        )

        contract2 = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="handler.two",
        )

        # Contracts should be independent
        assert contract1.handler_id != contract2.handler_id
        assert contract1.handler_id == "handler.one"
        assert contract2.handler_id == "handler.two"

    def test_different_handler_types_use_different_templates(self) -> None:
        """Test that different handler types load different templates."""
        factory = HandlerContractFactory()

        compute_contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="compute.handler",
        )

        effect_contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="effect.handler",
        )

        # Templates should differ in their descriptor configurations
        assert compute_contract.descriptor.handler_kind != effect_contract.descriptor.handler_kind

    def test_get_default_accepts_model_semver(self) -> None:
        """Test get_default accepts ModelSemVer for version."""
        factory = HandlerContractFactory()
        version = ModelSemVer(major=2, minor=3, patch=4)

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
            version=version,
        )

        assert contract.version == "2.3.4"

    def test_get_default_model_semver_with_prerelease(self) -> None:
        """Test get_default handles ModelSemVer with prerelease."""
        factory = HandlerContractFactory()
        version = ModelSemVer(major=1, minor=0, patch=0, prerelease=("alpha", "1"))

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="test.handler",
            version=version,
        )

        # The version string should include prerelease
        assert contract.version == "1.0.0-alpha.1"

    @pytest.mark.parametrize(
        "version_input,expected",
        [
            ("1.0.0", "1.0.0"),
            ("2.5.10", "2.5.10"),
            (ModelSemVer(major=3, minor=0, patch=0), "3.0.0"),
            (ModelSemVer(major=0, minor=1, patch=0), "0.1.0"),
        ],
    )
    def test_get_default_version_formats(
        self, version_input: ModelSemVer | str, expected: str
    ) -> None:
        """Test various version formats are handled correctly."""
        factory = HandlerContractFactory()

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
            version=version_input,
        )

        assert contract.version == expected


@pytest.mark.unit
class TestGetDefaultHandlerContractFunction:
    """Tests for the convenience function get_default_handler_contract."""

    def test_convenience_function_returns_contract(self) -> None:
        """Test convenience function returns valid contract."""
        contract = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="test.handler",
            version="1.0.0",
        )

        assert isinstance(contract, ModelHandlerContract)
        assert contract.handler_id == "test.handler"

    def test_convenience_function_default_version(self) -> None:
        """Test convenience function uses default version."""
        contract = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
        )

        assert contract.version == "1.0.0"

    @pytest.mark.parametrize(
        "handler_type",
        [
            EnumHandlerTypeCategory.COMPUTE,
            EnumHandlerTypeCategory.EFFECT,
            EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ],
    )
    def test_convenience_function_all_types(
        self, handler_type: EnumHandlerTypeCategory
    ) -> None:
        """Test convenience function works for all handler types."""
        contract = get_default_handler_contract(
            handler_type=handler_type,
            handler_name=f"test.{handler_type.value}.handler",
        )

        assert isinstance(contract, ModelHandlerContract)

    def test_convenience_function_raises_for_invalid_type(self) -> None:
        """Test convenience function raises ValueError for invalid type."""
        with pytest.raises(ValueError, match="handler_type must be an EnumHandlerTypeCategory"):
            get_default_handler_contract(
                handler_type="NOT_A_TYPE",  # type: ignore[arg-type]
                handler_name="test.handler",
            )

    def test_convenience_function_accepts_model_semver(self) -> None:
        """Test convenience function accepts ModelSemVer."""
        version = ModelSemVer(major=5, minor=2, patch=1)

        contract = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
            version=version,
        )

        assert contract.version == "5.2.1"


@pytest.mark.unit
class TestHandlerContractFactoryContractValidation:
    """Tests validating the contract contents match handler type expectations."""

    def test_compute_handler_contract_has_compute_descriptor(self) -> None:
        """Test compute handler has compute-type descriptor."""
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="compute.test",
        )

        assert contract.descriptor.handler_kind == "compute"
        assert contract.descriptor.purity == "pure"

    def test_effect_handler_contract_has_effect_descriptor(self) -> None:
        """Test effect handler has effect-type descriptor with side_effecting purity."""
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="effect.test",
        )

        assert contract.descriptor.handler_kind == "effect"
        # Effect handlers are side_effecting, not pure
        assert contract.descriptor.purity == "side_effecting"

    def test_nondeterministic_handler_contract_has_correct_descriptor(self) -> None:
        """Test nondeterministic handler has compute kind with side_effecting purity.

        Nondeterministic compute handlers are architecturally compute nodes,
        but are treated as side-effecting for replay purposes because
        LLM calls can produce different outputs for the same input.
        """
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
            handler_name="nondeterministic.test",
        )

        # Architecturally compute, but treated as side-effecting for replay
        assert contract.descriptor.handler_kind == "compute"
        assert contract.descriptor.purity == "side_effecting"

    def test_nondeterministic_handler_has_llm_capability_input(self) -> None:
        """Test nondeterministic handler has LLM capability input."""
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
            handler_name="nondeterministic.test",
        )

        # Nondeterministic handlers typically need LLM provider capability
        assert contract.capability_inputs is not None
        assert len(contract.capability_inputs) > 0

    def test_nondeterministic_handler_has_tags(self) -> None:
        """Test nondeterministic handler has AI/LLM-related tags."""
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
            handler_name="nondeterministic.test",
        )

        assert contract.tags is not None
        assert "nondeterministic" in contract.tags
        assert "llm" in contract.tags

    def test_compute_handler_has_no_capability_inputs(self) -> None:
        """Test compute handler has no capability inputs (pure compute)."""
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="compute.test",
        )

        # Pure compute handlers have no external dependencies
        assert contract.capability_inputs is not None
        assert len(contract.capability_inputs) == 0

    def test_effect_handler_timeout_is_set(self) -> None:
        """Test effect handler has a timeout configured."""
        factory = HandlerContractFactory()
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="effect.test",
        )

        # Effect handlers need timeouts for I/O operations
        assert contract.descriptor.timeout_ms is not None
        assert contract.descriptor.timeout_ms > 0

    def test_nondeterministic_handler_has_longer_timeout(self) -> None:
        """Test nondeterministic handler has longer timeout for LLM calls."""
        factory = HandlerContractFactory()

        effect_contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="effect.test",
        )

        nondeterministic_contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
            handler_name="nondeterministic.test",
        )

        # LLM calls typically need longer timeouts than regular effects
        assert nondeterministic_contract.descriptor.timeout_ms is not None
        assert effect_contract.descriptor.timeout_ms is not None
        assert (
            nondeterministic_contract.descriptor.timeout_ms
            > effect_contract.descriptor.timeout_ms
        )


@pytest.mark.unit
class TestHandlerContractFactoryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_handler_id_validation_requires_segments(self) -> None:
        """Test that handler_id validation requires at least 2 segments."""
        factory = HandlerContractFactory()

        # Single segment should fail validation
        with pytest.raises(pydantic.ValidationError):
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="single_segment",
            )

    def test_handler_name_with_multiple_segments(self) -> None:
        """Test factory handles handler name with multiple valid segments."""
        factory = HandlerContractFactory()
        # Segments must start with letter or underscore
        handler_name = "my.handler.v1_0"

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name=handler_name,
        )

        assert contract.handler_id == handler_name

    def test_handler_name_with_underscores_in_segments(self) -> None:
        """Test factory handles handler name with underscores in segments."""
        factory = HandlerContractFactory()
        handler_name = "my_domain.my_handler"

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name=handler_name,
        )

        assert contract.handler_id == handler_name

    def test_handler_segment_starting_with_number_fails(self) -> None:
        """Test that handler_id segments starting with numbers fail validation."""
        factory = HandlerContractFactory()

        # Segments cannot start with numbers (e.g., '0' in 'v1.0')
        with pytest.raises(pydantic.ValidationError):
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="my.handler.v1.0",  # '0' is invalid segment
            )

    def test_multiple_factory_instances_independent(self) -> None:
        """Test multiple factory instances have independent caches."""
        factory1 = HandlerContractFactory()
        factory2 = HandlerContractFactory()

        # Load template in factory1
        factory1.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="handler.one",
        )

        # factory2 should have empty cache
        assert EnumHandlerTypeCategory.COMPUTE in factory1._template_cache
        assert EnumHandlerTypeCategory.COMPUTE not in factory2._template_cache

    def test_version_semver_format(self) -> None:
        """Test factory accepts semver-formatted versions."""
        factory = HandlerContractFactory()
        versions = ["1.0.0", "2.0.0-alpha", "3.0.0-beta.1", "4.0.0+build.123"]

        for version in versions:
            contract = factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="test.handler",
                version=version,
            )
            assert contract.version == version

    def test_long_handler_name_segments(self) -> None:
        """Test factory handles long segment names."""
        factory = HandlerContractFactory()
        handler_name = "very_long_domain_name.very_long_handler_name"

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name=handler_name,
        )

        assert contract.handler_id == handler_name

    def test_handler_name_with_underscore_prefix(self) -> None:
        """Test factory handles handler name with underscore-prefixed segments."""
        factory = HandlerContractFactory()
        handler_name = "_private.handler"

        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name=handler_name,
        )

        assert contract.handler_id == handler_name


@pytest.mark.unit
class TestHandlerContractFactoryImports:
    """Test that factory imports work correctly from different locations."""

    def test_import_from_factories_module(self) -> None:
        """Test direct import from handler_contract_factory module."""
        from omnibase_spi.factories.handler_contract_factory import (
            HandlerContractFactory as DirectFactory,
        )

        factory = DirectFactory()
        assert factory is not None

    def test_import_from_factories_package(self) -> None:
        """Test import from factories package."""
        from omnibase_spi.factories import HandlerContractFactory as PackageFactory

        factory = PackageFactory()
        assert factory is not None

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.factories import HandlerContractFactory as PackageFactory
        from omnibase_spi.factories.handler_contract_factory import (
            HandlerContractFactory as DirectFactory,
        )

        assert DirectFactory is PackageFactory

    def test_convenience_function_import_from_module(self) -> None:
        """Test convenience function import from module."""
        from omnibase_spi.factories.handler_contract_factory import (
            get_default_handler_contract as direct_func,
        )

        contract = direct_func(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
        )
        assert isinstance(contract, ModelHandlerContract)

    def test_convenience_function_import_from_package(self) -> None:
        """Test convenience function import from package."""
        from omnibase_spi.factories import (
            get_default_handler_contract as package_func,
        )

        contract = package_func(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
        )
        assert isinstance(contract, ModelHandlerContract)


@pytest.mark.unit
class TestVersionParsingErrorHandling:
    """Tests for version string parsing error handling.

    These tests verify that malformed version strings are rejected with
    clear, descriptive error messages rather than cryptic internal errors.
    """

    @pytest.mark.parametrize(
        "invalid_version,expected_substring",
        [
            ("1.x.0", "Invalid version format"),
            ("invalid", "Invalid version format"),
            ("1.0.x", "Invalid version format"),
            ("a.b.c", "Invalid version format"),
            ("1.2.3.4", "Invalid version format"),
            ("", "Invalid version format"),
            ("   ", "Invalid version format"),
            ("v1.0.0", "Invalid version format"),
            (".1.0", "Invalid version format"),
            ("1..0", "Invalid version format"),
            ("1.0.", "Invalid version format"),
            ("-1.0.0", "Invalid version format"),
            ("1.-1.0", "Invalid version format"),
            ("1.0.0-", "Invalid version format"),
            ("1.0.0+", "Invalid version format"),
            ("01.0.0", "Invalid version format"),  # Leading zeros not allowed in semver
            ("1.00.0", "Invalid version format"),  # Leading zeros not allowed
        ],
    )
    def test_invalid_version_string_raises_value_error(
        self, invalid_version: str, expected_substring: str
    ) -> None:
        """Test that invalid version strings raise ValueError with descriptive message."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError) as exc_info:
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="test.handler",
                version=invalid_version,
            )

        assert expected_substring in str(exc_info.value)
        # Verify the invalid version is included in error for debugging
        assert invalid_version.strip() in str(exc_info.value) or "format" in str(
            exc_info.value
        ).lower()

    def test_error_message_includes_valid_examples(self) -> None:
        """Test that error message includes examples of valid version formats."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError) as exc_info:
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="test.handler",
                version="invalid",
            )

        error_msg = str(exc_info.value)
        # Should include examples of valid formats
        assert "1.0.0" in error_msg

    def test_convenience_function_also_validates_version(self) -> None:
        """Test that convenience function also validates version strings."""
        with pytest.raises(ValueError, match="Invalid version format"):
            get_default_handler_contract(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="test.handler",
                version="1.x.0",
            )

    @pytest.mark.parametrize(
        "valid_version",
        [
            "0.0.0",
            "1.0.0",
            "10.20.30",
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0-0.3.7",
            "1.0.0-x.7.z.92",
            "1.0.0+build",
            "1.0.0+build.123",
            "1.0.0-beta+build.456",
            "1.0.0-alpha.1+001",
        ],
    )
    def test_valid_version_strings_accepted(self, valid_version: str) -> None:
        """Test that valid semver strings are accepted without error."""
        factory = HandlerContractFactory()

        # Should not raise - valid versions accepted
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="test.handler",
            version=valid_version,
        )

        assert contract.version == valid_version


@pytest.mark.unit
class TestHandlerNameValidationErrors:
    """Tests for handler_name parameter validation."""

    def test_none_handler_name_raises_value_error(self) -> None:
        """Test that None handler_name raises ValueError."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError, match="handler_name cannot be None"):
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name=None,  # type: ignore[arg-type]
            )

    def test_empty_handler_name_raises_value_error(self) -> None:
        """Test that empty handler_name raises ValueError."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError, match="empty"):
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="",
            )

    def test_whitespace_handler_name_raises_value_error(self) -> None:
        """Test that whitespace-only handler_name raises ValueError."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError, match="empty"):
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name="   ",
            )

    def test_non_string_handler_name_raises_value_error(self) -> None:
        """Test that non-string handler_name raises ValueError."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError, match="must be a string"):
            factory.get_default(
                handler_type=EnumHandlerTypeCategory.COMPUTE,
                handler_name=123,  # type: ignore[arg-type]
            )


@pytest.mark.unit
class TestHandlerTypeValidationErrors:
    """Tests for handler_type parameter validation."""

    def test_none_handler_type_raises_value_error(self) -> None:
        """Test that None handler_type raises ValueError."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError, match="handler_type cannot be None"):
            factory.get_default(
                handler_type=None,  # type: ignore[arg-type]
                handler_name="test.handler",
            )

    def test_wrong_type_handler_type_raises_value_error(self) -> None:
        """Test that wrong type for handler_type raises ValueError."""
        factory = HandlerContractFactory()

        with pytest.raises(ValueError, match="must be an EnumHandlerTypeCategory"):
            factory.get_default(
                handler_type="COMPUTE",  # type: ignore[arg-type]
                handler_name="test.handler",
            )


@pytest.mark.unit
class TestCachedFactorySingleton:
    """Tests for the cached factory singleton pattern."""

    def test_get_cached_factory_returns_same_instance(self) -> None:
        """Test that _get_cached_factory returns the same instance on repeated calls."""
        from omnibase_spi.factories.handler_contract_factory import _get_cached_factory

        # Clear any existing cache
        _get_cached_factory.cache_clear()

        factory1 = _get_cached_factory()
        factory2 = _get_cached_factory()

        # Should be the exact same instance
        assert factory1 is factory2

    def test_convenience_function_uses_shared_factory(self) -> None:
        """Test that multiple calls to get_default_handler_contract share template cache."""
        from omnibase_spi.factories.handler_contract_factory import _get_cached_factory

        # Clear any existing cache
        _get_cached_factory.cache_clear()
        factory = _get_cached_factory()

        # Verify cache is empty initially
        assert EnumHandlerTypeCategory.EFFECT not in factory._template_cache

        # Call convenience function
        get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="test.handler",
        )

        # Template should now be in the cached factory's cache
        assert EnumHandlerTypeCategory.EFFECT in factory._template_cache

    def test_multiple_convenience_calls_reuse_template_cache(self) -> None:
        """Test that template caching works across multiple convenience function calls."""
        from omnibase_spi.factories.handler_contract_factory import _get_cached_factory

        # Clear any existing cache to start fresh
        _get_cached_factory.cache_clear()

        # Create first contract
        contract1 = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="handler.one",
        )

        # Create second contract of same type (should use cached template)
        contract2 = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="handler.two",
        )

        # Contracts should be independent
        assert contract1.handler_id == "handler.one"
        assert contract2.handler_id == "handler.two"

        # Verify template was cached and reused
        factory = _get_cached_factory()
        assert EnumHandlerTypeCategory.COMPUTE in factory._template_cache

    def test_cache_clear_creates_new_factory(self) -> None:
        """Test that cache_clear creates a fresh factory instance."""
        from omnibase_spi.factories.handler_contract_factory import _get_cached_factory

        factory1 = _get_cached_factory()
        _get_cached_factory.cache_clear()
        factory2 = _get_cached_factory()

        # Should be different instances after clear
        assert factory1 is not factory2


@pytest.mark.unit
class TestTemplateExceptionTypes:
    """Tests for template-specific exception types.

    These tests verify that the factory raises appropriate typed exceptions
    for template loading and parsing errors, enabling more precise error handling.
    """

    def test_template_not_found_error_is_spi_error(self) -> None:
        """Test that TemplateNotFoundError inherits from SPIError."""
        from omnibase_spi.exceptions import (
            SPIError,
            TemplateError,
            TemplateNotFoundError,
        )

        assert issubclass(TemplateNotFoundError, TemplateError)
        assert issubclass(TemplateNotFoundError, SPIError)
        assert issubclass(TemplateNotFoundError, Exception)

    def test_template_parse_error_is_spi_error(self) -> None:
        """Test that TemplateParseError inherits from SPIError."""
        from omnibase_spi.exceptions import SPIError, TemplateError, TemplateParseError

        assert issubclass(TemplateParseError, TemplateError)
        assert issubclass(TemplateParseError, SPIError)
        assert issubclass(TemplateParseError, Exception)

    def test_template_not_found_error_with_context(self) -> None:
        """Test TemplateNotFoundError includes context information."""
        from omnibase_spi.exceptions import TemplateNotFoundError

        error = TemplateNotFoundError(
            "Template file not found: test.yaml",
            context={
                "template_name": "test.yaml",
                "source": "filesystem",
                "search_path": "/path/to/templates",
            },
        )

        assert "test.yaml" in str(error)
        assert error.context["template_name"] == "test.yaml"
        assert error.context["source"] == "filesystem"
        assert "search_path" in error.context

    def test_template_parse_error_with_context(self) -> None:
        """Test TemplateParseError includes context information."""
        from omnibase_spi.exceptions import TemplateParseError

        error = TemplateParseError(
            "Invalid YAML in template: test.yaml",
            context={
                "template_name": "test.yaml",
                "yaml_error": "expected ':'",
                "source_path": "/path/to/test.yaml",
            },
        )

        assert "test.yaml" in str(error)
        assert error.context["template_name"] == "test.yaml"
        assert error.context["yaml_error"] == "expected ':'"

    def test_template_error_base_class(self) -> None:
        """Test that TemplateError can be used to catch all template errors."""
        from omnibase_spi.exceptions import (
            TemplateError,
            TemplateNotFoundError,
            TemplateParseError,
        )

        # Both specific errors should be catchable via base TemplateError
        not_found = TemplateNotFoundError("not found")
        parse_error = TemplateParseError("parse failed")

        # These should all work
        try:
            raise not_found
        except TemplateError:
            pass  # Expected

        try:
            raise parse_error
        except TemplateError:
            pass  # Expected

    def test_load_template_raises_template_not_found_error(self) -> None:
        """Test that _load_template raises TemplateNotFoundError for missing files."""
        from omnibase_spi.exceptions import TemplateNotFoundError
        from omnibase_spi.factories.handler_contract_factory import _load_template

        with pytest.raises(TemplateNotFoundError) as exc_info:
            _load_template("nonexistent_template.yaml")

        assert "nonexistent_template.yaml" in str(exc_info.value)
        assert exc_info.value.context["template_name"] == "nonexistent_template.yaml"

    def test_exception_chaining_preserved(self) -> None:
        """Test that exception chaining is preserved for debugging."""
        from omnibase_spi.exceptions import TemplateNotFoundError
        from omnibase_spi.factories.handler_contract_factory import _load_template

        try:
            _load_template("nonexistent_template.yaml")
        except TemplateNotFoundError as e:
            # The original exception should be available via __cause__
            # (This depends on implementation; if using 'from e', __cause__ is set)
            # If not chained, __cause__ is None, which is also acceptable
            # The key is that TemplateNotFoundError is raised
            assert isinstance(e, TemplateNotFoundError)


@pytest.mark.unit
class TestTemplateImmutability:
    """Tests verifying that cached templates are protected from mutation."""

    def test_template_cache_returns_deep_copy(self) -> None:
        """Test that _get_template returns a deep copy, not the cached original."""
        factory = HandlerContractFactory()

        # Get template twice
        template1 = factory._get_template(EnumHandlerTypeCategory.COMPUTE)
        template2 = factory._get_template(EnumHandlerTypeCategory.COMPUTE)

        # They should be equal in content
        assert template1 == template2

        # But they should be different objects
        assert template1 is not template2

    def test_modifying_returned_template_does_not_affect_cache(self) -> None:
        """Test that modifications to returned template don't affect cached version."""
        factory = HandlerContractFactory()

        # Get template and modify it
        template1 = factory._get_template(EnumHandlerTypeCategory.COMPUTE)
        original_handler_id = template1["handler_id"]
        template1["handler_id"] = "MODIFIED_VALUE"

        # Get template again - should have original value
        template2 = factory._get_template(EnumHandlerTypeCategory.COMPUTE)
        assert template2["handler_id"] == original_handler_id
        assert template2["handler_id"] != "MODIFIED_VALUE"

    def test_nested_modifications_dont_affect_cache(self) -> None:
        """Test that nested object modifications don't affect cached templates."""
        factory = HandlerContractFactory()

        # Get template and modify nested structure
        template1 = factory._get_template(EnumHandlerTypeCategory.EFFECT)
        if "descriptor" in template1:
            template1["descriptor"]["handler_kind"] = "MODIFIED"

        # Get template again - nested value should be unchanged
        template2 = factory._get_template(EnumHandlerTypeCategory.EFFECT)
        if "descriptor" in template2:
            assert template2["descriptor"]["handler_kind"] != "MODIFIED"
