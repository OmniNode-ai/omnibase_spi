"""Verification types for ONEX SPI package verification interfaces.

Domain: Hash algorithm types and verification-related type definitions.

This module defines the foundational types for package verification operations
including cryptographic hash algorithm specifications.

Hash Algorithms:
    - SHA256: SHA-256 cryptographic hash (default, recommended)

Future versions may add additional algorithms (SHA384, SHA512, BLAKE2b) as needed.

See Also:
    - protocol_package_verifier.py: The main verification protocol interface
    - omnibase_infra: Contains concrete verifier implementations

"""

from __future__ import annotations

from typing import Literal

# ==============================================================================
# Hash Algorithm Literal
# ==============================================================================

LiteralHashAlgorithm = Literal["SHA256"]
"""
Literal type representing supported cryptographic hash algorithms.

Values:
    SHA256: SHA-256 hash algorithm producing 256-bit (64 hex character) digests.
        This is the default and recommended algorithm for package verification.
        It provides a good balance of security and performance.

Hash Output Format:
    All hash values are represented as lowercase hexadecimal strings.
    - SHA256: 64 characters (256 bits / 4 bits per hex char)

Example:
    ```python
    def compute_package_hash(
        path: Path,
        algorithm: LiteralHashAlgorithm = "SHA256"
    ) -> str:
        # Returns lowercase hex string
        return "a1b2c3d4..."  # 64 chars for SHA256
    ```

Note:
    Future versions may expand this to include additional algorithms:
    - SHA384: For higher security requirements
    - SHA512: For maximum security
    - BLAKE2b: For performance-critical scenarios
"""

# ==============================================================================
# Module Exports
# ==============================================================================

__all__ = [
    "LiteralHashAlgorithm",
]
