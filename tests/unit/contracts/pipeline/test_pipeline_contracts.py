"""Tests for all pipeline contracts."""

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.pipeline.contract_artifact_pointer import (
    ContractArtifactPointer,
)
from omnibase_spi.contracts.pipeline.contract_auth_gate_input import (
    ContractAuthGateInput,
)
from omnibase_spi.contracts.pipeline.contract_checkpoint import ContractCheckpoint
from omnibase_spi.contracts.pipeline.contract_execution_context import (
    ContractExecutionContext,
)
from omnibase_spi.contracts.pipeline.contract_hook_invocation import (
    ContractHookInvocation,
)
from omnibase_spi.contracts.pipeline.contract_hook_invocation_result import (
    ContractHookInvocationResult,
)
from omnibase_spi.contracts.pipeline.contract_node_error import ContractNodeError
from omnibase_spi.contracts.pipeline.contract_node_operation_request import (
    ContractNodeOperationRequest,
)
from omnibase_spi.contracts.pipeline.contract_node_operation_result import (
    ContractNodeOperationResult,
)
from omnibase_spi.contracts.pipeline.contract_repo_scope import ContractRepoScope
from omnibase_spi.contracts.pipeline.contract_rrh_result import ContractRRHResult
from omnibase_spi.contracts.pipeline.contract_run_context import ContractRunContext
from omnibase_spi.contracts.pipeline.contract_session_index import ContractSessionIndex
from omnibase_spi.contracts.pipeline.contract_work_authorization import (
    ContractWorkAuthorization,
)
from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult
from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict


@pytest.mark.unit
class TestContractHookInvocation:
    """Tests for ContractHookInvocation."""

    def test_create_minimal(self) -> None:
        inv = ContractHookInvocation(hook_name="PreToolUse", tool_name="Bash")
        assert inv.hook_name == "PreToolUse"
        assert inv.tool_name == "Bash"
        assert inv.schema_version == "1.0"
        assert inv.tool_input == {}
        assert inv.metadata == {}

    def test_frozen(self) -> None:
        inv = ContractHookInvocation(hook_name="PreToolUse", tool_name="Bash")
        with pytest.raises(ValidationError):
            inv.hook_name = "changed"  # type: ignore[misc]

    def test_forward_compat(self) -> None:
        inv = ContractHookInvocation.model_validate(
            {"hook_name": "PreToolUse", "tool_name": "Bash", "new_field": True}
        )
        assert inv.model_extra is not None
        assert inv.model_extra["new_field"] is True

    def test_json_round_trip(self) -> None:
        inv = ContractHookInvocation(
            hook_name="PostToolUse",
            tool_name="Write",
            tool_input={"path": "/tmp/test"},
            session_id="sess-1",
            run_id="run-1",
        )
        j = inv.model_dump_json()
        inv2 = ContractHookInvocation.model_validate_json(j)
        assert inv == inv2


@pytest.mark.unit
class TestContractHookInvocationResult:
    """Tests for ContractHookInvocationResult."""

    def test_create_allow(self) -> None:
        res = ContractHookInvocationResult(decision="allow")
        assert res.decision == "allow"
        assert res.errors == []
        assert res.modified_input is None

    def test_create_block(self) -> None:
        res = ContractHookInvocationResult(
            decision="block",
            reason="Destructive operation not allowed",
            errors=[ContractNodeError(error_code="AUTH-DENIED", message="Blocked")],
        )
        assert res.decision == "block"
        assert len(res.errors) == 1

    def test_create_modify(self) -> None:
        res = ContractHookInvocationResult(
            decision="modify",
            modified_input={"sanitized": True},
        )
        assert res.decision == "modify"
        assert res.modified_input == {"sanitized": True}


@pytest.mark.unit
class TestContractNodeError:
    """Tests for ContractNodeError."""

    def test_create(self) -> None:
        err = ContractNodeError(
            error_code="NODE-TIMEOUT",
            message="Operation timed out after 30s",
            retryable=True,
            details={"timeout_ms": 30000},
        )
        assert err.error_code == "NODE-TIMEOUT"
        assert err.retryable is True
        assert err.details["timeout_ms"] == 30000

    def test_frozen(self) -> None:
        err = ContractNodeError(error_code="X")
        with pytest.raises(ValidationError):
            err.error_code = "Y"  # type: ignore[misc]


@pytest.mark.unit
class TestContractNodeOperationRequest:
    """Tests for ContractNodeOperationRequest."""

    def test_create(self) -> None:
        req = ContractNodeOperationRequest(
            node_id="rrh-preflight",
            operation="execute",
            parameters={"check_ids": ["RRH-1001"]},
        )
        assert req.node_id == "rrh-preflight"
        assert req.operation == "execute"
        assert req.schema_version == "1.0"


