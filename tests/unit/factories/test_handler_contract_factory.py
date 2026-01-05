"""
Unit tests for HandlerContractFactory.

Tests the factory for creating default handler contracts based on handler type category.
Validates that contracts are properly created with correct defaults, caching behavior,
and parameter handling.
"""

from __future__ import annotations

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

        with pytest.raises(ValueError, match="Unsupported handler type"):
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
        with pytest.raises(ValueError, match="Unsupported handler type"):
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
        with pytest.raises(Exception):  # ValidationError from Pydantic
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
        with pytest.raises(Exception):  # ValidationError from Pydantic
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
