# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Production loader for SPI default handler contract YAML templates (OMN-9755)."""

from __future__ import annotations

from pathlib import Path

import yaml

from omnibase_core.models.contracts.model_handler_contract import ModelHandlerContract
from omnibase_spi.exceptions import TemplateNotFoundError, TemplateParseError

_DEFAULTS_DIR = Path(__file__).parent.parent / "contracts" / "defaults"


def load_default_handler_contract(template_name: str) -> ModelHandlerContract:
    """Load and validate a default handler contract template.

    Args:
        template_name: Filename of the YAML template (e.g. "default_effect_handler.yaml").

    Returns:
        Validated ModelHandlerContract instance.

    Raises:
        TemplateNotFoundError: If the template file does not exist.
        TemplateParseError: If the file contains invalid YAML.
    """
    path = _DEFAULTS_DIR / template_name
    if not path.exists():
        raise TemplateNotFoundError(
            f"Template not found: {template_name}",
            context={"template_name": template_name, "search_dir": str(_DEFAULTS_DIR)},
        )
    try:
        with path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise TemplateParseError(
            f"Invalid YAML in template: {template_name}",
            context={"template_name": template_name, "yaml_error": str(exc)},
        ) from exc
    return ModelHandlerContract.model_validate(raw)
