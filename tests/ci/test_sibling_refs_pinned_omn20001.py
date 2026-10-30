# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Sibling-repo reads in CI must name an exact sha (OMN-20001).

A workflow that reads a sibling repo (checkout or reusable workflow) at a
branch lets a merge in that sibling turn this repo's required checks red.
Each such read must be pinned to a 40-hex sha or to a dev-merge tag
(dev-<UTC YYYYMMDDHHMMSS>-<sha12>, a fixed ref of the sibling's dev branch, per
the rulings of 2026-10-16T09:35:49Z and 2026-10-29T01:50:26Z); a new sibling rev
is integration-tested by a consumer PR that moves the pin.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"
SHA = re.compile(r"^(?:[0-9a-f]{40}|dev-\d{14}-[0-9a-f]{12})$")
SIBLING_USES = re.compile(r"^OmniNode-ai/(?!omnibase_spi/)[^@]+@(?P<ref>.+)$")


def _steps_and_jobs(doc: dict) -> list[dict]:
    items: list[dict] = []
    for job in (doc.get("jobs") or {}).values():
        items.append(job)
        items.extend(job.get("steps") or [])
    return items


def _unpinned(doc: dict) -> list[str]:
    bad: list[str] = []
    for item in _steps_and_jobs(doc):
        uses = item.get("uses", "")
        m = SIBLING_USES.match(uses)
        if m and not SHA.match(m.group("ref")):
            bad.append(uses)
        with_ = item.get("with") or {}
        repo = with_.get("repository", "")
        sibling = repo.startswith("OmniNode-ai/") and not repo.endswith("/omnibase_spi")
        if sibling and not SHA.match(str(with_.get("ref", ""))):
            bad.append(f"checkout {repo} ref={with_.get('ref')!r}")
    return bad


@pytest.mark.unit
def test_every_sibling_read_is_sha_pinned() -> None:
    bad: dict[str, list[str]] = {}
    for path in sorted(WORKFLOWS.glob("*.yml")):
        found = _unpinned(yaml.safe_load(path.read_text(encoding="utf-8")))
        if found:
            bad[path.name] = found
    assert not bad, f"sibling reads not pinned to a sha: {bad}"


@pytest.mark.unit
@pytest.mark.parametrize(
    "snippet",
    [
        "jobs: {j: {uses: 'OmniNode-ai/omniclaude/.github/workflows/x.yml@dev'}}",
        "jobs: {j: {steps: [{uses: a/b@v1, with: {repository: OmniNode-ai/omniclaude}}]}}",
        "jobs: {j: {steps: [{uses: a/b@v1, with: {repository: OmniNode-ai/omnimarket, ref: dev}}]}}",
        "jobs: {j: {uses: 'OmniNode-ai/omnibase_core/.github/workflows/x.yml@dev-2026103015233-66d35d2283c3'}}",
    ],
)
def test_detector_flags_branch_and_missing_ref(snippet: str) -> None:
    """Positive control: the detector must fire on the pre-fix shapes."""
    assert _unpinned(yaml.safe_load(snippet))


@pytest.mark.unit
def test_detector_accepts_a_dev_merge_tag() -> None:
    """A dev-merge tag is a fixed ref; the detector must not flag it."""
    snippet = (
        "jobs: {j: {uses: "
        "'OmniNode-ai/omnibase_core/.github/workflows/x.yml@dev-20261030152335-66d35d2283c3'}}"
    )
    assert not _unpinned(yaml.safe_load(snippet))
