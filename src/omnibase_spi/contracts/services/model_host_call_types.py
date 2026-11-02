# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Host-call wire-format contracts for ProtocolHostCall: one typed request, one typed answer.

The request carries ids, hashes and names only, never a value. The answer is one of
three kinds: ``ok``, ``refused`` (with a cause) or ``unknown`` (no answer within the
timeout, so the caller cannot say whether the host acted). This module MUST NOT
import from omnibase_core, omnibase_infra, or omniclaude.
"""

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


class ModelHostCallRequest(BaseModel):
    """One typed request to a host.

    Attributes:
        request_id: Caller-chosen id; the answer repeats it.
        operation: Name of the host operation, such as ``offer`` or ``status``.
        fields: Operation arguments as ids, hashes and names.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    request_id: str = Field(..., min_length=1, description="Caller-chosen id.")
    operation: str = Field(..., min_length=1, description="Host operation name.")
    fields: dict[str, str] = Field(
        default_factory=dict,
        description="Operation arguments as ids, hashes and names.",
    )


class ModelHostCallAnswer(BaseModel):
    """The typed answer to a ModelHostCallRequest.

    Attributes:
        request_id: The id of the request this answers.
        outcome: ``ok``, ``refused`` or ``unknown``.
        cause: The refusal cause; required for ``refused``, absent otherwise.
        fields: Result values as ids, hashes and names.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    request_id: str = Field(..., min_length=1, description="Id of the request.")
    outcome: Literal["ok", "refused", "unknown"] = Field(
        ..., description="ok, refused(cause) or unknown."
    )
    cause: str | None = Field(default=None, description="Refusal cause.")
    fields: dict[str, str] = Field(
        default_factory=dict, description="Result values as ids, hashes and names."
    )

    @model_validator(mode="after")
    def _cause_matches_outcome(self) -> Self:
        if self.outcome == "refused" and not self.cause:
            raise ValueError("a refused answer names its cause")
        if self.outcome != "refused" and self.cause is not None:
            raise ValueError("only a refused answer carries a cause")
        return self


__all__ = ["ModelHostCallAnswer", "ModelHostCallRequest"]
