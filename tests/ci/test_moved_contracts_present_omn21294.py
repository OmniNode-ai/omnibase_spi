# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-21294: the ticket contracts moved from onex_change_control live in contracts/.

Each moved contract must exist at ``contracts/<id>.yaml``, load as a mapping with
``yaml.safe_load``, name its own ticket id, load through omnibase_core's strict
loader (no duplicate mapping key, as dod-verify reads it) and pass omnibase_core's
``ModelTicketContract``, the model the ``contract-validation`` workflow runs.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from omnibase_core.models.ticket.model_ticket_contract import ModelTicketContract
from omnibase_core.utils.util_safe_yaml_loader import load_yaml_mapping_no_duplicates

pytestmark = pytest.mark.unit

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"

MOVED_TICKET_IDS = ["OMN-14160"]


@pytest.mark.parametrize("ticket_id", MOVED_TICKET_IDS)
def test_moved_contract_is_present_and_names_its_ticket(ticket_id: str) -> None:
    path = CONTRACTS / f"{ticket_id}.yaml"
    assert path.is_file(), f"missing moved contract {path.name}"
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict), f"{path.name} does not load as a mapping"
    assert data.get("ticket_id") == ticket_id
    load_yaml_mapping_no_duplicates(text, source=path.name)
    assert ModelTicketContract.from_yaml(text).ticket_id == ticket_id
