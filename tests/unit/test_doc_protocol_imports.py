# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Doc-drift assertion suite (OMN-16127).

Every fenced ``python`` code block in the repo's markdown documentation may
contain ``from omnibase_spi... import X`` / ``import omnibase_spi...``
statements. This suite parses every such statement out of every doc and
verifies it actually resolves against the *live* package — catching the
class of defect this ticket fixed: docs that name protocols, exceptions, or
functions that were renamed, moved, or never existed.

It also single-sources the version badge and protocol/domain counts that are
otherwise hand-copied across ~16 files: this suite fails if any doc's
``SPI-vX.Y.Z`` badge or ``protocol_*.py`` file count drifts from the live
package, so a future release bump or protocol addition/removal cannot go
stale silently the way v0.20.5/v0.22.0 and the 231-file count did.

Run standalone: ``uv run pytest tests/unit/test_doc_protocol_imports.py -v``
"""

from __future__ import annotations

import ast
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Markdown roots to scan for fenced python code containing omnibase_spi
# imports. Deliberately broad -- any doc anywhere in the tree can drift.
DOC_GLOBS: tuple[str, ...] = (
    "docs/**/*.md",
    "src/**/*.md",
    "scripts/**/*.md",
    "README.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
)

FENCE_RE = re.compile(r"```(?:python|py)\n(.*?)```", re.DOTALL)
BADGE_RE = re.compile(r"SPI-v(\d+\.\d+\.\d+)-blue")


def _doc_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in DOC_GLOBS:
        files.update(REPO_ROOT.glob(pattern))
    return sorted(f for f in files if f.is_file())


@dataclass(frozen=True)
class ImportStatement:
    doc: Path
    module: str
    names: tuple[str, ...]  # empty for a bare `import module` statement


def _extract_import_statements(doc: Path) -> list[ImportStatement]:
    content = doc.read_text(encoding="utf-8")
    statements: list[ImportStatement] = []
    for block in FENCE_RE.findall(content):
        try:
            tree = ast.parse(block)
        except SyntaxError:
            # Illustrative/partial snippet, not standalone-parseable -- skip.
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("omnibase_spi")
            ):
                names = tuple(alias.name for alias in node.names)
                statements.append(ImportStatement(doc, node.module, names))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("omnibase_spi"):
                        statements.append(ImportStatement(doc, alias.name, ()))
    return statements


def _all_import_statements() -> list[ImportStatement]:
    statements: list[ImportStatement] = []
    for doc in _doc_files():
        statements.extend(_extract_import_statements(doc))
    return statements


def _relpath(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT))


@pytest.mark.unit
def test_every_documented_import_resolves() -> None:
    """Every `from omnibase_spi... import X` in the docs must be real.

    This is the spot-check assertion required by OMN-16127's AC: every
    documented protocol/exception/type name must import successfully from
    the package at its documented path.
    """
    statements = _all_import_statements()
    assert statements, "expected to find omnibase_spi import statements in the docs"

    failures: list[str] = []
    for stmt in statements:
        try:
            module = __import__(stmt.module, fromlist=list(stmt.names) or ["_"])
        except Exception as exc:
            failures.append(
                f"{_relpath(stmt.doc)}: `import {stmt.module}` failed: "
                f"{type(exc).__name__}: {exc}"
            )
            continue
        missing = [n for n in stmt.names if not hasattr(module, n)]
        if missing:
            failures.append(
                f"{_relpath(stmt.doc)}: `from {stmt.module} import "
                f"{', '.join(stmt.names)}` -- not exported: {missing}"
            )

    assert not failures, (
        f"{len(failures)} documented import(s) do not resolve against the "
        "live package:\n" + "\n".join(f"  - {f}" for f in failures)
    )


@pytest.mark.unit
def test_no_documented_import_statement_is_empty() -> None:
    """Sanity check on the extractor itself: every parsed statement names
    at least a module (guards against a silent parsing regression making
    the drift check above vacuously pass).
    """
    for stmt in _all_import_statements():
        assert stmt.module.startswith("omnibase_spi")


def _live_package_version() -> str:
    pyproject = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    version = data["project"]["version"]
    assert isinstance(version, str)
    return version


@pytest.mark.unit
def test_version_badges_match_live_package_version() -> None:
    """Every `SPI-vX.Y.Z` badge in the docs must match the live pyproject
    version -- the single-source enforcement for OMN-16127's AC (no stale
    version badges).
    """
    live_version = _live_package_version()
    stale: list[str] = []
    for doc in _doc_files():
        content = doc.read_text(encoding="utf-8")
        for match in BADGE_RE.finditer(content):
            badge_version = match.group(1)
            if badge_version != live_version:
                stale.append(
                    f"{_relpath(doc)}: badge says v{badge_version}, live is v{live_version}"
                )

    assert not stale, f"{len(stale)} stale version badge(s) found:\n" + "\n".join(
        f"  - {f}" for f in stale
    )


@pytest.mark.unit
def test_protocol_file_count_matches_api_reference_readme() -> None:
    """The protocol-file/domain counts stamped in docs/api-reference/README.md
    and CLAUDE.md must match the live count under
    src/omnibase_spi/protocols/ -- catches the class of drift that let
    "231 protocol_*.py files" survive after the real count moved to 232.
    """
    protocols_dir = REPO_ROOT / "src" / "omnibase_spi" / "protocols"
    live_file_count = sum(1 for _ in protocols_dir.rglob("protocol_*.py"))
    live_domain_count = sum(
        1 for p in protocols_dir.iterdir() if p.is_dir() and not p.name.startswith("__")
    )

    api_reference_readme = REPO_ROOT / "docs" / "api-reference" / "README.md"
    content = api_reference_readme.read_text(encoding="utf-8")

    file_count_matches = re.findall(r"(\d+)\s*`?protocol_\*\.py`?\s*files", content)
    assert file_count_matches, (
        "expected a 'N protocol_*.py files' stamp in api-reference/README.md"
    )
    for found in file_count_matches:
        assert int(found) == live_file_count, (
            f"docs/api-reference/README.md claims {found} protocol_*.py files, "
            f"live count is {live_file_count}"
        )

    domain_count_matches = re.findall(r"(\d+)\s*protocol domains", content)
    assert domain_count_matches, (
        "expected a 'N protocol domains' stamp in api-reference/README.md"
    )
    for found in domain_count_matches:
        assert int(found) == live_domain_count, (
            f"docs/api-reference/README.md claims {found} protocol domains, "
            f"live count is {live_domain_count}"
        )