@pytest.mark.unit
class TestContractNodeOperationResult:
    """Tests for ContractNodeOperationResult."""

    def test_create_success(self) -> None:
        res = ContractNodeOperationResult(
            node_id="rrh-preflight",
            status="success",
            output={"passed": True},
        )
        assert res.status == "success"
        assert res.errors == []

    def test_create_error(self) -> None:
        res = ContractNodeOperationResult(
            status="error",
            errors=[ContractNodeError(error_code="EXEC-FAIL", message="failed")],
        )
        assert res.status == "error"
        assert len(res.errors) == 1


@pytest.mark.unit
class TestContractRunContext:
    """Tests for ContractRunContext."""

    def test_create(self) -> None:
        ctx = ContractRunContext(
            run_id="run-abc",
            ticket_id="OMN-1234",
            repo="omnibase_spi",
            branch="main",
            phase="implement",
        )
        assert ctx.run_id == "run-abc"
        assert ctx.attempt == 1

    def test_attempt_ge_1(self) -> None:
        with pytest.raises(ValidationError):
            ContractRunContext(run_id="x", attempt=0)


@pytest.mark.unit
class TestContractSessionIndex:
    """Tests for ContractSessionIndex."""

    def test_create(self) -> None:
        idx = ContractSessionIndex(
            session_id="sess-1",
            ticket_id="OMN-2004",
            repo="omnibase_spi",
        )
        assert idx.session_id == "sess-1"
        assert idx.schema_version == "1.0"


@pytest.mark.unit
class TestContractWorkAuthorization:
    """Tests for ContractWorkAuthorization."""

    def test_allow(self) -> None:
        auth = ContractWorkAuthorization(
            decision="allow",
            reason_code="ALLOW_DEFAULT",
        )
        assert auth.decision == "allow"

    def test_deny(self) -> None:
        auth = ContractWorkAuthorization(
            decision="deny",
            reason_code="DENY_CROSS_REPO",
            reason="Cannot modify files outside current repo",
        )
        assert auth.decision == "deny"

    def test_escalate(self) -> None:
        auth = ContractWorkAuthorization(
            decision="escalate",
            reason_code="ESCALATE_HUMAN_REQUIRED",
        )
        assert auth.decision == "escalate"


@pytest.mark.unit
class TestContractExecutionContext:
    """Tests for ContractExecutionContext."""

    def test_create(self) -> None:
        ctx = ContractExecutionContext(
            run_id="run-1",
            skill_name="ticket-work",
            phase="implement",
            permissions=["read", "write"],
        )
        assert ctx.skill_name == "ticket-work"
        assert len(ctx.permissions) == 2


@pytest.mark.unit
class TestContractRRHResult:
    """Tests for ContractRRHResult."""

    def test_create(self) -> None:
        verdict = ContractVerdict(status="PASS", score=95)
        checks = [
            ContractCheckResult(check_id="RRH-1001", domain="rrh", status="pass"),
            ContractCheckResult(check_id="RRH-1201", domain="rrh", status="pass"),
        ]
        rrh = ContractRRHResult(
            run_id="run-1",
            checks=checks,
            verdict=verdict,
            duration_ms=500.0,
        )
        assert len(rrh.checks) == 2
        assert rrh.verdict.status == "PASS"
        assert rrh.duration_ms == 500.0


@pytest.mark.unit
class TestContractCheckpoint:
    """Tests for ContractCheckpoint."""

    def test_create(self) -> None:
        cp = ContractCheckpoint(
            run_id="run-1",
            phase="local_review",
            status="completed",
        )
        assert cp.phase == "local_review"
        assert cp.status == "completed"


@pytest.mark.unit
class TestContractRepoScope:
    """Tests for ContractRepoScope."""

    def test_create(self) -> None:
        scope = ContractRepoScope(
            repo="omnibase_spi",
            path_globs=["src/**/*.py"],
            exclude_globs=["**/test_*.py"],
        )
        assert scope.repo == "omnibase_spi"
        assert len(scope.path_globs) == 1
        assert len(scope.exclude_globs) == 1


@pytest.mark.unit
class TestContractArtifactPointer:
    """Tests for ContractArtifactPointer."""

    def test_create(self) -> None:
        ptr = ContractArtifactPointer(
            artifact_type="pr",
            name="PR #42",
            uri="https://github.com/org/repo/pull/42",
        )
        assert ptr.artifact_type == "pr"
        assert ptr.name == "PR #42"


@pytest.mark.unit
class TestContractAuthGateInput:
    """Tests for ContractAuthGateInput."""

    def test_create(self) -> None:
        gate = ContractAuthGateInput(
            tool_name="Bash",
            operation="execute",
            resource="/etc/hosts",
        )
        assert gate.tool_name == "Bash"
        assert gate.resource == "/etc/hosts"
