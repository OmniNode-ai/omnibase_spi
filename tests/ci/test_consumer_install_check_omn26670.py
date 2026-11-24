# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""An omnibase_spi pull request is installed into its consumers before it can merge (OMN-26670).

The logic is omnibase_core's node_consumer_install_check_effect, reached through core's reusable
workflow consumer-install-check.yml at a dev-merge tag. This repository only calls it, so these tests
pin the call: the candidate, the pin shape, the docs-only scope, and that a failure is never softened.

AC1  the job calls core's reusable with omnibase-spi as the candidate.
AC2  nothing in the call can turn the node's failure (consumer, import, missing name) into a pass.
AC3  the replay of the 0.47.77 change is core's test (omnibase_core tests/unit/nodes/
     node_consumer_install_check_effect); the call here names the same reusable and pin kind.
AC4  a docs-only diff does not run it, and the scope is read the same way on every event.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / ".github" / "workflows" / "ci.yml"
_GIT = shutil.which("git") or "git"
_BASH = shutil.which("bash") or "bash"
DEV_TAG = re.compile(r"^dev-[0-9]{14}-[0-9a-f]{12}$")


def _jobs() -> dict[str, Any]:
    return yaml.safe_load(CI.read_text(encoding="utf-8"))["jobs"]


def test_ac1_the_job_calls_the_core_reusable_with_omnibase_spi_as_the_candidate() -> (
    None
):
    job = _jobs()["consumer-install-check"]
    uses = str(job["uses"])
    path, _, ref = uses.partition("@")
    assert (
        path == "OmniNode-ai/omnibase_core/.github/workflows/consumer-install-check.yml"
    )
    assert DEV_TAG.match(ref), ref
    assert job["with"]["candidate-distribution"] == "omnibase-spi"


def test_ac2_the_call_cannot_soften_the_nodes_failure() -> None:
    job = _jobs()["consumer-install-check"]
    assert "continue-on-error" not in job
    assert "if" not in job, (
        "a job-level if would let the merge queue run a job a PR skips"
    )


def test_ac4_the_docs_only_scope_comes_from_a_job_that_runs_on_every_event() -> None:
    jobs = _jobs()
    call = jobs["consumer-install-check"]
    assert "consumer-check-scope" in call["needs"]
    assert (
        call["with"]["docs-only"]
        == "${{ needs.consumer-check-scope.outputs.docs_only }}"
    )
    assert "if" not in jobs["consumer-check-scope"]


def _scope_script() -> str:
    steps = _jobs()["consumer-check-scope"]["steps"]
    return next(s["run"] for s in steps if s.get("id") == "scope")


def _git(repo: Path, *args: str) -> str:
    env = {
        "PATH": os.environ["PATH"],
        "HOME": str(repo),
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t.t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t.t",
    }
    done = subprocess.run(
        [_GIT, *args], cwd=repo, env=env, capture_output=True, text=True, check=True
    )
    return done.stdout.strip()


def _scope(repo: Path, base: str, *, event: str) -> str:
    output = repo / "gh_output"
    env = {
        "PATH": os.environ["PATH"],
        "EVENT_NAME": event,
        "PR_BASE": base if event == "pull_request" else "",
        "MQ_BASE": base if event == "merge_group" else "",
        "PUSH_BEFORE": base if event == "push" else "",
        "GITHUB_OUTPUT": str(output),
    }
    subprocess.run(
        [_BASH, "-c", _scope_script()],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
    )
    return output.read_text(encoding="utf-8").strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q", "-b", "dev")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


@pytest.mark.parametrize("event", ["pull_request", "merge_group", "push"])
def test_ac4_a_docs_only_diff_is_docs_only_on_every_event(
    repo: Path, event: str
) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("# g\n", encoding="utf-8")
    (repo / "CHANGELOG.md").write_text("# c\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "docs")
    assert _scope(repo, base, event=event) == "docs_only=true"


@pytest.mark.parametrize("event", ["pull_request", "merge_group", "push"])
def test_ac4_a_diff_with_code_runs_the_check_on_every_event(
    repo: Path, event: str
) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("# g\n", encoding="utf-8")
    (repo / "src" / "a.py").write_text("x = 2\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "code")
    assert _scope(repo, base, event=event) == "docs_only=false"


def test_ac4_no_resolvable_base_runs_the_check(repo: Path) -> None:
    assert _scope(repo, "", event="workflow_dispatch") == "docs_only=false"


def test_ac3_the_caller_cannot_narrow_the_consumers_the_core_replay_covers() -> None:
    """Core's replay of 0.47.77 fails the check; the call here passes only the candidate and the scope."""
    job = _jobs()["consumer-install-check"]
    assert set(job["with"]) == {"candidate-distribution", "docs-only"}
