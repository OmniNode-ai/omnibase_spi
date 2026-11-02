# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-21351: SPI no longer carries Dependabot version-update configuration."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("filename", ["dependabot.yml", "dependabot.yaml"])
def test_no_dependabot_version_updates(filename: str) -> None:
    config = REPO_ROOT / ".github" / filename
    assert not config.exists(), (
        f"Dependabot version-update configuration remains: {config.relative_to(REPO_ROOT)}"
    )
