# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Public boundary for an evidence-only model-swap validation implementation."""

from typing import Protocol, runtime_checkable

from omnibase_core.models.model_swap_validation import (
    ModelModelSwapValidationRequest,
    ModelModelSwapValidationResult,
)


@runtime_checkable
class ProtocolModelSwapValidator(Protocol):
    """Validate candidate-model evidence without making a routing decision."""

    @property
    def validator_id(self) -> str:
        """Identify the implementation and its pinned version."""
        ...

    async def validate(
        self, request: ModelModelSwapValidationRequest
    ) -> ModelModelSwapValidationResult:
        """Return evidence or a typed terminal failure for the request."""
        ...


__all__ = ["ProtocolModelSwapValidator"]
