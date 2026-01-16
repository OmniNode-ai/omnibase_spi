#!/usr/bin/env python3
"""
Shared constants for SPI validation scripts.

This module centralizes configuration that is shared across multiple
validation scripts to prevent drift and ensure consistency.
"""

from __future__ import annotations

# Known protocol name conflicts that are intentional and documented.
# These are protocols with the same name but different signatures that serve
# different purposes in different contexts. Add justification when adding entries.
#
# NOTE: In --strict mode, these known conflicts are still reported as info-level
# violations for user verification. This ensures periodic review that the conflicts
# remain intentional and properly documented.
KNOWN_ALLOWED_CONFLICTS: set[str] = {
    # ProtocolValidationResult: onex/protocol_validation.py vs validation/protocol_validation.py
    # ONEX-specific validation result vs general validation result
    "ProtocolValidationResult",
}
