# SPDX-FileCopyrightText: 2026 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Runtime and layering guarantees for the model-swap validation SPI."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import get_type_hints

from omnibase_core.models.model_swap_validation import (
    ModelModelSwapValidationRequest,
    ModelModelSwapValidationResult,
)
from omnibase_spi.protocols.validation import (
    ProtocolModelSwapValidator,
    protocol_model_swap_validator as module,
)


class _Validator:
    @property
    def validator_id(self) -> str:
        return "example-validator@pinned-version"

    async def validate(
        self, request: ModelModelSwapValidationRequest
    ) -> ModelModelSwapValidationResult:
        raise AssertionError("runtime protocol check must not invoke validation")


class _MissingValidate:
    @property
    def validator_id(self) -> str:
        return "example-validator@pinned-version"


class _MissingIdentifier:
    async def validate(
        self, request: ModelModelSwapValidationRequest
    ) -> ModelModelSwapValidationResult:
        raise AssertionError("runtime protocol check must not invoke validation")


def test_runtime_check_requires_both_validator_members() -> None:
    assert isinstance(_Validator(), ProtocolModelSwapValidator)
    assert not isinstance(_MissingValidate(), ProtocolModelSwapValidator)
    assert not isinstance(_MissingIdentifier(), ProtocolModelSwapValidator)
    assert not isinstance(object(), ProtocolModelSwapValidator)


def test_signature_uses_only_canonical_core_models() -> None:
    hints = get_type_hints(ProtocolModelSwapValidator.validate)
    assert hints == {
        "request": ModelModelSwapValidationRequest,
        "return": ModelModelSwapValidationResult,
    }
    assert inspect.iscoroutinefunction(ProtocolModelSwapValidator.validate)
    descriptor = inspect.getattr_static(ProtocolModelSwapValidator, "validator_id")
    assert isinstance(descriptor, property)
    assert descriptor.fset is None


def test_protocol_has_no_implementation_layer_imports() -> None:
    tree = ast.parse(Path(module.__file__).read_text())
    modules = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert modules == {"typing", "omnibase_core.models.model_swap_validation"}
    assert not any(isinstance(node, ast.Import) for node in ast.walk(tree))
