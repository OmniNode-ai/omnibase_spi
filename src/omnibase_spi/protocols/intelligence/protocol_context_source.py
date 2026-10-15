# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol for context-source reads (OMN-21124 / OMN-18531 TC.1).

The SPI half of the context-source contract whose core half landed as
omnibase_core#1988: a context source answers one typed read —
``handle(ModelContextSourceRequest) -> ModelContextSourceResult`` — carrying
what it is asked for, on whose behalf, and at which revision. The wire models
live in omnibase_core and are imported from there only; the SPI never forks
them.

Example:
    >>> class RepoStateSource:
    ...     def handle(self, request: ModelContextSourceRequest) -> ModelContextSourceResult:
    ...         ...
    >>> assert isinstance(RepoStateSource(), ProtocolContextSource)
"""

from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.context.model_context_source_request import (
        ModelContextSourceRequest,
    )
    from omnibase_core.models.context.model_context_source_result import (
        ModelContextSourceResult,
    )

__all__ = ["ProtocolContextSource"]


@runtime_checkable
class ProtocolContextSource(Protocol):
    """A readable source of context-pack entries.

    Implementations answer exactly one read per call: the request's factor,
    scopes and revision select the entries, ``access`` names the tenant and
    principal the read is made for, and the result's status records whether
    entries were resolved, the read was denied, or the source is unavailable —
    never a silent empty success (see ModelContextSourceResult).

    The ``synchronous_execution = True`` class-level flag is read by the SPI
    validator to exempt ``handle`` from the async-by-default rule: the read is
    a definition-B style synchronous handler call. Do not remove it.
    """

    synchronous_execution: ClassVar[bool]

    def handle(
        self, request: "ModelContextSourceRequest"
    ) -> "ModelContextSourceResult":
        """Answer one context-source read at the requested revision.

        Args:
            request: The typed read: factor, scopes, task kind, caller scope,
                access (tenant/principal) and the revision to read at.

        Returns:
            The source's answer: status plus entries, paging, counts and
                timings, or the error code when nothing could be served.
        """
        ...
