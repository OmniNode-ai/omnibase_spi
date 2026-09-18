# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""A release's two halves must be separately retryable (OMN-17272).

Publishing is irreversible; moving `main` to the tag's commit is idempotent.
Release run 35304497808 did the first and then failed the second, and the
workflow offered no way to retry only the second -- re-dispatching it would
have re-uploaded artifacts the index already holds. So `0.23.4` sat published
with `main` unmoved, and the recovery needed a code change rather than a
dispatch.

`sync_only` is that entry point. These tests are asserted over the PARSED
workflow rather than over a diff, so a later edit that drops a guard, or that
guards a step it must not, fails here instead of passing review unnoticed.

The second test is the one that matters most, and it is a positive control:
a guard added to the mint, sync or readback steps would make a sync-only run
do nothing at all while still reporting success -- the precise failure this
change exists to remove.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"

# The steps a sync-only run must NOT execute. Each publishes something, and
# every one of them is non-idempotent against an already-released tag.
PUBLISHING_STEPS = (
    "astral-sh/setup-uv@v7",
    "Build wheel + sdist",
    "Verify dist artifacts exist",
    "Verify PyPI dependency-pin resolvability (OMN-14070)",
    "Publish to PyPI",
    "Generate checksums",
    "Create GitHub Release",
)

# The steps a sync-only run exists to execute. A sync-only guard on any of
# these is the bug, not the fix.
POINTER_STEPS = (
    "Mint onexbot-occ-writer app token",
    "Sync main to release tag",
    "Read the pointer back",
)

pytestmark = pytest.mark.unit


def _workflow() -> dict[Any, Any]:
    assert WORKFLOW.is_file(), f"release workflow is missing at {WORKFLOW}"
    doc: dict[Any, Any] = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(doc, dict), f"unreadable workflow: {doc!r}"
    return doc


def _steps() -> list[dict[Any, Any]]:
    steps = _workflow()["jobs"]["release"]["steps"]
    assert isinstance(steps, list) and steps, f"unreadable step list: {steps!r}"
    return [s for s in steps if isinstance(s, dict)]


def _label(step: dict[Any, Any]) -> str:
    return str(step.get("name") or step.get("uses") or "")


def _dispatch_inputs() -> dict[Any, Any]:
    """The workflow's dispatch inputs.

    YAML 1.1 reads a bare ``on`` as the boolean ``True``, so the trigger block
    is looked up under both spellings rather than under the one that happens to
    win on this parser version.
    """
    doc = _workflow()
    triggers = doc.get("on", doc.get(True))
    assert isinstance(triggers, dict), f"unreadable trigger block: {triggers!r}"
    dispatch = triggers.get("workflow_dispatch")
    assert isinstance(dispatch, dict), f"no workflow_dispatch trigger: {dispatch!r}"
    inputs = dispatch.get("inputs")
    assert isinstance(inputs, dict), f"the dispatch declares no inputs: {inputs!r}"
    return inputs


def test_sync_only_is_a_boolean_input_defaulting_to_off() -> None:
    """Default-off, so every dispatch that exists today is unchanged."""
    inputs = _dispatch_inputs()
    assert "sync_only" in inputs, (
        "release.yml declares no sync_only input, so a tag whose publish "
        "succeeded and whose main sync failed has no recovery path that "
        "avoids re-uploading already-published artifacts (OMN-17272)"
    )
    sync_only = inputs["sync_only"]
    assert sync_only.get("type") == "boolean", (
        f"sync_only must be a boolean input, not {sync_only.get('type')!r}"
    )
    assert sync_only.get("default") is False, (
        f"sync_only must default to false, not {sync_only.get('default')!r}; "
        "a default-on flag would silently stop publishing releases"
    )


def test_the_tag_input_is_still_required() -> None:
    """A sync-only run resolves the commit FROM the tag, so it cannot be absent."""
    tag = _dispatch_inputs().get("tag")
    assert isinstance(tag, dict), f"the dispatch declares no tag input: {tag!r}"
    assert tag.get("required") is True, (
        "the tag input must stay required: both the publishing path and the "
        "sync-only path resolve the target commit from it"
    )


def test_every_publishing_step_is_guarded_by_sync_only() -> None:
    by_label = {_label(s): s for s in _steps()}
    for label in PUBLISHING_STEPS:
        assert label in by_label, f"expected a step {label!r} in the release job"
        condition = str(by_label[label].get("if") or "")
        assert "inputs.sync_only" in condition, (
            f"step {label!r} carries no sync_only guard (if: {condition!r}), so "
            "a sync-only run would publish again; publishing is the "
            "irreversible half and must never be retried by a pointer repair"
        )


def test_the_pointer_steps_are_never_guarded_by_sync_only() -> None:
    """Positive control: the steps a sync-only run exists to execute must run.

    Without this, the previous test passes just as well over a workflow that
    guards EVERY step -- a sync-only run that does nothing and reports success.
    """
    by_label = {_label(s): s for s in _steps()}
    for label in POINTER_STEPS:
        assert label in by_label, f"expected a step {label!r} in the release job"
        condition = str(by_label[label].get("if") or "")
        assert "sync_only" not in condition, (
            f"step {label!r} is guarded by sync_only (if: {condition!r}); a "
            "sync-only run would then skip the very work it was dispatched "
            "to do, and still report success"
        )


def test_the_readback_is_the_terminal_step() -> None:
    """The proof cannot be skipped, reordered away, or left non-terminal.

    A sync that reports success without reading the pointer back cannot tell a
    moved ref from an accepted request, which is the silent form of this same
    failure (OMN-16343).
    """
    labels = [_label(s) for s in _steps()]
    assert labels[-1] == "Read the pointer back", (
        f"the last step of the release job is {labels[-1]!r}, not the "
        "readback; the readback must remain terminal so no step can report "
        "a release complete after it"
    )
