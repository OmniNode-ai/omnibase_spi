# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-22198: the lane wire contracts hold the shapes the lane protocols return."""

from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from omnibase_spi.contracts import services as services_contracts
from omnibase_spi.contracts.services import (
    ModelLaneHostPoolReading,
    ModelLaneHostPoolSnapshot,
    ModelLaneHostRef,
    ModelLanePrepareWorktreeRequest,
    ModelLanePrepareWorktreeResult,
    ModelLaneReadEngineExitResult,
    ModelLaneReadLogTailRequest,
    ModelLaneStartEngineRequest,
    ModelLaneStartEngineResult,
    ModelLaneStopEngineRequest,
)

HOST = ModelLaneHostRef(name="h")
SHA = "a" * 40


def _prepare(**overrides: Any) -> ModelLanePrepareWorktreeRequest:
    fields: dict[str, Any] = {
        "host": HOST,
        "lane": "l",
        "run_id": "r",
        "repo": "repo",
        "owner": "owner",
        "sha": SHA,
        "timeout_seconds": 1.0,
    }
    fields.update(overrides)
    return ModelLanePrepareWorktreeRequest(**fields)


def _start(**overrides: Any) -> ModelLaneStartEngineRequest:
    fields: dict[str, Any] = {
        "host": HOST,
        "lane": "l",
        "run_id": "r",
        "workdir": "/w",
        "engine_argv": ("e",),
        "timeout_seconds": 1.0,
    }
    fields.update(overrides)
    return ModelLaneStartEngineRequest(**fields)


@pytest.mark.unit
def test_every_lane_model_is_frozen_and_forbids_extra_fields() -> None:
    lane_models = [n for n in services_contracts.__all__ if n.startswith("ModelLane")]
    # 17 engine and pool models, and 12 provisioning models (OMN-22848).
    assert len(lane_models) == 29
    for name in lane_models:
        model = getattr(services_contracts, name)
        assert issubclass(model, BaseModel)
        assert model.model_config["frozen"] is True, name
        assert model.model_config["extra"] == "forbid", name
        for field_name, field in model.model_fields.items():
            assert field.description, f"{name}.{field_name} has no description"


@pytest.mark.unit
def test_a_host_ref_needs_a_name() -> None:
    with pytest.raises(ValidationError):
        ModelLaneHostRef(name="")


@pytest.mark.unit
@pytest.mark.parametrize("sha", ["abc", "A" * 40, "g" * 40, "a" * 41])
def test_prepare_request_sha_must_be_40_lowercase_hex(sha: str) -> None:
    with pytest.raises(ValidationError):
        _prepare(sha=sha)
    assert _prepare().sha == SHA


@pytest.mark.unit
def test_timeouts_and_graces_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        _prepare(timeout_seconds=0)
    with pytest.raises(ValidationError):
        _start(timeout_seconds=-1)
    with pytest.raises(ValidationError):
        ModelLaneStopEngineRequest(host=HOST, run_id="r", grace_seconds=0)


@pytest.mark.unit
def test_a_prepared_result_needs_a_workdir_and_an_unprepared_one_an_error() -> None:
    with pytest.raises(ValidationError):
        ModelLanePrepareWorktreeResult(prepared=True)
    with pytest.raises(ValidationError):
        ModelLanePrepareWorktreeResult(prepared=False)
    assert ModelLanePrepareWorktreeResult(prepared=True, workdir="/w").workdir == "/w"
    assert ModelLanePrepareWorktreeResult(prepared=False, error="x").error == "x"


@pytest.mark.unit
def test_start_request_needs_a_command() -> None:
    with pytest.raises(ValidationError):
        _start(engine_argv=())


@pytest.mark.unit
def test_start_result_fields_match_the_state() -> None:
    with pytest.raises(ValidationError):
        ModelLaneStartEngineResult(state="started")
    with pytest.raises(ValidationError):
        ModelLaneStartEngineResult(state="started", session_id="s", error="e")
    with pytest.raises(ValidationError):
        ModelLaneStartEngineResult(state="failed")
    with pytest.raises(ValidationError):
        ModelLaneStartEngineResult.model_validate({"state": "maybe"})
    assert (
        ModelLaneStartEngineResult(state="started", session_id="s").state == "started"
    )
    assert ModelLaneStartEngineResult(state="failed", error="e").error == "e"
    assert ModelLaneStartEngineResult(state="unresolved").state == "unresolved"


@pytest.mark.unit
def test_exit_result_is_running_xor_an_exit_code() -> None:
    with pytest.raises(ValidationError):
        ModelLaneReadEngineExitResult(running=True, exit_code=0)
    with pytest.raises(ValidationError):
        ModelLaneReadEngineExitResult(running=False)
    assert ModelLaneReadEngineExitResult(running=True).exit_code is None
    assert ModelLaneReadEngineExitResult(running=False, exit_code=0).exit_code == 0


@pytest.mark.unit
def test_log_offsets_are_not_negative() -> None:
    with pytest.raises(ValidationError):
        ModelLaneReadLogTailRequest(host=HOST, run_id="r", offset=-1)


@pytest.mark.unit
def test_pool_reading_defaults_and_bounds() -> None:
    reading = ModelLaneHostPoolReading(name="h")
    assert reading.placed == 0 and reading.rank_free == 0.0
    assert reading.lane_ready is False and reading.engines == ()
    with pytest.raises(ValidationError):
        ModelLaneHostPoolReading(name="h", placed=-1)
    assert ModelLaneHostPoolReading(name="h", rank_free=None).rank_free is None


@pytest.mark.unit
def test_pool_snapshot_is_frozen_and_empty_by_default() -> None:
    snapshot = ModelLaneHostPoolSnapshot()
    assert snapshot.readings == () and snapshot.launching_venv_hash is None
    with pytest.raises(ValidationError):
        snapshot.__setattr__("limited_hosts", ("h",))


@pytest.mark.unit
def test_a_failed_provisioning_step_must_name_its_error() -> None:
    with pytest.raises(ValidationError):
        services_contracts.ModelLaneHostStepResult(ok=False)
    assert services_contracts.ModelLaneHostStepResult(ok=False, error="x").error == "x"


@pytest.mark.unit
@pytest.mark.parametrize("name", ["", "a/b", "..\\x"])
def test_a_staged_input_name_has_no_path_separator(name: str) -> None:
    with pytest.raises(ValidationError):
        services_contracts.ModelLaneStageInputRequest(
            host=HOST, lane="l", run_id="r", name=name, content="", timeout_seconds=1.0
        )


@pytest.mark.unit
def test_a_staged_input_names_its_path_or_its_error() -> None:
    with pytest.raises(ValidationError):
        services_contracts.ModelLaneStagedInput(staged=True)
    with pytest.raises(ValidationError):
        services_contracts.ModelLaneStagedInput(staged=False)
    with pytest.raises(ValidationError):
        services_contracts.ModelLaneShipPluginTreesResult(shipped=False)
    with pytest.raises(ValidationError):
        services_contracts.ModelLaneRegistryRootResult()
    with pytest.raises(ValidationError):
        services_contracts.ModelLaneRunDirsResult(run_dir="/r")
