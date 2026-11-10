# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-23517: the retain-run-artifacts request model holds the lane's retention shape."""

from typing import Any

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.services import (
    ModelLaneHostRef,
    ModelLaneRetainRunArtifactsRequest,
)

HOST = ModelLaneHostRef(name="h")


def _retain(**overrides: Any) -> ModelLaneRetainRunArtifactsRequest:
    fields = {
        "host": HOST,
        "lane": "l",
        "run_id": "r",
        "lab_work_root": "/lab-run",
        "receipt_json": "{}",
        "timeout_seconds": 1.0,
    }
    fields.update(overrides)
    return ModelLaneRetainRunArtifactsRequest(**fields)


@pytest.mark.unit
def test_a_valid_request_builds_and_is_frozen() -> None:
    request = _retain()
    assert request.lane == "l" and request.run_id == "r"
    assert request.lab_work_root == "/lab-run" and request.receipt_json == "{}"
    with pytest.raises(ValidationError):
        request.lane = "other"


@pytest.mark.unit
def test_an_empty_lane_is_refused() -> None:
    with pytest.raises(ValidationError):
        _retain(lane="")


@pytest.mark.unit
def test_keep_days_zero_is_refused() -> None:
    with pytest.raises(ValidationError):
        _retain(keep_days=0)


@pytest.mark.unit
def test_timeout_seconds_zero_is_refused() -> None:
    with pytest.raises(ValidationError):
        _retain(timeout_seconds=0)


@pytest.mark.unit
def test_an_extra_field_is_refused() -> None:
    with pytest.raises(ValidationError):
        _retain(bogus=1)


@pytest.mark.unit
def test_the_defaults_are_keep_days_seven_and_delete_false() -> None:
    request = _retain()
    assert request.keep_days == 7
    assert request.delete is False
