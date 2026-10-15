# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-20074: the references to onex_change_control that nothing needs are gone.

After the S6 cut-over (no workflow calls or checks out onex_change_control, see
``test_no_occ_callers_omn20074``) a few files still named the retired
change-control repository as a live part of this repository's process:

* ``architecture-handshakes/validator-requirements.yaml`` listed it as a known
  repository and as a target of two validators, and named it as the central
  source of no-hardcoded-topics and no-untracked-todos, which this repository
  takes from omnibase_core. The edits mirror omnibase_core's canonical spec.
* ``CLAUDE.md`` said it holds this repository's evidence and receipts; the
  evidence is ``contracts/<OMN-N>.yaml`` here, checked by
  ``repo-evidence / dod-verify``.
* the skip-token hook's remediation told the author to push an OCC contract
  and receipts.
* the dep-provenance gate described an onex-change-control git pin as the
  legitimate state; pyproject.toml has carried no such dependency since S8.
  The gate's behaviour is unchanged: it never special-cased that package.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
_OCC = "onex_change_control"
_OCC_DIST = "onex-change-control"

_SPEC = REPO_ROOT / "architecture-handshakes/validator-requirements.yaml"
_SKIP_HOOK = REPO_ROOT / ".pre-commit-hooks/reject-deploy-gate-skip-token.sh"
_DEP_PROVENANCE_FILES = (
    "scripts/check_dep_provenance.py",
    ".github/workflows/dep-provenance-gate.yml",
    "tests/scripts/test_check_dep_provenance.py",
)


def _strings_naming_occ(node: object) -> list[str]:
    if isinstance(node, str):
        return [node] if _OCC in node else []
    if isinstance(node, dict):
        return [hit for v in node.values() for hit in _strings_naming_occ(v)]
    if isinstance(node, list):
        return [hit for v in node for hit in _strings_naming_occ(v)]
    return []


def test_occ_string_walk_has_a_positive_control() -> None:
    planted = {
        "known_repos": ["omnibase_spi", _OCC],
        "v": {"central_source": f"{_OCC} (centralized)"},
    }
    assert len(_strings_naming_occ(planted)) == 2


def test_validator_requirements_spec_names_no_change_control_repo() -> None:
    spec = yaml.safe_load(_SPEC.read_text(encoding="utf-8"))
    assert "omnibase_spi" in spec["known_repos"]
    assert _strings_naming_occ(spec) == []


def test_validator_requirements_central_sources_are_omnibase_core() -> None:
    validators = yaml.safe_load(_SPEC.read_text(encoding="utf-8"))[
        "required_validators"
    ]
    assert (
        validators["no-hardcoded-topics"]["central_source"]
        == "omnibase_core.handlers.handler_no_hardcoded_topics"
    )
    assert (
        validators["no-untracked-todos"]["central_source"]
        == "omnibase_core.handlers.handler_todo_format"
    )


def test_claude_md_places_evidence_in_this_repository() -> None:
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert _OCC not in text
    assert "repo-evidence / dod-verify" in text


def test_skip_token_hook_remediation_names_repo_owned_evidence() -> None:
    text = _SKIP_HOOK.read_text(encoding="utf-8")
    assert "OCC contract" not in text
    assert "contracts/<OMN-N>.yaml" in text


@pytest.mark.parametrize("rel", _DEP_PROVENANCE_FILES)
def test_dep_provenance_gate_describes_no_change_control_pin(rel: str) -> None:
    text = (REPO_ROOT / rel).read_text(encoding="utf-8")
    assert _OCC_DIST not in text
    assert _OCC not in text


def test_pyproject_declares_no_change_control_dependency() -> None:
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert _OCC_DIST not in text
    assert _OCC not in text
