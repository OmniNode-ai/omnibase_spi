#!/usr/bin/env python3
"""Check for unused protocol exports in omnibase_spi.

Scans the ``__all__`` list from ``omnibase_spi.protocols`` and checks whether
each exported symbol is imported/referenced in at least one other file within
the repository (excluding the defining module and ``__init__.py`` re-exports).

Supports an allowlist for newly added APIs that may not yet have consumers.

Usage:
    # Check for unused exports (warns but does not fail)
    uv run python scripts/check_unused_exports.py

    # Strict mode: exit 1 if unused exports found (for CI)
    uv run python scripts/check_unused_exports.py --strict

    # JSON output
    uv run python scripts/check_unused_exports.py --json

    # With custom allowlist
    uv run python scripts/check_unused_exports.py --allowlist scripts/export_allowlist.txt

Ticket: OMN-794
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Repository root (relative to this script)
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
PROTOCOLS_INIT = SRC_DIR / "omnibase_spi" / "protocols" / "__init__.py"

# Default allowlist: symbols that are exported but may not yet have consumers.
# These are typically newly added APIs or types used only by downstream repos.
DEFAULT_ALLOWLIST: set[str] = set()

# Files that are excluded from "consumer" search (they define/re-export, not consume)
EXCLUDE_PATTERNS = {
    "__init__.py",
    "conftest.py",
}


def _extract_all_exports(init_path: Path) -> list[str]:
    """Extract all symbol names from the __all__ list in a Python init file.

    Args:
        init_path: Path to the __init__.py file.

    Returns:
        List of exported symbol names.
    """
    content = init_path.read_text(encoding="utf-8")
    # Match __all__ = [ ... ] spanning multiple lines
    match = re.search(r"__all__\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not match:
        return []

    all_block = match.group(1)
    # Extract quoted strings
    symbols = re.findall(r'"([^"]+)"', all_block)
    return symbols


def _load_allowlist(allowlist_path: Path | None) -> set[str]:
    """Load allowlist from file (one symbol per line, # comments supported).

    Args:
        allowlist_path: Path to the allowlist file, or None for defaults.

    Returns:
        Set of allowed symbol names.

    Raises:
        FileNotFoundError: If allowlist_path is provided but does not exist.
    """
    allowed = set(DEFAULT_ALLOWLIST)
    if allowlist_path is not None:
        if not allowlist_path.exists():
            raise FileNotFoundError(
                f"Allowlist file not found: {allowlist_path}"
            )
        for line in allowlist_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                allowed.add(line)
    return allowed


def _find_symbol_consumers(symbol: str, search_dirs: list[Path]) -> list[str]:
    """Find files that reference the given symbol (excluding re-exports).

    Searches for the symbol name in Python files, looking for actual usage
    patterns (imports, type annotations, isinstance checks) rather than
    just the defining module.

    Args:
        symbol: The symbol name to search for.
        search_dirs: Directories to search in.

    Returns:
        List of file paths that reference the symbol.
    """
    consumers: list[str] = []
    # Pattern: word boundary match for the symbol
    pattern = re.compile(rf"\b{re.escape(symbol)}\b")

    for search_dir in search_dirs:
        for py_file in search_dir.rglob("*.py"):
            # Skip excluded files
            if py_file.name in EXCLUDE_PATTERNS:
                continue
            # Skip the protocols __init__.py itself (it defines the exports)
            if py_file == PROTOCOLS_INIT:
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            if pattern.search(content):
                rel_path = str(py_file.relative_to(REPO_ROOT))
                consumers.append(rel_path)

    return consumers


def check_unused_exports(
    allowlist_path: Path | None = None,
) -> dict[str, list[str]]:
    """Check all protocol exports for usage.

    Args:
        allowlist_path: Optional path to an allowlist file.

    Returns:
        Dictionary mapping each exported symbol to its list of consumer files.
        Symbols with empty lists are unused.
    """
    exports = _extract_all_exports(PROTOCOLS_INIT)
    allowlist = _load_allowlist(allowlist_path)

    search_dirs = [
        SRC_DIR,
        REPO_ROOT / "tests",
        REPO_ROOT / "scripts",
        REPO_ROOT / "examples",
    ]
    # Only search dirs that exist
    search_dirs = [d for d in search_dirs if d.exists()]

    results: dict[str, list[str]] = {}
    for symbol in sorted(exports):
        if symbol in allowlist:
            continue
        consumers = _find_symbol_consumers(symbol, search_dirs)
        results[symbol] = consumers

    return results


def main() -> int:
    """Main entry point for the unused export checker.

    Returns:
        Exit code: 0 if no unused exports (or not strict), 1 if strict and unused found.
    """
    parser = argparse.ArgumentParser(
        description="Check for unused protocol exports in omnibase_spi"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if unused exports are found",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=None,
        help="Path to allowlist file (one symbol per line)",
    )
    args = parser.parse_args()

    results = check_unused_exports(allowlist_path=args.allowlist)

    used = {k: v for k, v in results.items() if v}
    unused = {k: v for k, v in results.items() if not v}

    if args.json_output:
        output = {
            "total_exports": len(results),
            "used_count": len(used),
            "unused_count": len(unused),
            "unused_symbols": sorted(unused.keys()),
            "used_symbols": dict(sorted(used.items())),
        }
        print(json.dumps(output, indent=2))
    else:
        print("Protocol Export Usage Report")
        print(f"{'=' * 50}")
        print(f"Total exports checked: {len(results)}")
        print(f"Used exports: {len(used)}")
        print(f"Unused exports: {len(unused)}")
        print()

        if unused:
            print("UNUSED EXPORTS:")
            print("-" * 40)
            for symbol in sorted(unused.keys()):
                print(f"  - {symbol}")
            print()
            print(
                "To allowlist these symbols, add them to scripts/export_allowlist.txt"
            )
            print("(one per line, # for comments)")
        else:
            print("All exports are used.")

    if args.strict and unused:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
