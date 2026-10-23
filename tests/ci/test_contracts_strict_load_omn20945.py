# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-20945: every ticket contract in contracts/ loads through the strict loader.

The dod-verify node reads product-repo contracts through omnibase_core's
``load_yaml_mapping_no_duplicates``, so a contract with a duplicate mapping key is a
FAILED verdict even though ``yaml.safe_load`` accepts it and keeps the last value.
``contracts/OMN-20074.yaml`` carried one evidence item whose ``description`` and
``command`` were each written twice; this pins every contract to one value per key.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from omnibase_core.errors.error_duplicate_yaml_mapping_key import (
    DuplicateYamlMappingKeyError,
)
from omnibase_core.utils.util_safe_yaml_loader import load_yaml_mapping_no_duplicates

pytestmark = pytest.mark.unit

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"


def _scan(paths: list[Path]) -> list[tuple[str, int, str]]:
    duplicates: list[tuple[str, int, str]] = []
    for path in paths:
        try:
            load_yaml_mapping_no_duplicates(
                path.read_text(encoding="utf-8"), source=path.name
            )
        except DuplicateYamlMappingKeyError as error:
            duplicates.append((error.source, error.line, str(error.key)))
    return duplicates


def test_every_contract_loads_without_a_duplicate_mapping_key() -> None:
    paths = sorted(CONTRACTS.glob("*.yaml"))
    assert paths, f"no contract under {CONTRACTS}"
    refused: list[str] = []
    for path in paths:
        try:
            load_yaml_mapping_no_duplicates(
                path.read_text(encoding="utf-8"), source=path.name
            )
        except DuplicateYamlMappingKeyError as error:
            refused.append(str(error))
    assert not refused, "contracts with a duplicate mapping key: " + "; ".join(refused)


def test_strict_loader_refuses_a_duplicate_key() -> None:
    with pytest.raises(DuplicateYamlMappingKeyError):
        load_yaml_mapping_no_duplicates(
            "item:\n  description: first\n  description: second\n",
            source="positive-control.yaml",
        )


def test_ac3_scan_lists_each_duplicate_by_file_line_and_key(tmp_path: Path) -> None:
    planted = tmp_path / "OMN-0.yaml"
    planted.write_text(
        "item:\n  description: first\n  description: second\n", encoding="utf-8"
    )
    # The loader reports the third line using 1-based line numbering.
    assert _scan([planted]) == [("OMN-0.yaml", 3, "description")]

    paths = sorted(CONTRACTS.glob("*.yaml"))
    assert paths, f"no contract under {CONTRACTS}"
    duplicates = _scan(paths)
    assert duplicates == [], f"contracts with duplicate (file, line, key): {duplicates}"
