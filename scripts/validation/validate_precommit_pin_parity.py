#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Compare core hook revisions with their CI requirement sources (OMN-22360).

The precommit_pin_pairs table names each hook and the file CI installs it from.
A source may be an inline workflow requirement or a requirements overlay.
Only commit SHAs and dev-merge tags are accepted, and both sides must match.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml
from timeout_utils import load_script_setting

_CI_PIN_RE = re.compile(
    r"omnibase-core\s*@\s*git\+https://github\.com/OmniNode-ai/omnibase_core"
    r"(?:\.git)?@([0-9a-f]{40}|dev-[0-9]{14}-[0-9a-f]{12})(?=$|[\s\'\"])"
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


def main(repo_root: Path) -> int:
    config_path = repo_root / ".pre-commit-config.yaml"
    if not config_path.is_file():
        print(f"ERROR: {config_path} not found", file=sys.stderr)
        return 1

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    violations: list[str] = []

    for hook_id, repo_url, ci_workflow_rel, validator in load_script_setting(
        "precommit_pin_pairs"
    ):
        ci_workflow_path = repo_root / ci_workflow_rel
        if not ci_workflow_path.is_file():
            violations.append(
                f"pin-parity: CI workflow {ci_workflow_rel!r} not found "
                f"(hook {hook_id!r}, validator {validator!r}) -- "
                "update precommit_pin_pairs in pyproject.toml or restore the workflow."
            )
            continue

        precommit_rev = _find_hook_rev(config, hook_id, repo_url)
        if precommit_rev is None:
            violations.append(
                f"pin-parity: hook id={hook_id!r} not found under repo={repo_url!r} "
                f"in {config_path.name} -- update precommit_pin_pairs in pyproject.toml or the config."
            )
            continue

        ci_pins = _find_ci_pins(ci_workflow_path.read_text(encoding="utf-8"))
        if not ci_pins:
            violations.append(
                f"pin-parity: no immutable CI-pinned ref found in {ci_workflow_rel} "
                f"(hook {hook_id!r}, validator {validator!r}) -- "
                "update precommit_pin_pairs in pyproject.toml or restore the CI pin."
            )
            continue

        mismatched = sorted({p for p in ci_pins if p != precommit_rev})
        if mismatched:
            violations.append(
                f"pin-parity: hook {hook_id!r} pins rev={precommit_rev} in "
                f"{config_path.name}, but {ci_workflow_rel} pins {mismatched} "
                f"for the same validator ({validator}). These must match -- "
                "bump whichever side is stale."
            )

    if violations:
        print(f"FAIL: {len(violations)} pin-parity violation(s):\n")
        for v in violations:
            print(f"  {v}\n")
        return 1

    print(
        "OK: all pinned revs in precommit_pin_pairs match their CI-pinned counterpart."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(Path.cwd()))
