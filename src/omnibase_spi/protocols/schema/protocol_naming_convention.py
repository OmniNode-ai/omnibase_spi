# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.132271'
# description: Stamped by ToolPython
# entrypoint: python://protocol_naming_convention
# hash: 3cc5f68ecdc8ba39c85db923420a42b40f4cd7e5a6a2c1989e6da28813f3545b
# last_modified_at: '2025-05-29T14:14:00.276344+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_naming_convention.py
# namespace: python://omnibase.protocol.protocol_naming_convention
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: b403ea41-293d-4927-8dc8-e7208b8d28fa
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolNamingConventionResult(Protocol):
    """
    Protocol for naming convention validation results.

    Captures the outcome of validating a name against ONEX naming
    conventions including validity status, any errors or warnings,
    and a suggested correction if the name is invalid.

    Attributes:
        is_valid: Whether the name conforms to naming conventions
        errors: List of critical naming convention violations
        warnings: List of non-critical naming suggestions
        suggested_name: Suggested valid name if original is invalid
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggested_name: str | None

    def to_dict(self) -> dict[str, object]:
        """Convert the validation result to a dictionary representation.

        Serializes the result including validity status, messages,
        and suggested corrections for logging or API responses.

        Returns:
            Dictionary containing 'is_valid', 'errors', 'warnings',
            and 'suggested_name' keys with their respective values.
        """
        ...


@runtime_checkable
class ProtocolNamingConvention(Protocol):
    """
    Protocol for ONEX naming convention enforcement.

    Example:
        class MyNamingConvention:
            def validate_name(self, name: str) -> ProtocolNamingConventionResult:
                ...
    """

    async def validate_name(self, name: str) -> ProtocolNamingConventionResult: ...
