# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Runtime protocols for domain plugin lifecycle management.

ProtocolDomainPlugin is the protocol exported from this subpackage.
ModelDomainPluginConfig and ModelDomainPluginResult are concrete dataclasses
that live in omnibase_core.models.runtime.model_domain_plugin; they are
re-exported here via __getattr__ (lazy) so that callers can import them
from this subpackage without a circular import at package-init time.
"""

from __future__ import annotations

import importlib

from omnibase_spi.protocols.runtime.protocol_domain_plugin import ProtocolDomainPlugin

__all__: list[str] = [
    "ModelDomainPluginConfig",
    "ModelDomainPluginResult",
    "ProtocolDomainPlugin",
]

_lazy: dict[str, str] = {
    "ModelDomainPluginConfig": "omnibase_core.models.runtime.model_domain_plugin",
    "ModelDomainPluginResult": "omnibase_core.models.runtime.model_domain_plugin",
}


def __getattr__(name: str) -> object:
    if name in _lazy:
        mod = importlib.import_module(_lazy[name])
        obj = getattr(mod, name)
        globals()[name] = obj
        return obj
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
