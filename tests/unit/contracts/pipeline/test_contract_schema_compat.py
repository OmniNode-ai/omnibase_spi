"""Tests for pipeline schema compatibility helpers."""

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.pipeline.contract_schema_compat import (
    SchemaVersion,
    is_compatible,
)


@pytest.mark.unit
class TestSchemaVersion:
    """Tests for SchemaVersion parsing."""

    def test_parse_valid(self) -> None:
        v = SchemaVersion.parse("1.0")
        assert v.major == 1
        assert v.minor == 0
        assert v.raw == "1.0"

    def test_parse_with_whitespace(self) -> None:
        v = SchemaVersion.parse("  2.3  ")
        assert v.major == 2
        assert v.minor == 3

    def test_parse_invalid_no_dot(self) -> None:
        with pytest.raises(ValueError, match="expected 'major.minor'"):
            SchemaVersion.parse("1")

    def test_parse_invalid_non_numeric(self) -> None:
        with pytest.raises(ValueError):
            SchemaVersion.parse("a.b")

    def test_frozen(self) -> None:
        # SchemaVersion uses Pydantic BaseModel(frozen=True) which raises
        # ValidationError on mutation attempts (not AttributeError).
        v = SchemaVersion.parse("1.0")
        with pytest.raises(ValidationError):
            v.major = 2  # type: ignore[misc]


@pytest.mark.unit
class TestIsCompatible:
    """Tests for is_compatible function."""

    def test_same_version(self) -> None:
        assert is_compatible("1.0", "1.0") is True

    def test_minor_difference_compatible(self) -> None:
        assert is_compatible("1.1", "1.0") is True
        assert is_compatible("1.0", "1.5") is True

    def test_major_difference_incompatible(self) -> None:
        assert is_compatible("2.0", "1.0") is False
        assert is_compatible("1.0", "2.0") is False

    def test_same_major_different_minor(self) -> None:
        assert is_compatible("3.7", "3.2") is True
