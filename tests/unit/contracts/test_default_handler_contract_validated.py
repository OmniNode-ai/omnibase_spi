# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for the production SPI default handler contract loader (OMN-9755).

Verifies that load_default_handler_contract() returns ModelHandlerContract
instances (not raw dicts) for all default YAML templates.
"""

from __future__ import annotations

import pytest

from omnibase_core.models.contracts.model_handler_contract import ModelHandlerContract
from omnibase_spi.exceptions import TemplateNotFoundError
from omnibase_spi.factories.default_handler_contract_loader import (
    load_default_handler_contract,
)


@pytest.mark.unit
class TestDefaultHandlerContractLoader:
    def test_default_effect_contract_is_typed(self) -> None:
        contract = load_default_handler_contract("default_effect_handler.yaml")
        assert isinstance(contract, ModelHandlerContract)

    def test_default_compute_contract_is_typed(self) -> None:
        contract = load_default_handler_contract("default_compute_handler.yaml")
        assert isinstance(contract, ModelHandlerContract)

    def test_default_nondeterministic_compute_contract_is_typed(self) -> None:
        contract = load_default_handler_contract(
            "default_nondeterministic_compute_handler.yaml"
        )
        assert isinstance(contract, ModelHandlerContract)

    def test_missing_template_raises_template_not_found_error(self) -> None:
        with pytest.raises(TemplateNotFoundError):
            load_default_handler_contract("nonexistent_template.yaml")

    def test_effect_contract_has_expected_handler_id(self) -> None:
        contract = load_default_handler_contract("default_effect_handler.yaml")
        assert contract.handler_id == "template.effect.default"

    def test_compute_contract_has_expected_handler_id(self) -> None:
        contract = load_default_handler_contract("default_compute_handler.yaml")
        assert contract.handler_id == "template.compute.default"
