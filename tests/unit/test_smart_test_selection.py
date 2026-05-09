# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Unit tests for change-aware test selection (OMN-10758)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.ci.detect_test_paths import compute_selection, resolve_test_paths
from scripts.ci.test_selection_models import EnumFullSuiteReason, ModelTestSelection

ADJACENCY_PATH = (
    Path(__file__).parent.parent.parent / "scripts/ci/test_selection_adjacency.yaml"
)


@pytest.mark.unit
class TestResolveTestPaths:
    def test_src_protocols_change_maps_to_unit_protocols(self) -> None:
        paths = resolve_test_paths(
            ["src/omnibase_spi/protocols/core/protocol_logger.py"],
            ADJACENCY_PATH,
        )
        assert "tests/unit/protocols/" in paths

    def test_src_enums_change_expands_via_reverse_deps(self) -> None:
        paths = resolve_test_paths(
            ["src/omnibase_spi/enums/enum_spi_status.py"],
            ADJACENCY_PATH,
        )
        assert "tests/unit/enums/" in paths
        # enums reverse_deps include protocols — check expansion
        assert "tests/unit/protocols/" in paths

    def test_unit_test_only_change_included_directly(self) -> None:
        paths = resolve_test_paths(
            ["tests/unit/factories/test_something.py"],
            ADJACENCY_PATH,
        )
        assert "tests/unit/factories/" in paths

    def test_integration_test_change_ignored(self) -> None:
        paths = resolve_test_paths(
            ["tests/integration/test_protocol_integration.py"],
            ADJACENCY_PATH,
        )
        assert paths == []

    def test_unknown_src_module_not_included(self) -> None:
        paths = resolve_test_paths(
            ["src/omnibase_spi/nonexistent_module/foo.py"],
            ADJACENCY_PATH,
        )
        assert paths == []

    def test_docs_change_not_included(self) -> None:
        paths = resolve_test_paths(
            ["docs/architecture/README.md"],
            ADJACENCY_PATH,
        )
        assert paths == []

    def test_result_is_sorted(self) -> None:
        paths = resolve_test_paths(
            [
                "src/omnibase_spi/protocols/core/protocol_logger.py",
                "src/omnibase_spi/enums/enum_spi_status.py",
            ],
            ADJACENCY_PATH,
        )
        assert paths == sorted(paths)


@pytest.mark.unit
class TestComputeSelection:
    def test_feature_flag_off_returns_full_suite(self) -> None:
        sel = compute_selection(
            changed_files=["src/omnibase_spi/protocols/core/protocol_logger.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/feature-branch",
            feature_flag_enabled=False,
        )
        assert sel.is_full_suite is True
        assert sel.full_suite_reason == EnumFullSuiteReason.FEATURE_FLAG_OFF
        assert sel.split_count == 40

    def test_main_branch_forces_full_suite(self) -> None:
        sel = compute_selection(
            changed_files=["src/omnibase_spi/protocols/core/protocol_logger.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="main",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is True
        assert sel.full_suite_reason == EnumFullSuiteReason.MAIN_BRANCH

    def test_merge_group_forces_full_suite(self) -> None:
        sel = compute_selection(
            changed_files=["src/omnibase_spi/factories/factory_spi.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            event_name="merge_group",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is True
        assert sel.full_suite_reason == EnumFullSuiteReason.MERGE_GROUP

    def test_schedule_forces_full_suite(self) -> None:
        sel = compute_selection(
            changed_files=[],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            event_name="schedule",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is True
        assert sel.full_suite_reason == EnumFullSuiteReason.SCHEDULED

    def test_shared_module_protocols_forces_full_suite(self) -> None:
        sel = compute_selection(
            changed_files=["src/omnibase_spi/protocols/core/protocol_logger.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is True
        assert sel.full_suite_reason == EnumFullSuiteReason.SHARED_MODULE

    def test_test_infrastructure_pyproject_forces_full_suite(self) -> None:
        sel = compute_selection(
            changed_files=["pyproject.toml"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is True
        assert sel.full_suite_reason == EnumFullSuiteReason.TEST_INFRASTRUCTURE

    def test_test_infrastructure_conftest_forces_full_suite(self) -> None:
        sel = compute_selection(
            changed_files=["tests/conftest.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is True
        assert sel.full_suite_reason == EnumFullSuiteReason.TEST_INFRASTRUCTURE

    def test_leaf_module_change_returns_smart_selection(self) -> None:
        sel = compute_selection(
            changed_files=["src/omnibase_spi/factories/factory_something.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is False
        assert sel.full_suite_reason is None
        assert "tests/unit/factories/" in sel.selected_paths

    def test_no_mapped_changes_fallback_to_unit_root(self) -> None:
        sel = compute_selection(
            changed_files=["docs/architecture/README.md"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            feature_flag_enabled=True,
        )
        assert sel.is_full_suite is False
        assert sel.selected_paths == ["tests/unit/"]

    def test_matrix_length_equals_split_count(self) -> None:
        sel = compute_selection(
            changed_files=["src/omnibase_spi/factories/factory_something.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            feature_flag_enabled=True,
        )
        assert len(sel.matrix) == sel.split_count

    def test_output_is_json_serialisable(self) -> None:
        sel = compute_selection(
            changed_files=["src/omnibase_spi/factories/factory_something.py"],
            adjacency_path=ADJACENCY_PATH,
            ref_name="jonah/branch",
            feature_flag_enabled=True,
        )
        raw = sel.model_dump_json()
        parsed = json.loads(raw)
        assert "selected_paths" in parsed
        assert "split_count" in parsed
        assert "is_full_suite" in parsed


@pytest.mark.unit
class TestModelTestSelection:
    def test_full_suite_requires_reason(self) -> None:
        with pytest.raises(ValidationError):
            ModelTestSelection(
                selected_paths=["tests/"],
                split_count=40,
                is_full_suite=True,
                full_suite_reason=None,
                matrix=list(range(1, 41)),
            )

    def test_non_full_suite_forbids_reason(self) -> None:
        with pytest.raises(ValidationError):
            ModelTestSelection(
                selected_paths=["tests/unit/factories/"],
                split_count=1,
                is_full_suite=False,
                full_suite_reason=EnumFullSuiteReason.MAIN_BRANCH,
                matrix=[1],
            )

    def test_matrix_must_match_split_count(self) -> None:
        with pytest.raises(ValidationError):
            ModelTestSelection(
                selected_paths=["tests/unit/factories/"],
                split_count=2,
                is_full_suite=False,
                full_suite_reason=None,
                matrix=[1],  # length mismatch
            )
