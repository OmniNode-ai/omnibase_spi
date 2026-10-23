# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-21331: exercise the canonical-file-shape job through its dev-merge tag."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/ci.yml"


def _workflow() -> dict[Any, Any]:
    loaded = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_canonical_validator_uses_a_dev_merge_tag() -> None:
    job = _workflow()["jobs"]["canonical-file-shape"]
    reference = job["env"]["CANONICAL_FILE_SHAPE_CORE"]
    assert re.fullmatch(
        r"omnibase-core @ git\+https://github\.com/OmniNode-ai/omnibase_core"
        r"@dev-[0-9]{14}-[0-9a-f]{12}",
        reference,
    ), f"canonical validator must use a dev-merge tag: {reference}"
    validator_steps = [step for step in job["steps"] if "run" in step]
    assert validator_steps
    for step in validator_steps:
        assert '--with "$CANONICAL_FILE_SHAPE_CORE"' in step["run"]


def test_pull_request_and_merge_queue_run_the_planted_sample(tmp_path: Path) -> None:
    workflow = _workflow()
    # PyYAML's YAML 1.1 safe loader also accepts `on` as the boolean True.
    events = workflow.get("on", workflow.get(True))
    assert isinstance(events, dict)
    assert {"pull_request", "merge_group"} <= events.keys()
    job = workflow["jobs"]["canonical-file-shape"]
    assert "if" not in job
    assert "needs" not in job
    (control,) = [
        step
        for step in job["steps"]
        if step.get("name", "").startswith("Positive control")
    ]
    assert "if" not in control
    git = shutil.which("git")
    bash = shutil.which("bash")
    assert git is not None
    assert bash is not None
    subprocess.run([git, "init", "--quiet", str(tmp_path)], check=True)
    result = subprocess.run(
        [bash, "-e", "-c", control["run"]],
        cwd=tmp_path,
        env={**os.environ, **job["env"], "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "positive control: planted bad sample refused" in result.stdout
    assert "positive control: clean sample accepted" in result.stdout
    assert "bin/zz_canary_planted: [noncanonical-file]" in result.stderr
    assert not (tmp_path / "bin/zz_canary_planted").exists()
    assert not (tmp_path / "tests/zz_canary_clean.py").exists()
