# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""The test splits name the interpreter they compare signatures under (OMN-22812).

``tests/test_protocol_snapshot.py`` compares the *reprs* of protocol
annotations, and those reprs are not stable across Python versions: 3.14 renders
``uuid.UUID`` as ``UUID``, ``...`` as ``Ellipsis``, ``Callable[[], X]`` as
``Callable[X]`` and a ``Literal``'s members unquoted. The ``test-parallel`` job
named no interpreter, so uv resolved the newest one satisfying
``requires-python = ">=3.12"``; when ``ubuntu-latest`` became Ubuntu 26.04 on
2026-11-06 that became 3.14 and the snapshot reported 125 signature drifts that
were no such thing.

These tests fail on a tree where that step names no version, which is what the
merge base looks like.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
#: The interpreter the rest of this workflow already names through actions/setup-python.
EXPECTED = "3.12"


def _workflow() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _split_job() -> dict[str, Any]:
    jobs = _workflow()["jobs"]
    named = [
        job
        for job in jobs.values()
        if isinstance(job, dict) and "Tests (Split" in str(job.get("name", ""))
    ]
    assert len(named) == 1, f"expected one Tests (Split) job, found {len(named)}"
    return named[0]


def _uv_steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        step
        for step in job["steps"]
        if isinstance(step, dict) and "astral-sh/setup-uv" in str(step.get("uses", ""))
    ]


def test_the_split_job_pins_the_interpreter_uv_would_otherwise_choose() -> None:
    """Without this, uv takes the newest Python the image offers."""
    steps = _uv_steps(_split_job())
    assert steps, "the Tests (Split) job sets up no uv"
    for step in steps:
        with_ = step.get("with") or {}
        assert str(with_.get("python-version", "")) == EXPECTED, (
            "the Tests (Split) job's uv setup names no python-version, so the "
            "protocol snapshot is compared under whichever interpreter the "
            "runner image happens to offer"
        )


def test_the_pin_is_the_version_the_other_jobs_name() -> None:
    """A pin that disagreed with the rest of the workflow would be a new choice
    rather than a restoration of the measured environment.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert (
        f"python-version: '{EXPECTED}'" in text
        or f'python-version: "{EXPECTED}"' in text
    )
