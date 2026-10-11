# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-20074: the CodeQL caller uses omnibase_core's reusable, not onex_change_control's.

OCC retirement: omnibase_core carries ``codeql-reusable.yml`` with the job name,
inputs and permissions of the file it replaces, so repointing the caller keeps the
required context ``CodeQL / CodeQL Analysis (python)`` byte-identical. Only the
``uses:`` line (and the ``required-checks.yaml`` row naming it) moves.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
CALLER = REPO_ROOT / ".github" / "workflows" / "security-scan.yml"
REQUIRED_CHECKS = REPO_ROOT / ".github" / "required-checks.yaml"

# Squash commit of omnibase_core#1940, which adds the reusable on that repo's dev branch.
CORE_REUSABLE_PIN = "3fbb43eaff028a30edccb1b9b794e0a3f3d9523c"
CORE_REUSABLE_PATH = "OmniNode-ai/omnibase_core/.github/workflows/codeql-reusable.yml"
CORE_REUSABLE_USES = f"{CORE_REUSABLE_PATH}@{CORE_REUSABLE_PIN}"
FORBIDDEN_REFERENCE = "onex_change_control"
CALLER_JOB_ID = "codeql"
CALLER_JOB_NAME = "CodeQL"
REQUIRED_CONTEXT = "CodeQL / CodeQL Analysis (python)"
EXPECTED_WITH = {"language": "python", "query_suite": "security-and-quality"}
EXPECTED_PERMISSIONS = {
    "actions": "read",
    "contents": "read",
    "security-events": "write",
}


def _names_occ(text: str) -> bool:
    return FORBIDDEN_REFERENCE in text


def _caller_job() -> dict[str, Any]:
    doc = yaml.safe_load(CALLER.read_text(encoding="utf-8"))
    assert isinstance(doc, dict)
    jobs = doc["jobs"]
    assert set(jobs) == {CALLER_JOB_ID}
    job: dict[str, Any] = jobs[CALLER_JOB_ID]
    return job


def _codeql_row() -> dict[str, Any]:
    doc = yaml.safe_load(REQUIRED_CHECKS.read_text(encoding="utf-8"))
    rows = [g for g in doc["gates"] if g["name"] == REQUIRED_CONTEXT]
    assert len(rows) == 1
    row: dict[str, Any] = rows[0]
    return row


def test_codeql_caller_uses_the_core_reusable_at_the_full_sha() -> None:
    assert _caller_job()["uses"] == CORE_REUSABLE_USES
    assert re.fullmatch(r"[0-9a-f]{40}", CORE_REUSABLE_PIN)


def test_codeql_caller_names_no_onex_change_control() -> None:
    assert not _names_occ(CALLER.read_text(encoding="utf-8"))


def test_codeql_caller_job_id_name_inputs_and_permissions_are_unchanged() -> None:
    job = _caller_job()
    assert job["name"] == CALLER_JOB_NAME
    assert job["with"] == EXPECTED_WITH
    assert job["permissions"] == EXPECTED_PERMISSIONS
    assert f"{job['name']} / CodeQL Analysis ({job['with']['language']})" == (
        REQUIRED_CONTEXT
    )


def test_required_checks_codeql_row_names_the_core_file() -> None:
    row = _codeql_row()
    assert row["caller_workflow"] == "security-scan.yml"
    assert row["caller_job"] == CALLER_JOB_ID
    assert row["cross_repo_ref"] == f"{CORE_REUSABLE_PATH}@main"
    assert not _names_occ(row["cross_repo_ref"])
    assert not _names_occ(row["rationale"])


def test_occ_reference_check_has_a_positive_control() -> None:
    assert _names_occ(
        "uses: OmniNode-ai/onex_change_control/.github/workflows/codeql-reusable.yml@main"
    )
    assert not _names_occ(f"uses: {CORE_REUSABLE_USES}")
