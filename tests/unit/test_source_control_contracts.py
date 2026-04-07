# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for source control wire-format contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.source_control import (
    ModelBranch,
    ModelCheckRun,
    ModelDiff,
    ModelMergeResult,
    ModelPullRequest,
)


class TestModelPullRequest:
    def test_minimal_construction(self) -> None:
        now = datetime.now(tz=UTC)
        pr = ModelPullRequest(
            number=42,
            title="feat: add models",
            state="open",
            head_ref="feature/branch",
            base_ref="main",
            author="jonah",
            created_at=now,
            updated_at=now,
        )
        assert pr.number == 42
        assert pr.labels == []
        assert pr.merged_at is None
        assert pr.mergeable is None
        assert pr.review_decision is None
        assert pr.body == ""

    def test_full_construction(self) -> None:
        now = datetime.now(tz=UTC)
        pr = ModelPullRequest(
            number=1,
            title="fix: bug",
            body="Fixes the bug.",
            state="merged",
            head_ref="fix/bug",
            base_ref="main",
            mergeable=True,
            author="dev",
            created_at=now,
            updated_at=now,
            merged_at=now,
            labels=["bug", "urgent"],
            review_decision="approved",
        )
        assert pr.state == "merged"
        assert pr.merged_at == now
        assert pr.labels == ["bug", "urgent"]

    def test_frozen(self) -> None:
        now = datetime.now(tz=UTC)
        pr = ModelPullRequest(
            number=1,
            title="t",
            state="open",
            head_ref="h",
            base_ref="b",
            author="a",
            created_at=now,
            updated_at=now,
        )
        with pytest.raises(ValidationError):
            pr.title = "new"  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        now = datetime.now(tz=UTC)
        with pytest.raises(ValidationError):
            ModelPullRequest(
                number=1,
                title="t",
                state="open",
                head_ref="h",
                base_ref="b",
                author="a",
                created_at=now,
                updated_at=now,
                unknown_field="bad",  # type: ignore[call-arg]
            )


class TestModelBranch:
    def test_construction(self) -> None:
        branch = ModelBranch(name="main", sha="abc123")
        assert branch.name == "main"
        assert branch.sha == "abc123"
        assert branch.protected is False

    def test_protected(self) -> None:
        branch = ModelBranch(name="main", sha="abc123", protected=True)
        assert branch.protected is True

    def test_frozen(self) -> None:
        branch = ModelBranch(name="main", sha="abc123")
        with pytest.raises(ValidationError):
            branch.name = "dev"  # type: ignore[misc]


class TestModelDiff:
    def test_construction(self) -> None:
        diff = ModelDiff(files_changed=3, additions=100, deletions=50)
        assert diff.files_changed == 3
        assert diff.additions == 100
        assert diff.deletions == 50
        assert diff.patch == ""

    def test_with_patch(self) -> None:
        diff = ModelDiff(
            files_changed=1, additions=1, deletions=0, patch="@@ +1 @@\n+hello"
        )
        assert diff.patch == "@@ +1 @@\n+hello"


class TestModelCheckRun:
    def test_minimal(self) -> None:
        check = ModelCheckRun(name="lint", status="queued")
        assert check.name == "lint"
        assert check.status == "queued"
        assert check.conclusion is None
        assert check.started_at is None
        assert check.completed_at is None
        assert check.details_url is None

    def test_completed(self) -> None:
        now = datetime.now(tz=UTC)
        check = ModelCheckRun(
            name="test",
            status="completed",
            conclusion="success",
            started_at=now,
            completed_at=now,
            details_url="https://ci.example.com/runs/1",
        )
        assert check.conclusion == "success"
        assert check.details_url == "https://ci.example.com/runs/1"


class TestModelMergeResult:
    def test_success(self) -> None:
        result = ModelMergeResult(
            merged=True, sha="abc123", message="Merged via squash"
        )
        assert result.merged is True
        assert result.sha == "abc123"

    def test_failure(self) -> None:
        result = ModelMergeResult(merged=False, message="Merge conflict")
        assert result.merged is False
        assert result.sha is None
