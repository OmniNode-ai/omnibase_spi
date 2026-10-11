# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-20940: omnibase_spi produces the required context `public-repo-hygiene / deployment-config`.

No deployment or lab configuration lives in a shipped repository, and the check
that refuses it is a required CI context on every shipped repository. omniclaude
ships the check as the ``deployment-config`` job of its reusable hygiene workflow
and as the exported ``deployment-config`` pre-commit hook. This repository's caller workflow pins that reusable at the commit below.

The job reads no private vocabulary and uses no secret, so it runs on a fork pull
request. The pin below is the omniclaude commit that carries the job; the local hook
runs the same commit, so the local and CI verdicts cannot diverge.

Falsifier: restore the previous pin or drop the hook and the named test fails.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
CALLER = REPO_ROOT / ".github" / "workflows" / "public-repo-hygiene.yml"
PRECOMMIT = REPO_ROOT / ".pre-commit-config.yaml"

GATE_REV = "0c9f9146d8dd0446fc5c10952aa57247b3a880ae"
REUSABLE = "OmniNode-ai/omniclaude/.github/workflows/public-repo-hygiene-reusable.yml"
OMNICLAUDE = "https://github.com/OmniNode-ai/omniclaude"
CALLER_JOB_ID = "public-repo-hygiene"


def _load(path: Path) -> dict[Any, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), f"{path} did not parse to a mapping"
    return loaded


def test_caller_calls_the_reusable_hygiene_workflow_at_the_gate_revision() -> None:
    job = _load(CALLER)["jobs"][CALLER_JOB_ID]
    assert job["uses"] == f"{REUSABLE}@{GATE_REV}"


def test_caller_runs_on_every_pull_request_to_the_default_branch() -> None:
    workflow = _load(CALLER)
    triggers = workflow.get("on", workflow.get(True))
    assert isinstance(triggers, dict)
    assert triggers["pull_request"]["branches"] == ["dev"]
    assert "paths" not in triggers["pull_request"], "a paths filter hides the context"
    assert "if" not in workflow["jobs"][CALLER_JOB_ID]


def test_precommit_runs_the_deployment_config_hook_at_the_gate_revision() -> None:
    blocks = [
        (repo, hook)
        for repo in _load(PRECOMMIT)["repos"]
        if repo["repo"] == OMNICLAUDE
        for hook in repo.get("hooks", [])
        if hook.get("id") == "deployment-config"
    ]
    assert len(blocks) == 1, "exactly one deployment-config hook is declared"
    repo, hook = blocks[0]
    assert str(repo["rev"]).split()[0] == GATE_REV
    # The exported hook already runs over the staged added lines, always_run, in the
    # pre-commit stage. An override here would narrow it.
    narrowing = {"entry", "args", "files", "exclude", "stages", "always_run"}
    assert not narrowing & set(hook), sorted(narrowing & set(hook))
