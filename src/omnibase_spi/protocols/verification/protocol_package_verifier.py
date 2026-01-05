"""Protocol for package verification in the ONEX SPI framework.

Package verifiers provide a uniform interface for verifying the integrity
and authenticity of handler packages before loading. This enables secure
handler distribution by allowing runtime verification of artifacts.

The protocol supports:
    - Integrity verification via cryptographic hashes
    - Signature verification using Ed25519 public-key cryptography
    - Hash computation for artifact fingerprinting

Security Considerations:
    - Implementations SHOULD use constant-time comparison for hash verification
    - Signature verification SHOULD use well-tested cryptographic libraries
    - Failed verifications SHOULD NOT leak timing information

See Also:
    - docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md
    - omnibase_infra: Contains concrete verifier implementations

Example:
    ```python
    class Ed25519PackageVerifier:
        async def verify_integrity(self, artifact_path: Path, expected_hash: str) -> bool:
            computed = await self.compute_hash(artifact_path)
            return secrets.compare_digest(computed, expected_hash.lower())

        async def verify_signature(
            self, artifact_path: Path, signature: bytes, public_key: bytes
        ) -> bool:
            from nacl.signing import VerifyKey
            verify_key = VerifyKey(public_key)
            file_hash = await self.compute_hash(artifact_path)
            try:
                verify_key.verify(file_hash.encode(), signature)
                return True
            except nacl.exceptions.BadSignature:
                return False

        async def compute_hash(
            self, artifact_path: Path, algorithm: LiteralHashAlgorithm = "SHA256"
        ) -> str:
            import hashlib
            hasher = hashlib.sha256()
            with open(artifact_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()

    verifier = Ed25519PackageVerifier()
    assert isinstance(verifier, ProtocolPackageVerifier)
    ```

"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.verification.types import LiteralHashAlgorithm


@runtime_checkable
class ProtocolPackageVerifier(Protocol):
    """Protocol for verifying handler package integrity and signatures.

    Package verifiers enable secure handler distribution by providing
    cryptographic verification of artifacts before they are loaded into
    the runtime. This protocol defines a mockable interface that can have
    multiple implementations (e.g., Ed25519, RSA, or test/mock verifiers).

    Implementations should:
        - Use constant-time comparisons for hash verification
        - Use well-tested cryptographic libraries for signatures
        - Handle file I/O errors gracefully
        - Not leak timing information on verification failures

    Attributes:
        verify_integrity: Verify artifact matches expected hash.
        verify_signature: Verify artifact signature using public key.
        compute_hash: Compute cryptographic hash of artifact.

    Example:
        ```python
        class MockVerifier:
            async def verify_integrity(self, artifact_path: Path, expected_hash: str) -> bool:
                return True  # Always passes in tests

            async def verify_signature(
                self, artifact_path: Path, signature: bytes, public_key: bytes
            ) -> bool:
                return True

            async def compute_hash(
                self, artifact_path: Path, algorithm: LiteralHashAlgorithm = "SHA256"
            ) -> str:
                return "a" * 64  # Mock SHA256

        verifier = MockVerifier()
        assert isinstance(verifier, ProtocolPackageVerifier)
        ```

    See Also:
        - ``LiteralHashAlgorithm``: Supported hash algorithm types
        - ``omnibase_infra.verification``: Concrete implementations

    """

    async def verify_integrity(self, artifact_path: Path, expected_hash: str) -> bool:
        """Verify that an artifact matches the expected hash.

        Computes the hash of the artifact at the given path and compares it
        to the expected hash value. This verifies the artifact has not been
        modified or corrupted.

        Args:
            artifact_path: Path to the artifact file to verify.
            expected_hash: Expected hash value as a lowercase hexadecimal string.
                For SHA256, this should be exactly 64 characters.

        Returns:
            True if the computed hash matches the expected hash, False otherwise.

        Raises:
            FileNotFoundError: If the artifact file does not exist.
            PermissionError: If the artifact file cannot be read.
            OSError: If an I/O error occurs while reading the file.

        Note:
            Implementations MAY wrap OS-level exceptions in domain-specific
            exceptions (e.g., ``VerificationIOError``) for cleaner error handling
            at the call site.

        Security:
            Implementations SHOULD use constant-time comparison (e.g.,
            ``secrets.compare_digest``) to prevent timing attacks.

        Example:
            ```python
            async def verify_package(verifier: ProtocolPackageVerifier) -> None:
                is_valid = await verifier.verify_integrity(
                    Path("/packages/handler-1.0.0.tar.gz"),
                    "a1b2c3d4e5f6..."  # 64-char lowercase hex
                )
                if not is_valid:
                    raise SecurityError("Package integrity check failed")
            ```

        """
        ...

    async def verify_signature(
        self, artifact_path: Path, signature: bytes, public_key: bytes
    ) -> bool:
        """Verify the cryptographic signature of an artifact.

        Verifies that the artifact was signed by the holder of the
        corresponding private key. This provides authenticity verification
        in addition to integrity.

        Args:
            artifact_path: Path to the artifact file to verify.
            signature: Raw signature bytes. For Ed25519, this should be
                exactly 64 bytes.
            public_key: Raw public key bytes. For Ed25519, this should be
                exactly 32 bytes.

        Returns:
            True if the signature is valid for the artifact and public key,
            False otherwise.

        Raises:
            FileNotFoundError: If the artifact file does not exist.
            PermissionError: If the artifact file cannot be read.
            ValueError: If signature or public_key have invalid length/format.
            OSError: If an I/O error occurs while reading the file.

        Note:
            Implementations MAY wrap OS-level exceptions in domain-specific
            exceptions (e.g., ``VerificationIOError``) for cleaner error handling
            at the call site.

        Security:
            - Implementations SHOULD use Ed25519 or equivalent modern
              signature schemes
            - The signature is typically over the hash of the file content,
              not the raw file bytes
            - Failed verifications SHOULD NOT leak timing information

        Example:
            ```python
            async def verify_package_signature(verifier: ProtocolPackageVerifier) -> None:
                with open("handler-1.0.0.tar.gz.sig", "rb") as f:
                    signature = f.read()  # 64 bytes
                with open("publisher.pub", "rb") as f:
                    public_key = f.read()  # 32 bytes

                is_authentic = await verifier.verify_signature(
                    Path("/packages/handler-1.0.0.tar.gz"),
                    signature,
                    public_key,
                )
                if not is_authentic:
                    raise SecurityError("Package signature verification failed")
            ```

        """
        ...

    async def compute_hash(
        self, artifact_path: Path, algorithm: LiteralHashAlgorithm = "SHA256"
    ) -> str:
        """Compute the cryptographic hash of an artifact.

        Reads the artifact file and computes its hash using the specified
        algorithm. The result can be used for integrity verification or
        as input to signature operations.

        Args:
            artifact_path: Path to the artifact file to hash.
            algorithm: Hash algorithm to use. Defaults to "SHA256".
                Currently only SHA256 is supported.

        Returns:
            Hash value as a lowercase hexadecimal string.
            For SHA256, this is exactly 64 characters.

        Raises:
            FileNotFoundError: If the artifact file does not exist.
            PermissionError: If the artifact file cannot be read.
            OSError: If an I/O error occurs while reading the file.

        Note:
            For large files, implementations SHOULD read in chunks to
            avoid loading the entire file into memory. Implementations
            MAY wrap OS-level exceptions in domain-specific exceptions
            (e.g., ``VerificationIOError``) for cleaner error handling
            at the call site.

        Example:
            ```python
            async def compute_artifact_hash(verifier: ProtocolPackageVerifier) -> str:
                hash_value = await verifier.compute_hash(
                    Path("/packages/handler-1.0.0.tar.gz"),
                    algorithm="SHA256",
                )
                print(f"SHA256: {hash_value}")  # 64 lowercase hex chars
                return hash_value
            ```

        """
        ...


# ==============================================================================
# Module Exports
# ==============================================================================

__all__ = [
    "ProtocolPackageVerifier",
]
