# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-21522: the canonical-file-shape node entry refuses the two ratchet canaries."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/ci.yml"
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"
BURNDOWN = ROOT / ".onex_ratchets/canonical_file_shape_burndown_baseline.txt"
ENTRY = (
    "omnibase_core.nodes.node_canonical_file_shape_check_compute"
    ".runtime_canonical_file_shape_check"
)
CORE_REPO = "https://github.com/OmniNode-ai/omnibase_core"


def _core_reference() -> str:
    loaded: dict[Any, Any] = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    reference = loaded["jobs"]["canonical-file-shape"]["env"][
        "CANONICAL_FILE_SHAPE_CORE"
    ]
    assert isinstance(reference, str)
    return reference


def _git(repo: Path, *args: str) -> str:
    git = shutil.which("git")
    assert git is not None
    done = subprocess.run(
        [
            git,
            "-c",
            "user.email=canary@example.invalid",
            "-c",
            "user.name=canary",
            *args,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout.strip()


def _ratchet(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    uv = shutil.which("uv")
    assert uv is not None
    return subprocess.run(
        [
            uv,
            "run",
            "--no-project",
            "--with",
            _core_reference(),
            "python",
            "-m",
            ENTRY,
            "--rules",
            "file-shape",
            *args,
        ],
        cwd=repo,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )


@pytest.fixture
def base_repo(tmp_path: Path) -> tuple[Path, str]:
    """A repository whose only refused file is the baselined scripts/old_a.py."""
    _git(tmp_path, "init", "--quiet")
    (tmp_path / ".onex_ratchets").mkdir()
    (tmp_path / ".onex_ratchets/canonical_file_shape_baseline.txt").write_text(
        "# canonical-file-shape baseline. Shrink-only.\nscripts/old_a.py\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/old_a.py").write_text("A = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "--quiet", "-m", "base")
    return tmp_path, _git(tmp_path, "rev-parse", "HEAD")


def test_clean_base_is_accepted(base_repo: tuple[Path, str]) -> None:
    repo, _ = base_repo
    result = _ratchet(repo, "--head", "HEAD")
    assert result.returncode == 0, result.stdout + result.stderr


def test_new_unbound_handler_is_refused(base_repo: tuple[Path, str]) -> None:
    repo, base = base_repo
    handler = repo / "src/canary_pkg/protocols/handler_canary.py"
    handler.parent.mkdir(parents=True)
    handler.write_text("def handle(request):\n    return request\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "--quiet", "-m", "plant an unbound handler")
    result = _ratchet(repo, "--base", base, "--head", "HEAD")
    assert result.returncode != 0
    assert "handler_canary.py: [handler_outside_node]" in result.stdout + result.stderr


def test_baseline_line_for_an_existing_refused_file_is_refused(
    base_repo: tuple[Path, str],
) -> None:
    repo, _ = base_repo
    (repo / "scripts/old_b.py").write_text("B = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "--quiet", "-m", "an existing refused file")
    existing = _git(repo, "rev-parse", "HEAD")
    baseline = repo / ".onex_ratchets/canonical_file_shape_baseline.txt"
    baseline.write_text(
        baseline.read_text(encoding="utf-8") + "scripts/old_b.py\n", encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "--quiet", "-m", "baseline the refused file")
    result = _ratchet(repo, "--base", existing, "--head", "HEAD")
    assert result.returncode != 0
    assert "[baseline-growth] entry 'scripts/old_b.py' is new" in (
        result.stdout + result.stderr
    )


def test_burndown_baseline_names_this_ticket() -> None:
    lines = BURNDOWN.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# Burn-down ticket: OMN-21522"


def test_precommit_hook_rev_equals_the_ci_dev_merge_tag() -> None:
    config = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
    revs = {
        repo["rev"]
        for repo in config["repos"]
        if repo["repo"] == CORE_REPO
        and any(hook["id"] == "canonical-file-shape" for hook in repo["hooks"])
    }
    assert revs == {_core_reference().rsplit("@", 1)[1]}
