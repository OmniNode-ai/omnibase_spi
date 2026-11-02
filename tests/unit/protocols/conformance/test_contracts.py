# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-22185: the host-call and push-result wire contracts hold their three-kind shape."""

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.services import ModelHostCallAnswer, ModelHostCallRequest
from omnibase_spi.contracts.source_control import ModelPushResult


@pytest.mark.unit
def test_a_refused_answer_must_name_its_cause() -> None:
    with pytest.raises(ValidationError):
        ModelHostCallAnswer(request_id="r", outcome="refused")
    ok = ModelHostCallAnswer(request_id="r", outcome="refused", cause="held")
    assert ok.cause == "held"


@pytest.mark.unit
@pytest.mark.parametrize("outcome", ["ok", "unknown"])
def test_only_a_refused_answer_carries_a_cause(outcome: str) -> None:
    with pytest.raises(ValidationError):
        ModelHostCallAnswer.model_validate(
            {"request_id": "r", "outcome": outcome, "cause": "x"}
        )
    answer = ModelHostCallAnswer.model_validate({"request_id": "r", "outcome": outcome})
    assert answer.cause is None


@pytest.mark.unit
def test_an_answer_outcome_is_one_of_three() -> None:
    with pytest.raises(ValidationError):
        ModelHostCallAnswer.model_validate({"request_id": "r", "outcome": "maybe"})


@pytest.mark.unit
def test_a_request_needs_an_id_and_an_operation() -> None:
    with pytest.raises(ValidationError):
        ModelHostCallRequest(request_id="", operation="status")
    with pytest.raises(ValidationError):
        ModelHostCallRequest(request_id="r", operation="")


@pytest.mark.unit
def test_a_refused_push_names_its_cause_and_an_accepted_one_has_none() -> None:
    with pytest.raises(ValidationError):
        ModelPushResult(pushed=False)
    with pytest.raises(ValidationError):
        ModelPushResult(pushed=True, cause="x")
    assert ModelPushResult(pushed=False, cause="lease-stale").pushed is False
