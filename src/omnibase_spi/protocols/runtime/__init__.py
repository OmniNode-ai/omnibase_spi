# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Runtime protocols.

Includes:
    * ProtocolDomainPlugin — domain plugin lifecycle hooks.
    * ProtocolHandleable — structural ``handle()`` protocol for handlers.
    * ProtocolHandlerOwnershipQuery — local-vs-remote ownership decision.
    * ProtocolHandlerResolver — handler class → instance resolution.
    * ProtocolLocalRuntimeBus (+ UnsubscribeCallback) — minimal event bus shape
      used by the local runtime.
    * ProtocolLocalRuntimeMessage — minimal bus message shape.
    * ProtocolLocalRuntimeCallableTarget — local runtime call entry point.
    * ProtocolLocalRuntimePayloadModel — publishable payload model shape.
    * ProtocolLocalRuntimeDumpModel — handler return-value dump model shape.

ModelDomainPluginConfig and ModelDomainPluginResult are concrete dataclasses
that live in omnibase_core.models.runtime.model_domain_plugin; they are
re-exported here via __getattr__ (lazy) so that callers can import them
from this subpackage without a circular import at package-init time.
"""

import importlib

from omnibase_spi.protocols.runtime.protocol_domain_plugin import ProtocolDomainPlugin
from omnibase_spi.protocols.runtime.protocol_handleable import ProtocolHandleable
from omnibase_spi.protocols.runtime.protocol_handler_ownership_query import (
    ProtocolHandlerOwnershipQuery,
)
from omnibase_spi.protocols.runtime.protocol_handler_resolver import (
    ProtocolHandlerResolver,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_bus import (
    ProtocolLocalRuntimeBus,
    UnsubscribeCallback,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_callable_target import (
    ProtocolLocalRuntimeCallableTarget,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_dump_model import (
    ProtocolLocalRuntimeDumpModel,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_message import (
    ProtocolLocalRuntimeMessage,
)
from omnibase_spi.protocols.runtime.protocol_local_runtime_payload_model import (
    ProtocolLocalRuntimePayloadModel,
)

__all__: list[str] = [
    "ModelDomainPluginConfig",
    "ModelDomainPluginResult",
    "ProtocolDomainPlugin",
    "ProtocolHandleable",
    "ProtocolHandlerOwnershipQuery",
    "ProtocolHandlerResolver",
    "ProtocolLocalRuntimeBus",
    "ProtocolLocalRuntimeCallableTarget",
    "ProtocolLocalRuntimeDumpModel",
    "ProtocolLocalRuntimeMessage",
    "ProtocolLocalRuntimePayloadModel",
    "UnsubscribeCallback",
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
