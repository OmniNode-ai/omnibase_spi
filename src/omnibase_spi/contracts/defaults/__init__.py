"""
Default handler contract templates.

This module contains default YAML templates for handler contracts:
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
