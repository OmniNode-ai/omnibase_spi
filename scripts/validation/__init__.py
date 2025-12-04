# SPDX-FileCopyrightText: 2025 OmniNode Team
# SPDX-License-Identifier: Apache-2.0
"""
Validation scripts for omnibase_spi.

This package contains standalone validation scripts using only Python stdlib.
These are TEMPORARY validators until omnibase_core removes its SPI dependency,
at which point these will be replaced with omnibase_core.validation imports.

Available Validators:
    - validate_architecture.py: One-protocol-per-file validation
    - validate_naming_patterns.py: Naming conventions and @runtime_checkable
    - validate_namespace_isolation.py: No Infra imports, no Pydantic models
    - run_all_validations.py: Unified runner for all validators
"""
