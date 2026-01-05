"""
Tests for LiteralHandlerSourceType type alias.

Validates that LiteralHandlerSourceType:
- Is a Literal type with expected values
- Works correctly with type narrowing
- Provides exhaustive matching support
"""

from __future__ import annotations

from typing import get_args

import pytest

from omnibase_spi.protocols.handlers import LiteralHandlerSourceType

# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestLiteralHandlerSourceType:
    """Test suite for LiteralHandlerSourceType type alias."""

    def test_type_is_literal(self) -> None:
        """LiteralHandlerSourceType should be a Literal type."""
        # Get the type arguments from the Literal
        # LiteralHandlerSourceType is Literal["BOOTSTRAP", "CONTRACT", "HYBRID"]
        type_args = get_args(LiteralHandlerSourceType)
        assert len(type_args) > 0, "LiteralHandlerSourceType should have type arguments"

    def test_type_has_bootstrap_value(self) -> None:
        """LiteralHandlerSourceType should include BOOTSTRAP."""
        type_args = get_args(LiteralHandlerSourceType)
        assert "BOOTSTRAP" in type_args

    def test_type_has_contract_value(self) -> None:
        """LiteralHandlerSourceType should include CONTRACT."""
        type_args = get_args(LiteralHandlerSourceType)
        assert "CONTRACT" in type_args

    def test_type_has_hybrid_value(self) -> None:
        """LiteralHandlerSourceType should include HYBRID."""
        type_args = get_args(LiteralHandlerSourceType)
        assert "HYBRID" in type_args

    def test_type_has_exactly_three_values(self) -> None:
        """LiteralHandlerSourceType should have exactly 3 values."""
        type_args = get_args(LiteralHandlerSourceType)
        assert len(type_args) == 3

    def test_all_values_are_strings(self) -> None:
        """All LiteralHandlerSourceType values should be strings."""
        type_args = get_args(LiteralHandlerSourceType)
        for arg in type_args:
            assert isinstance(arg, str)

    def test_all_values_are_uppercase(self) -> None:
        """All LiteralHandlerSourceType values should be uppercase."""
        type_args = get_args(LiteralHandlerSourceType)
        for arg in type_args:
            assert arg == arg.upper()


@pytest.mark.unit
class TestLiteralHandlerSourceTypeUsage:
    """Test usage patterns for LiteralHandlerSourceType."""

    def test_bootstrap_is_valid_value(self) -> None:
        """BOOTSTRAP should be a valid value."""
        value: LiteralHandlerSourceType = "BOOTSTRAP"
        assert value == "BOOTSTRAP"

    def test_contract_is_valid_value(self) -> None:
        """CONTRACT should be a valid value."""
        value: LiteralHandlerSourceType = "CONTRACT"
        assert value == "CONTRACT"

    def test_hybrid_is_valid_value(self) -> None:
        """HYBRID should be a valid value."""
        value: LiteralHandlerSourceType = "HYBRID"
        assert value == "HYBRID"

    def test_exhaustive_match_pattern(self) -> None:
        """All values can be matched exhaustively."""

        def describe_source(source_type: LiteralHandlerSourceType) -> str:
            descriptions: dict[LiteralHandlerSourceType, str] = {
                "BOOTSTRAP": "Handlers registered at startup",
                "CONTRACT": "Handlers from contracts",
                "HYBRID": "Combined bootstrap and contract",
            }
            return descriptions.get(source_type, "Unknown")

        assert describe_source("BOOTSTRAP") == "Handlers registered at startup"
        assert describe_source("CONTRACT") == "Handlers from contracts"
        assert describe_source("HYBRID") == "Combined bootstrap and contract"

    def test_can_be_used_in_list(self) -> None:
        """LiteralHandlerSourceType can be used in collections."""
        source_types: list[LiteralHandlerSourceType] = [
            "BOOTSTRAP",
            "CONTRACT",
            "HYBRID",
        ]
        assert len(source_types) == 3
        assert all(isinstance(t, str) for t in source_types)

    def test_can_be_used_as_dict_key(self) -> None:
        """LiteralHandlerSourceType can be used as dictionary key."""
        handlers_by_source: dict[LiteralHandlerSourceType, int] = {
            "BOOTSTRAP": 5,
            "CONTRACT": 10,
            "HYBRID": 2,
        }
        assert handlers_by_source["BOOTSTRAP"] == 5
        assert handlers_by_source["CONTRACT"] == 10
        assert handlers_by_source["HYBRID"] == 2

    def test_equality_comparison(self) -> None:
        """LiteralHandlerSourceType values can be compared for equality."""
        source1: LiteralHandlerSourceType = "BOOTSTRAP"
        source2: LiteralHandlerSourceType = "BOOTSTRAP"
        source3: LiteralHandlerSourceType = "CONTRACT"

        assert source1 == source2
        assert source1 != source3


@pytest.mark.unit
class TestLiteralHandlerSourceTypeImports:
    """Test imports for LiteralHandlerSourceType."""

    def test_import_from_types_module(self) -> None:
        """Test direct import from types module."""
        from omnibase_spi.protocols.handlers.types import (
            LiteralHandlerSourceType as DirectLiteralHandlerSourceType,
        )

        value: DirectLiteralHandlerSourceType = "BOOTSTRAP"
        assert value == "BOOTSTRAP"

    def test_import_from_handlers_package(self) -> None:
        """Test import from handlers package."""
        from omnibase_spi.protocols.handlers import (
            LiteralHandlerSourceType as HandlersLiteralHandlerSourceType,
        )

        value: HandlersLiteralHandlerSourceType = "CONTRACT"
        assert value == "CONTRACT"

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same type."""
        from omnibase_spi.protocols.handlers import (
            LiteralHandlerSourceType as HandlersType,
        )
        from omnibase_spi.protocols.handlers.types import (
            LiteralHandlerSourceType as DirectType,
        )

        # Both should have the same type arguments
        assert get_args(DirectType) == get_args(HandlersType)


@pytest.mark.unit
class TestLiteralHandlerSourceTypeDocumentation:
    """Test documentation for LiteralHandlerSourceType."""

    def test_module_has_documentation(self) -> None:
        """The types module should have documentation."""
        from omnibase_spi.protocols.handlers import types

        assert types.__doc__ is not None
        assert len(types.__doc__.strip()) > 0

    def test_documentation_mentions_source_types(self) -> None:
        """Module documentation should mention source types."""
        from omnibase_spi.protocols.handlers import types

        doc = types.__doc__ or ""
        assert "BOOTSTRAP" in doc or "bootstrap" in doc.lower()
