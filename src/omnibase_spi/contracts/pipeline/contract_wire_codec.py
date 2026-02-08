"""Canonical JSON/YAML serialization helpers for pipeline contracts.

Provides deterministic serialization and deserialization for all
Contract* models.  Deterministic means: sorted keys, consistent
formatting, and stable output for the same input.

This module must NOT import from omnibase_core, omnibase_infra, or omniclaude.
"""

from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# YAML is optional -- only used if pyyaml is installed
try:
    import yaml

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def to_json(model: BaseModel, *, indent: int = 2) -> str:
    """Serialize a contract model to canonical JSON.

    Keys are sorted for deterministic output.

    Args:
        model: A Pydantic BaseModel instance.
        indent: Number of spaces for indentation (default 2).

    Returns:
        A JSON string with sorted keys.
    """
    raw = model.model_dump(mode="json")
    return json.dumps(raw, sort_keys=True, indent=indent, ensure_ascii=False)


def from_json(json_str: str, model_class: type[T]) -> T:
    """Deserialize a contract model from JSON.

    Unknown fields are tolerated (extra='allow' on models).

    Args:
        json_str: A JSON string.
        model_class: The target Pydantic model class.

    Returns:
        An instance of model_class.
    """
    data = json.loads(json_str)
    return model_class.model_validate(data)


def to_yaml(model: BaseModel) -> str:
    """Serialize a contract model to canonical YAML.

    Requires PyYAML to be installed.

    Args:
        model: A Pydantic BaseModel instance.

    Returns:
        A YAML string with default flow style disabled.

    Raises:
        ImportError: If PyYAML is not installed.
    """
    if not _HAS_YAML:
        raise ImportError(
            "PyYAML is required for YAML serialization. "
            "Install it with: pip install pyyaml"
        )
    raw = model.model_dump(mode="json")
    return yaml.dump(  # type: ignore[no-any-return]
        raw,
        default_flow_style=False,
        sort_keys=True,
        allow_unicode=True,
    )


def from_yaml(yaml_str: str, model_class: type[T]) -> T:
    """Deserialize a contract model from YAML.

    Unknown fields are tolerated (extra='allow' on models).

    Requires PyYAML to be installed.

    Args:
        yaml_str: A YAML string.
        model_class: The target Pydantic model class.

    Returns:
        An instance of model_class.

    Raises:
        ImportError: If PyYAML is not installed.
    """
    if not _HAS_YAML:
        raise ImportError(
            "PyYAML is required for YAML deserialization. "
            "Install it with: pip install pyyaml"
        )
    data: dict[str, Any] = yaml.safe_load(yaml_str)
    return model_class.model_validate(data)
