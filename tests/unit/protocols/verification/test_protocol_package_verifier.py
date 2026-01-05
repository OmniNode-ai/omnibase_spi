"""
Tests for ProtocolPackageVerifier protocol.

Validates that ProtocolPackageVerifier:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest

from omnibase_spi.protocols.verification import (
    LiteralHashAlgorithm,
    ProtocolPackageVerifier,
)

# =============================================================================
# Mock Implementations
# =============================================================================


class MockPackageVerifier:
    """A class that fully implements the ProtocolPackageVerifier protocol."""

    def verify_integrity(self, artifact_path: Path, expected_hash: str) -> bool:
        """Verify artifact matches expected hash."""
        return True

    def verify_signature(
        self, artifact_path: Path, signature: bytes, public_key: bytes
    ) -> bool:
        """Verify artifact signature using public key."""
        return True

    def compute_hash(
        self, artifact_path: Path, algorithm: LiteralHashAlgorithm = "SHA256"
    ) -> str:
        """Compute hash of artifact."""
        return "a" * 64  # Mock SHA256 hex string


class PartialPackageVerifier:
    """A class that only implements some methods."""

    def verify_integrity(self, artifact_path: Path, expected_hash: str) -> bool:
        """Verify artifact matches expected hash."""
        return True

    # Missing: verify_signature, compute_hash


class NonCompliantVerifier:
    """A class that implements none of the ProtocolPackageVerifier protocol."""

    pass


class WrongSignatureVerifier:
    """A class with methods that have wrong signatures."""

    def verify_integrity(self, path: str) -> bool:  # Wrong signature
        """Wrong signature - missing expected_hash."""
        return True

    def verify_signature(self, artifact_path: Path) -> bool:  # Wrong signature
        """Wrong signature - missing signature and public_key."""
        return True

    def compute_hash(self, artifact_path: Path) -> str:
        """Compute hash - missing algorithm parameter."""
        return "hash"


# =============================================================================
# Test Classes: Protocol Definition
# =============================================================================


@pytest.mark.unit
class TestProtocolPackageVerifierProtocol:
    """Test suite for ProtocolPackageVerifier protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolPackageVerifier should be runtime_checkable."""
        assert hasattr(ProtocolPackageVerifier, "_is_runtime_protocol") or hasattr(
            ProtocolPackageVerifier, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolPackageVerifier should be a Protocol class."""
        from typing import Protocol

        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolPackageVerifier.__mro__
        )

    def test_protocol_has_verify_integrity_method(self) -> None:
        """ProtocolPackageVerifier should define verify_integrity method."""
        assert "verify_integrity" in dir(ProtocolPackageVerifier)
        assert callable(getattr(ProtocolPackageVerifier, "verify_integrity", None))

    def test_protocol_has_verify_signature_method(self) -> None:
        """ProtocolPackageVerifier should define verify_signature method."""
        assert "verify_signature" in dir(ProtocolPackageVerifier)
        assert callable(getattr(ProtocolPackageVerifier, "verify_signature", None))

    def test_protocol_has_compute_hash_method(self) -> None:
        """ProtocolPackageVerifier should define compute_hash method."""
        assert "compute_hash" in dir(ProtocolPackageVerifier)
        assert callable(getattr(ProtocolPackageVerifier, "compute_hash", None))

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolPackageVerifier protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolPackageVerifier()  # type: ignore[misc]


# =============================================================================
# Test Classes: Protocol Compliance
# =============================================================================


