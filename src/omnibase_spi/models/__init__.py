# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""SPI model types — concrete dataclasses used as config/result carriers by SPI protocols."""

from omnibase_spi.models.domain_plugin import (
    ModelDomainPluginConfig,
    ModelDomainPluginResult,
)

__all__: list[str] = [
    "ModelDomainPluginConfig",
    "ModelDomainPluginResult",
]
