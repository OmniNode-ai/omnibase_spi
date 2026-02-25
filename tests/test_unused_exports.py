"""Tests for unused protocol export detection.

Verifies that all symbols in ``omnibase_spi.protocols.__all__`` are referenced
somewhere in the codebase (excluding re-export modules). Symbols on the
allowlist at ``scripts/export_allowlist.txt`` are excluded.

Ticket: OMN-794
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src directory to Python path for testing
src_dir = Path(__file__).parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import the checker module
scripts_dir = Path(__file__).parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from check_unused_exports import (
    _extract_all_exports,
    _find_symbol_consumers,
    check_unused_exports,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
PROTOCOLS_INIT = REPO_ROOT / "src" / "omnibase_spi" / "protocols" / "__init__.py"
ALLOWLIST_PATH = REPO_ROOT / "scripts" / "export_allowlist.txt"


@pytest.mark.unit
class TestUnusedExportDetection:
    """Tests for the unused protocol export checker."""

    def test_all_exports_parsed(self) -> None:
        """Verify that __all__ exports are correctly extracted."""
        exports = _extract_all_exports(PROTOCOLS_INIT)
        # The SPI exports 150+ symbols
        assert len(exports) >= 150, (
            f"Expected at least 150 exports, found {len(exports)}"
        )
        # Spot-check known protocols
        assert "ProtocolLogger" in exports
        assert "ProtocolHealthMonitor" in exports
        assert "ProtocolNode" in exports

    def test_no_unused_exports_beyond_allowlist(self) -> None:
        """Verify all exports are used (respecting the allowlist).

        This test fails if any symbol in __all__ has zero consumers
        and is NOT on the allowlist. This ensures new protocols are
        actually used before being exported.
        """
        results = check_unused_exports(allowlist_path=ALLOWLIST_PATH)
        unused = {k: v for k, v in results.items() if not v}

        if unused:
            unused_list = ", ".join(sorted(unused.keys()))
            pytest.fail(
                f"Found {len(unused)} unused export(s) not on the allowlist: "
                f"{unused_list}\n\n"
                f"Either:\n"
                f"  1. Add a consumer (test, type hint, or usage) for the protocol\n"
                f"  2. Add it to scripts/export_allowlist.txt with a justification\n"
                f"  3. Remove it from __all__ if it should not be exported"
            )

    def test_known_protocol_has_consumers(self) -> None:
        """Verify that well-known protocols have at least one consumer."""
        search_dirs = [
            REPO_ROOT / "src",
            REPO_ROOT / "tests",
        ]
        for symbol in ["ProtocolLogger", "ProtocolNode", "ProtocolHealthMonitor"]:
            consumers = _find_symbol_consumers(symbol, search_dirs)
            assert len(consumers) > 0, (
                f"Expected {symbol} to have at least one consumer"
            )

    def test_allowlist_entries_are_real_exports(self) -> None:
        """Verify all allowlist entries correspond to actual exports.

        Prevents stale allowlist entries from accumulating.
        """
        exports = set(_extract_all_exports(PROTOCOLS_INIT))
        if not ALLOWLIST_PATH.exists():
            pytest.skip("No allowlist file found")
            return  # pragma: no cover

        allowlist_entries: list[str] = []
        for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                allowlist_entries.append(line)

        stale = [e for e in allowlist_entries if e not in exports]
        if stale:
            pytest.fail(
                f"Allowlist contains {len(stale)} symbol(s) not in __all__: "
                f"{', '.join(stale)}\n"
                f"Remove stale entries from scripts/export_allowlist.txt"
            )
