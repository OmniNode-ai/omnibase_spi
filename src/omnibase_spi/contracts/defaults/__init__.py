# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Default handler contract templates.

Default YAML templates for handler contracts:
- default_compute_handler.yaml: Pure computation handlers
- default_effect_handler.yaml: Side-effecting handlers (DB, HTTP, etc.)
- default_nondeterministic_compute_handler.yaml: LLM/AI inference handlers
"""

DEFAULT_TEMPLATES = [
    "default_compute_handler.yaml",
    "default_effect_handler.yaml",
    "default_nondeterministic_compute_handler.yaml",
]

__all__ = ["DEFAULT_TEMPLATES"]