@pytest.mark.unit
class TestProtocolPackageVerifierCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        verifier = MockPackageVerifier()
        assert isinstance(verifier, ProtocolPackageVerifier)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        verifier = PartialPackageVerifier()
        assert not isinstance(verifier, ProtocolPackageVerifier)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no methods should fail isinstance check."""
        verifier = NonCompliantVerifier()
        assert not isinstance(verifier, ProtocolPackageVerifier)


# =============================================================================
# Test Classes: Method Signatures
# =============================================================================


@pytest.mark.unit
class TestProtocolPackageVerifierMethodSignatures:
    """Test method signatures from compliant mock implementation."""

    def test_verify_integrity_returns_bool(self) -> None:
        """verify_integrity should return a boolean."""
        verifier = MockPackageVerifier()
        result = verifier.verify_integrity(Path("/tmp/artifact.tar.gz"), "abc123")
        assert isinstance(result, bool)

    def test_verify_signature_returns_bool(self) -> None:
        """verify_signature should return a boolean."""
        verifier = MockPackageVerifier()
        result = verifier.verify_signature(
            Path("/tmp/artifact.tar.gz"),
            b"signature_bytes",
            b"public_key_bytes",
        )
        assert isinstance(result, bool)

    def test_compute_hash_returns_string(self) -> None:
        """compute_hash should return a string."""
        verifier = MockPackageVerifier()
        result = verifier.compute_hash(Path("/tmp/artifact.tar.gz"))
        assert isinstance(result, str)

    def test_compute_hash_with_algorithm(self) -> None:
        """compute_hash should accept algorithm parameter."""
        verifier = MockPackageVerifier()
        result = verifier.compute_hash(Path("/tmp/artifact.tar.gz"), "SHA256")
        assert isinstance(result, str)


# =============================================================================
# Test Classes: LiteralHashAlgorithm Type
# =============================================================================


@pytest.mark.unit
class TestLiteralHashAlgorithm:
    """Test suite for LiteralHashAlgorithm type alias."""

    def test_type_is_literal(self) -> None:
        """LiteralHashAlgorithm should be a Literal type."""
        type_args = get_args(LiteralHashAlgorithm)
        assert len(type_args) > 0, "LiteralHashAlgorithm should have type arguments"

    def test_type_has_sha256_value(self) -> None:
        """LiteralHashAlgorithm should include SHA256."""
        type_args = get_args(LiteralHashAlgorithm)
        assert "SHA256" in type_args

    def test_sha256_is_valid_value(self) -> None:
        """SHA256 should be a valid value."""
        value: LiteralHashAlgorithm = "SHA256"
        assert value == "SHA256"

    def test_all_values_are_uppercase(self) -> None:
        """All LiteralHashAlgorithm values should be uppercase."""
        type_args = get_args(LiteralHashAlgorithm)
        for arg in type_args:
            assert arg == arg.upper()


# =============================================================================
# Test Classes: Usage Patterns
# =============================================================================


@pytest.mark.unit
class TestProtocolPackageVerifierUsagePatterns:
    """Test common usage patterns for ProtocolPackageVerifier."""

    def test_verification_workflow(self) -> None:
        """Test typical verification workflow."""
        verifier = MockPackageVerifier()
        artifact = Path("/tmp/handler-1.0.0.tar.gz")

        # Compute hash
        computed_hash = verifier.compute_hash(artifact)
        assert len(computed_hash) == 64  # SHA256 hex length

        # Verify integrity
        is_valid = verifier.verify_integrity(artifact, computed_hash)
        assert is_valid is True

    def test_signature_verification_workflow(self) -> None:
        """Test signature verification workflow."""
        verifier = MockPackageVerifier()
        artifact = Path("/tmp/handler-1.0.0.tar.gz")

        # Mock Ed25519 signature (64 bytes) and public key (32 bytes)
        signature = b"\x00" * 64
        public_key = b"\x00" * 32

        is_valid = verifier.verify_signature(artifact, signature, public_key)
        assert is_valid is True


# =============================================================================
# Test Classes: Imports
# =============================================================================


@pytest.mark.unit
class TestProtocolPackageVerifierImports:
    """Test protocol imports from different locations."""

    def test_import_from_verification_module(self) -> None:
        """Test direct import from protocol module."""
        from omnibase_spi.protocols.verification.protocol_package_verifier import (
            ProtocolPackageVerifier as DirectProtocolPackageVerifier,
        )

        verifier = MockPackageVerifier()
        assert isinstance(verifier, DirectProtocolPackageVerifier)

    def test_import_from_verification_package(self) -> None:
        """Test import from verification package."""
        from omnibase_spi.protocols.verification import (
            ProtocolPackageVerifier as PackageProtocolPackageVerifier,
        )

        verifier = MockPackageVerifier()
        assert isinstance(verifier, PackageProtocolPackageVerifier)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.verification import (
            ProtocolPackageVerifier as PackageProtocol,
        )
        from omnibase_spi.protocols.verification.protocol_package_verifier import (
            ProtocolPackageVerifier as DirectProtocol,
        )

        assert DirectProtocol is PackageProtocol


# =============================================================================
# Test Classes: Documentation
# =============================================================================


@pytest.mark.unit
class TestProtocolPackageVerifierDocumentation:
    """Test that ProtocolPackageVerifier has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolPackageVerifier should have a docstring."""
        assert ProtocolPackageVerifier.__doc__ is not None
        assert len(ProtocolPackageVerifier.__doc__.strip()) > 0

    def test_docstring_describes_purpose(self) -> None:
        """Docstring should describe the protocol's purpose."""
        doc = ProtocolPackageVerifier.__doc__ or ""
        assert "verif" in doc.lower() or "integrity" in doc.lower()
