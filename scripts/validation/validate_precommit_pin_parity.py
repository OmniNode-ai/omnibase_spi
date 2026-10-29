#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
CI/pre-commit check: pin-parity ratchet between .pre-commit-config.yaml and the
CI workflow(s) that independently pin the SAME omnibase_core validator
(OMN-14670, WS7 fan-out of OMN-14655; DRIFT-3 recurrence guard).

The problem this guards: a pre-commit `repo:` hook pins an omnibase_core `rev:`
that clones the validator at one SHA, while a CI ratchet job
(`uv run --with "omnibase-core @ git+...@<sha>"`) pins the SAME validator at a
DIFFERENT SHA. Both surfaces then enforce a DIFFERENT frozen baseline, so a
change that is green locally can be red in CI (or vice-versa) purely because the
two pins drifted -- staleness by construction. This gate fails closed the moment
a pinned pair diverges, on either side.

Adaptation to omnibase_spi: like the omnimarket/omniclaude canary (and unlike
omnibase_infra, which uses dedicated per-validator gate workflow files), spi
pins its shared-validator core SHA inline in `ci.yml` itself -- the
`no-noncanonical-lifecycle-classes` CI job runs
`uv run --no-project --with 'omnibase-core @ git+...@<sha>'
python -m omnibase_core.validators.no_noncanonical_lifecycle_classes`, and the
`repo:` hook of the same id in .pre-commit-config.yaml pins the same core SHA.
So the one PIN_PAIRS row names `.github/workflows/ci.yml` as the CI side, giving
a strict 1:1 hook<->gate comparison.

PIN_PAIRS below is a small, explicitly-verified table -- add a new pair only
after confirming (by hand, via `git diff <old-rev> <new-rev>` in omnibase_core)
that both sides really do reference the same validator, not two independently
pinned tools that happen to share an upstream repo. The other omnibase_core
`repo:` hooks in this config (check-stub-implementations,
validate-validator-requirements) have NO inline `omnibase-core @ git+...@<sha>`
counterpart in any spi workflow, so they are intentionally out of scope here.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / ".pre-commit-config.yaml"

# (pre-commit hook id, pre-commit repo URL, CI workflow file (repo-relative),
#  validator module the pair references [for humans/audit only]) -> both sides
# must resolve to the identical pinned omnibase_core SHA.
PIN_PAIRS: tuple[tuple[str, str, str, str], ...] = (
    (
        "no-noncanonical-lifecycle-classes",
        "https://github.com/OmniNode-ai/omnibase_core",
        ".github/workflows/ci.yml",
        "no_noncanonical_lifecycle_classes",
    ),
)

_CI_PIN_RE = re.compile(
    r"omnibase-core\s*@\s*git\+https://github\.com/OmniNode-ai/omnibase_core"
    r"(?:\.git)?@([0-9a-f]{40})"
)


def _find_hook_rev(config: dict[str, Any], hook_id: str, repo_url: str) -> str | None:
    for repo in config.get("repos", []):
        if repo.get("repo") != repo_url:
            continue
        for hook in repo.get("hooks", []):
            if hook.get("id") == hook_id:
                rev = repo.get("rev")
                return str(rev) if rev is not None else None
    return None


def _find_ci_pins(ci_text: str) -> list[str]:
    return [m.group(1) for m in _CI_PIN_RE.finditer(ci_text)]


def main() -> int:
    if not CONFIG_PATH.is_file():
        print(f"ERROR: {CONFIG_PATH} not found", file=sys.stderr)
        return 1

    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))

    violations: list[str] = []

    for hook_id, repo_url, ci_workflow_rel, validator in PIN_PAIRS:
        ci_workflow_path = REPO_ROOT / ci_workflow_rel
        if not ci_workflow_path.is_file():
            violations.append(
                f"pin-parity: CI workflow {ci_workflow_rel!r} not found "
                f"(hook {hook_id!r}, validator {validator!r}) -- "
                "update PIN_PAIRS or restore the workflow."
            )
            continue

        precommit_rev = _find_hook_rev(config, hook_id, repo_url)
        if precommit_rev is None:
            violations.append(
                f"pin-parity: hook id={hook_id!r} not found under repo={repo_url!r} "
                f"in {CONFIG_PATH.name} -- update PIN_PAIRS or the config."
            )
            continue

        ci_pins = _find_ci_pins(ci_workflow_path.read_text(encoding="utf-8"))
        if not ci_pins:
            violations.append(
                f"pin-parity: no CI-pinned SHA found in {ci_workflow_rel} "
                f"(hook {hook_id!r}, validator {validator!r}) -- "
                "update PIN_PAIRS or restore the CI pin."
            )
            continue

        mismatched = sorted({p for p in ci_pins if p != precommit_rev})
        if mismatched:
            violations.append(
                f"pin-parity: hook {hook_id!r} pins rev={precommit_rev} in "
                f"{CONFIG_PATH.name}, but {ci_workflow_rel} pins {mismatched} "
                f"for the same validator ({validator}). These must match -- "
                "bump whichever side is stale."
            )

    if violations:
        print(f"FAIL: {len(violations)} pin-parity violation(s):\n")
        for v in violations:
            print(f"  {v}\n")
        return 1

    print("OK: all pinned revs in PIN_PAIRS match their CI-pinned counterpart.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
