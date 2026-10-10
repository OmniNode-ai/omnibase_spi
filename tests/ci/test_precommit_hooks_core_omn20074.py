# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-20074: no-hardcoded-topics and no-untracked-todos come from omnibase_core, with every exclude and setting unchanged.

OCC retirement S8: the hooks of these ids used to be pulled from the
change-control repository; omnibase_core exports them under the same ids, so only
``repo:`` and ``rev:`` change.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

CONFIG = Path(__file__).resolve().parents[2] / ".pre-commit-config.yaml"
CORE_REPO = "https://github.com/OmniNode-ai/omnibase_core"
CHANGE_CONTROL_REPO = "https://github.com/OmniNode-ai/onex_change_control"
# Each hook's exclude from the change-control block, byte for byte (None: no exclude).
EXPECTED_EXCLUDE: dict[str, str | None] = {
    "no-hardcoded-topics": "^(src/omnibase_spi/contracts/events/contract_git_hook_event\\.py|src/omnibase_spi/contracts/events/contract_linear_snapshot_event\\.py|src/omnibase_spi/contracts/events/contract_github_pr_status_event\\.py|src/omnibase_spi/registry/event_registry\\.py|src/omnibase_spi/contracts/defaults/default_github_pr_poller\\.yaml|src/omnibase_spi/exceptions_skill_routing\\.py)$",
    "no-untracked-todos": None,
}
# The keys each hook carried, so a widened or added setting is refused.
EXPECTED_KEYS: dict[str, list[str]] = {
    "no-hardcoded-topics": ["exclude", "id"],
    "no-untracked-todos": ["id", "stages"],
}
# The stages each hook carried (None: no stages key).
EXPECTED_STAGES: dict[str, list[str] | None] = {
    "no-hardcoded-topics": None,
    "no-untracked-todos": ["pre-commit"],
}
# Hook ids the change-control repository still supplies after the move.
REMAINING_CHANGE_CONTROL_HOOKS: set[str] = {"cosmetic-lint"}


def _repos() -> list[dict[str, object]]:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert isinstance(config, dict)
    repos = config["repos"]
    assert isinstance(repos, list)
    return [repo for repo in repos if isinstance(repo, dict)]


def _hooks(repo: dict[str, object]) -> list[dict[str, object]]:
    hooks = repo.get("hooks", [])
    assert isinstance(hooks, list)
    return [hook for hook in hooks if isinstance(hook, dict)]


def _declarations(hook_id: str) -> list[tuple[dict[str, object], dict[str, object]]]:
    return [
        (repo, hook)
        for repo in _repos()
        for hook in _hooks(repo)
        if hook.get("id") == hook_id
    ]


@pytest.mark.parametrize("hook_id", sorted(EXPECTED_EXCLUDE))
def test_hook_is_declared_once_in_an_omnibase_core_block_at_a_full_sha(
    hook_id: str,
) -> None:
    found = _declarations(hook_id)
    assert len(found) == 1
    repo, _ = found[0]
    assert repo["repo"] == CORE_REPO
    rev = repo["rev"]
    assert isinstance(rev, str)
    assert re.fullmatch(r"[0-9a-f]{40}", rev)


@pytest.mark.parametrize("hook_id", sorted(EXPECTED_EXCLUDE))
def test_hook_keeps_its_exclude_and_settings(hook_id: str) -> None:
    _, hook = _declarations(hook_id)[0]
    exclude = hook.get("exclude")
    expected = EXPECTED_EXCLUDE[hook_id]
    if expected is None:
        assert exclude is None
    else:
        assert isinstance(exclude, str)
        assert exclude == expected
    assert sorted(hook) == EXPECTED_KEYS[hook_id]
    assert hook.get("stages") == EXPECTED_STAGES[hook_id]


def test_change_control_block_supplies_only_the_hooks_not_yet_ported() -> None:
    supplied = {
        str(hook["id"])
        for repo in _repos()
        if repo["repo"] == CHANGE_CONTROL_REPO
        for hook in _hooks(repo)
    }
    assert supplied == REMAINING_CHANGE_CONTROL_HOOKS
