# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-24065: pre-commit lists the core validator hooks that pass over the tree."""

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_URL = "https://github.com/OmniNode-ai/omnibase_core"
EXPECTED_HOOKS = {
    "declared-timeout-reaches-call",
    "no-time-bound-truncation",
    "no-id-from-stamp",
    "no-fixed-tmp-atomic-write",
}


def _core_hook_ids() -> set[str]:
    config = yaml.safe_load((REPO_ROOT / ".pre-commit-config.yaml").read_text())
    ids: set[str] = set()
    for repo in config["repos"]:
        if repo.get("repo") == CORE_URL:
            ids.update(hook["id"] for hook in repo.get("hooks", []))
    return ids


@pytest.mark.parametrize("hook_id", sorted(EXPECTED_HOOKS))
def test_core_validator_hook_listed(hook_id: str) -> None:
    assert hook_id in _core_hook_ids(), f"{hook_id} not listed from {CORE_URL}"
