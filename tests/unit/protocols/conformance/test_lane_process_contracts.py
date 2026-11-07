# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-22851: the lane process wire contracts hold the shapes the runner protocol returns."""

from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from omnibase_spi.contracts import services as services_contracts
from omnibase_spi.contracts.services import (
    ModelLaneProcessRunResult,
    ModelLaneProcessStartResult,
    ModelLaneStartSpec,
)


def _spec(**overrides: Any) -> ModelLaneStartSpec:
    fields: dict[str, Any] = {
        "argv": ("run",),
        "working_directory": "/w",
        "lane": "l",
    }
    fields.update(overrides)
    return ModelLaneStartSpec(**fields)


@pytest.mark.unit
@pytest.mark.parametrize(
    "overrides",
    [{"argv": ()}, {"working_directory": ""}, {"lane": ""}],
)
def test_a_spec_needs_an_argv_a_working_directory_and_a_lane(
    overrides: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError):
        _spec(**overrides)


@pytest.mark.unit
def test_a_spec_carries_no_log_path() -> None:
    with pytest.raises(ValidationError):
        _spec(log_path="/x.log")


@pytest.mark.unit
def test_start_result_shapes() -> None:
    assert ModelLaneProcessStartResult(state="started", pid=3).pid == 3
    assert ModelLaneProcessStartResult(state="failed", cause="x").cause == "x"
    for bad in (
        {"state": "started"},
        {"state": "started", "pid": 3, "cause": "x"},
        {"state": "failed"},
        {"state": "failed", "cause": "x", "pid": 3},
        {"state": "started", "pid": 0},
    ):
        with pytest.raises(ValidationError):
            ModelLaneProcessStartResult(**bad)


@pytest.mark.unit
def test_run_result_shapes() -> None:
    assert (
        ModelLaneProcessRunResult(state="exited", exit_code=0, stdout="o").stdout == "o"
    )
    assert ModelLaneProcessRunResult(state="timed_out").exit_code is None
    assert ModelLaneProcessRunResult(state="failed", cause="x").cause == "x"
    for bad in (
        {"state": "exited"},
        {"state": "exited", "exit_code": 0, "cause": "x"},
        {"state": "timed_out", "exit_code": 1},
        {"state": "timed_out", "stdout": "o"},
        {"state": "failed"},
        {"state": "failed", "cause": "x", "exit_code": 1},
    ):
        with pytest.raises(ValidationError):
            ModelLaneProcessRunResult(**bad)


@pytest.mark.unit
def test_the_models_are_frozen_and_exported() -> None:
    for name in (
        "ModelLaneStartSpec",
        "ModelLaneProcessStartResult",
        "ModelLaneProcessRunResult",
    ):
        model = getattr(services_contracts, name)
        assert issubclass(model, BaseModel)
        assert model.model_config["frozen"] is True
        assert model.model_config["extra"] == "forbid"
        assert name in services_contracts.__all__
