# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-22895: secret-scan.yml runs TruffleHog on a hosted runner, with a planted control.

The repository is public, so the secret-scan job must run on a hosted runner. The scanner is the
image omnimarket's security-scan.yml runs, by the same digest, spelled here because this test
cannot read another repository. The control detector must match a planted token and must not match
clean text or its own file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "secret-scan.yml"
CONTROL_CONFIG = REPO_ROOT / ".github" / "trufflehog-control.yml"

TRUFFLEHOG_IMAGE = (
    "ghcr.io/trufflesecurity/trufflehog@sha256:"
    "674b2f187620a19df77f44cf9a7d77efcc581a5662accef2f2739cbb46ba4a3a"
)
HOSTED_RUNNER = "ubuntu-latest"
CONTROL_STEP = "TruffleHog planted control"
CONTROL_ARGS = (
    "--branch HEAD",
    "--config=.github/trufflehog-control.yml",
    "--include-detectors=CustomRegex",
    "--results=unverified",
    "--no-verification",
)


def _workflow() -> dict[Any, Any]:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _job() -> dict[str, Any]:
    job = _workflow()["jobs"]["secret-scan"]
    assert isinstance(job, dict)
    return job


def _scanner_steps() -> list[dict[str, Any]]:
    return [s for s in _job()["steps"] if "$TRUFFLEHOG_IMAGE" in str(s.get("run", ""))]


def _planted_token() -> str:
    # Built from parts so this file never holds a full control token.
    return "ONEX_SCAN_" + "CONTROL_" + "abcdefghijklmnopqrstuvwxyz012345"


def _detector_regex() -> re.Pattern[str]:
    config = yaml.safe_load(CONTROL_CONFIG.read_text(encoding="utf-8"))
    (detector,) = config["detectors"]
    assert detector["name"] == "OnexScanControl"
    return re.compile(detector["regex"]["token"])


def test_job_runs_on_a_hosted_runner_only() -> None:
    runs_on = _job()["runs-on"]
    assert runs_on == HOSTED_RUNNER
    assert "self-hosted" not in str(runs_on)
    assert "vars." not in str(runs_on)


def test_scanner_is_the_reference_image_digest_and_the_action_is_gone() -> None:
    assert _workflow()["env"]["TRUFFLEHOG_IMAGE"] == TRUFFLEHOG_IMAGE
    code = [
        line
        for line in WORKFLOW.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    ]
    assert not [line for line in code if "uses: trufflesecurity" in line]
    assert not [line for line in code if "trufflehog:" in line]
    assert len(_scanner_steps()) == 3


def test_ordinary_scans_are_verified_only_and_the_history_is_full() -> None:
    job = _job()
    checkout = job["steps"][0]
    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"]["fetch-depth"] == 0
    ordinary = [s for s in _scanner_steps() if "--only-verified" in s["run"]]
    assert {s["name"] for s in ordinary} == {
        "TruffleHog Secret Scanning (push diff)",
        "TruffleHog Secret Scanning (full scan)",
    }
    for step in ordinary:
        assert "--fail" in step["run"]


def test_control_step_reads_the_declared_detector_unverified_on_the_head() -> None:
    (control,) = [s for s in _scanner_steps() if s["name"] == CONTROL_STEP]
    script = " ".join(control["run"].replace("\\\n", " ").split())
    for arg in CONTROL_ARGS:
        assert arg in script
    assert "--fail" in script
    assert "--only-verified" not in script
    assert "if" not in control


def test_control_detector_matches_the_planted_token() -> None:
    assert _detector_regex().search(f"x={_planted_token()}\n")


def test_control_detector_ignores_clean_text_and_its_own_file() -> None:
    pattern = _detector_regex()
    assert not pattern.search("ONEX_SCAN_CONTROL_short")
    assert not pattern.search("a clean line with no token")
    assert not pattern.search(CONTROL_CONFIG.read_text(encoding="utf-8"))
