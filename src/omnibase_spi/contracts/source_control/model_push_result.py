# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""ModelPushResult -- wire-format contract for the outcome of a leased push.

Returned by ProtocolGitRemote.push_with_lease. This module MUST NOT import from
omnibase_core, omnibase_infra, or omniclaude.
"""

from typing import Self

from pydantic import BaseModel, Field, model_validator


class ModelPushResult(BaseModel):
    """Outcome of one push guarded by an expected remote head.

    Attributes:
        pushed: True when the remote ref now points at the pushed sha.
        cause: Why the remote refused; required when ``pushed`` is False.
        remote_head: The remote ref's sha after the call, None when it does not exist.
    """

    model_config = {"frozen": True, "extra": "forbid"}

    pushed: bool = Field(..., description="True when the push was accepted.")
    cause: str | None = Field(default=None, description="Refusal cause.")
    remote_head: str | None = Field(
        default=None, description="The remote ref's sha after the call."
    )

    @model_validator(mode="after")
    def _cause_matches_pushed(self) -> Self:
        if self.pushed and self.cause is not None:
            raise ValueError("an accepted push carries no cause")
        if not self.pushed and not self.cause:
            raise ValueError("a refused push names its cause")
        return self


__all__ = ["ModelPushResult"]
