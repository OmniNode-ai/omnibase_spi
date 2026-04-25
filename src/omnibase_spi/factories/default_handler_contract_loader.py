# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Production loader for SPI default handler contract YAML templates (OMN-9755)."""

from __future__ import annotations

from pathlib import Path

import yaml

from omnibase_core.models.contracts.model_handler_contract import ModelHandlerContract
from omnibase_spi.exceptions import TemplateNotFoundError, TemplateParseError

_DEFAULTS_DIR = Path(__file__).parent.parent / "contracts" / "defaults"


def _resolve_template_path(template_name: str) -> Path:
    """Resolve template_name to an absolute path confined to _DEFAULTS_DIR.

    Raises TemplateNotFoundError for any name that would escape the defaults
    directory (absolute paths, '..' traversal, or non-existent files).
    """
    # Reject names that are absolute or contain path separators — only bare
    # filenames are valid (e.g. "default_effect_handler.yaml").
    if Path(template_name).parts != (template_name,):
        raise TemplateNotFoundError(
            f"Invalid template name: {template_name!r}",
            context={"template_name": template_name},
        )
    candidate = (_DEFAULTS_DIR / template_name).resolve()
    # Confirm the resolved path is still inside _DEFAULTS_DIR (guards symlinks).
    if not candidate.is_relative_to(_DEFAULTS_DIR.resolve()):
        raise TemplateNotFoundError(
            f"Template not found: {template_name!r}",
            context={"template_name": template_name},
        )
    return candidate


def load_default_handler_contract(template_name: str) -> ModelHandlerContract:
    """Load and validate a default handler contract template.

    Args:
        template_name: Bare filename of the YAML template
            (e.g. "default_effect_handler.yaml"). Absolute paths and
            directory traversal sequences are rejected.

    Returns:
        Validated ModelHandlerContract instance.

    Raises:
        TemplateNotFoundError: If the template name is invalid or the file
            does not exist within the defaults directory.
        TemplateParseError: If the file contains invalid YAML.
    """
    path = _resolve_template_path(template_name)
    if not path.exists():
        raise TemplateNotFoundError(
            f"Template not found: {template_name!r}",
            context={"template_name": template_name},
        )
    try:
        with path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise TemplateParseError(
            f"Invalid YAML in template: {template_name!r}",
            context={"template_name": template_name},
        ) from exc
    return ModelHandlerContract.model_validate(raw)
