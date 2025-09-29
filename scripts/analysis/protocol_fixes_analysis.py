#!/usr/bin/env python3
"""
Detailed analysis for fixing protocol validation issues.
Identifies specific fixes needed for each category of protocols.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple


def get_incomplete_protocols() -> List[str]:
    """Get list of protocols that definitely need methods."""
    return [
        "ProtocolContainerServiceFactory",
        "ProtocolErrorSanitizerFactory",
        "ProtocolConfigurationManagerFactory",
        "ProtocolCircuitBreakerFactory",
        "ProtocolEventBusFactory",
        "ProtocolCacheServiceProvider",
        "ProtocolFileTypeHandlerProvider",
        "ProtocolHttpClientProvider",
        "ProtocolValidationOrchestratorFactory",
    ]


def get_data_model_fixes() -> Dict[str, List[str]]:
    """Get suggested validation methods for data model protocols."""
    return {
        # Core data structures
        "ProtocolWorkflowMetadata": ["validate_metadata", "is_complete"],
        "ProtocolWorkflowContext": ["validate_context", "has_required_data"],
        "ProtocolWorkflowDefinition": ["validate_definition", "is_valid_schema"],
        "ProtocolWorkflowSnapshot": ["validate_snapshot", "is_consistent"],
        "ProtocolTaskConfiguration": ["validate_task", "has_valid_dependencies"],
        "ProtocolWorkflowEvent": ["validate_event", "is_valid_sequence"],
        "ProtocolTaskResult": ["validate_result", "is_success"],
        # Configuration objects
        "ProtocolRetryConfiguration": ["validate_retry_config", "is_valid_policy"],
        "ProtocolTimeoutConfiguration": ["validate_timeout_config", "is_reasonable"],
        "ProtocolCompensationAction": ["validate_compensation", "can_execute"],
        # MCP objects
        "ProtocolMCPToolDefinition": ["validate_tool_definition", "is_complete"],
        "ProtocolMCPSubsystemMetadata": ["validate_metadata", "has_required_fields"],
        "ProtocolMCPSubsystemRegistration": ["validate_registration", "is_active"],
        "ProtocolMCPToolExecution": ["validate_execution", "is_completed"],
        # Error and result objects
        "ProtocolErrorResult": ["validate_error", "is_retryable"],
        "ProtocolNodeResult": ["validate_result", "is_successful"],
        "ProtocolSerializationResult": ["validate_serialization", "has_data"],
        # Event and messaging
        "ProtocolEvent": ["validate_event", "has_required_fields"],
        "ProtocolOnexEvent": ["validate_onex_event", "is_well_formed"],
        "ProtocolEventResult": ["validate_result", "is_successful"],
        "ProtocolEventMessage": ["validate_message", "is_deliverable"],
        # Health and monitoring
        "ProtocolHealthCheck": ["validate_health_check", "is_passing"],
        "ProtocolHealthMetrics": ["validate_metrics", "is_within_thresholds"],
        "ProtocolPerformanceMetrics": ["validate_performance", "is_acceptable"],
        "ProtocolAuditEvent": ["validate_audit_event", "is_complete"],
        # Storage and persistence
        "ProtocolStorageResult": ["validate_storage_result", "is_successful"],
        "ProtocolCheckpointData": ["validate_checkpoint", "is_restorable"],
        # Security and validation
        "ProtocolSecurityContext": ["validate_security_context", "is_authenticated"],
        "ProtocolMCPValidationResult": ["validate_validation_result", "has_errors"],
        "ProtocolComplianceReport": ["validate_report", "is_compliant"],
    }


def get_marker_interface_fixes() -> Dict[str, Dict]:
    """Get fixes for marker interfaces."""
    return {
        "ProtocolSupportedMetadataType": {
            "add_method": "validate_for_metadata",
            "add_documentation": True,
            "purpose": "Validates that this type can be safely stored as metadata",
        },
        "ProtocolSupportedPropertyValue": {
            "add_method": "validate_for_property",
            "add_documentation": True,
            "purpose": "Validates that this value can be used as a property",
        },
        "ProtocolNodeInfoLike": {
            "add_method": "get_node_info",
            "add_documentation": True,
            "purpose": "Extracts node information for discovery systems",
        },
        "ProtocolIdentifiable": {
            "existing_method": "id",
            "add_documentation": True,
            "purpose": "Provides unique identification",
        },
        "ProtocolNameable": {
            "existing_method": "name",
            "add_documentation": True,
            "purpose": "Provides human-readable naming",
        },
        "ProtocolConfigurable": {
            "existing_method": "configure",
            "add_documentation": True,
            "purpose": "Supports runtime configuration",
        },
        "ProtocolExecutable": {
            "existing_method": "execute",
            "add_documentation": True,
            "purpose": "Supports execution operations",
        },
        "ProtocolMetadataProvider": {
            "existing_method": "get_metadata",
            "add_documentation": True,
            "purpose": "Provides metadata for introspection",
        },
    }


def get_incomplete_protocol_fixes() -> Dict[str, List[str]]:
    """Get methods needed for incomplete protocols."""
    return {
        "ProtocolContainerServiceFactory": [
            "create_container_service",
            "get_service_capabilities",
            "validate_configuration",
        ],
        "ProtocolErrorSanitizerFactory": [
            "create_sanitizer",
            "get_sanitizer_config",
            "validate_sanitizer_rules",
        ],
        "ProtocolConfigurationManagerFactory": [
            "create_configuration_manager",
            "get_supported_formats",
            "validate_configuration_schema",
        ],
        "ProtocolCircuitBreakerFactory": [
            "create_circuit_breaker",
            "get_default_config",
            "validate_circuit_breaker_config",
        ],
        "ProtocolEventBusFactory": [
            "create_event_bus",
            "get_supported_transports",
            "validate_event_bus_config",
        ],
        "ProtocolCacheServiceProvider": [
            "get_cache_service",
            "get_cache_statistics",
            "validate_cache_config",
        ],
        "ProtocolFileTypeHandlerProvider": [
            "get_handler_for_type",
            "get_supported_types",
            "register_handler",
        ],
        "ProtocolHttpClientProvider": [
            "get_http_client",
            "get_client_config",
            "validate_http_config",
        ],
        "ProtocolValidationOrchestratorFactory": [
            "create_orchestrator",
            "get_validation_capabilities",
            "validate_orchestrator_config",
        ],
    }


def generate_method_signatures(protocol_name: str, methods: List[str]) -> str:
    """Generate method signatures for a protocol."""
    signatures = []

    for method in methods:
        if method.startswith("validate_"):
            signatures.append(
                f"""
    def {method}(self) -> bool:
        \"\"\"Validate {protocol_name.replace('Protocol', '').lower()} data.\"\"\"
        ..."""
            )
        elif method.startswith("is_"):
            signatures.append(
                f"""
    def {method}(self) -> bool:
        \"\"\"Check if {protocol_name.replace('Protocol', '').lower()} {method[3:].replace('_', ' ')}.\"\"\"
        ..."""
            )
        elif method.startswith("has_"):
            signatures.append(
                f"""
    def {method}(self) -> bool:
        \"\"\"Check if {protocol_name.replace('Protocol', '').lower()} {method[4:].replace('_', ' ')}.\"\"\"
        ..."""
            )
        elif method.startswith("get_"):
            signatures.append(
                f"""
    def {method}(self) -> object:
        \"\"\"Get {method[4:].replace('_', ' ')} for {protocol_name.replace('Protocol', '').lower()}.\"\"\"
        ..."""
            )
        elif method.startswith("create_"):
            signatures.append(
                f"""
    def {method}(self, **kwargs: object) -> object:
        \"\"\"Create {method[7:].replace('_', ' ')}.\"\"\"
        ..."""
            )
        else:
            signatures.append(
                f"""
    def {method}(self, *args: object, **kwargs: object) -> object:
        \"\"\"Execute {method.replace('_', ' ')} operation.\"\"\"
        ..."""
            )

    return "".join(signatures)


def generate_marker_method(marker_info: Dict) -> str:
    """Generate method for marker interface."""
    if "existing_method" in marker_info:
        return ""  # Already has the method

    method_name = marker_info["add_method"]
    purpose = marker_info["purpose"]

    if method_name.startswith("validate_"):
        return f"""
    def {method_name}(self) -> bool:
        \"\"\"{purpose}.\"\"\"
        ..."""
    elif method_name.startswith("get_"):
        return f"""
    def {method_name}(self) -> object:
        \"\"\"{purpose}.\"\"\"
        ..."""
    else:
        return f"""
    def {method_name}(self) -> object:
        \"\"\"{purpose}.\"\"\"
        ..."""


def main():
    """Generate fixes for all protocol categories."""

    print("PROTOCOL FIXES ANALYSIS")
    print("=" * 80)

    # Get all fix requirements
    data_model_fixes = get_data_model_fixes()
    marker_fixes = get_marker_interface_fixes()
    incomplete_fixes = get_incomplete_protocol_fixes()

    print(f"\nDATA MODEL PROTOCOLS TO FIX ({len(data_model_fixes)}):")
    print("-" * 60)
    for protocol, methods in data_model_fixes.items():
        print(f"\n{protocol}:")
        print(f"  Methods to add: {', '.join(methods)}")
        print("  Generated signatures:")
        print(generate_method_signatures(protocol, methods))

    print(f"\nMARKER INTERFACES TO ENHANCE ({len(marker_fixes)}):")
    print("-" * 60)
    for protocol, info in marker_fixes.items():
        print(f"\n{protocol}:")
        print(f"  Purpose: {info['purpose']}")
        if "existing_method" in info:
            print(f"  Has method: {info['existing_method']}")
        else:
            print(f"  Method to add: {info['add_method']}")
            print("  Generated signature:")
            print(generate_marker_method(info))

    print(f"\nINCOMPLETE PROTOCOLS TO FIX ({len(incomplete_fixes)}):")
    print("-" * 60)
    for protocol, methods in incomplete_fixes.items():
        print(f"\n{protocol}:")
        print(f"  Methods to add: {', '.join(methods)}")
        print("  Generated signatures:")
        print(generate_method_signatures(protocol, methods))

    print(f"\nSUMMARY:")
    print("-" * 60)
    print(f"Data model protocols to enhance: {len(data_model_fixes)}")
    print(f"Marker interfaces to document: {len(marker_fixes)}")
    print(f"Incomplete protocols to fix: {len(incomplete_fixes)}")
    total_to_fix = len(data_model_fixes) + len(marker_fixes) + len(incomplete_fixes)
    print(f"Total protocols requiring changes: {total_to_fix}")

    print(f"\nNEXT STEPS:")
    print("-" * 60)
    print("1. Add validation methods to data model protocols")
    print("2. Enhance marker interface documentation")
    print("3. Add missing methods to incomplete protocols")
    print("4. Update validation to handle method signatures correctly")
    print("5. Verify all changes maintain SPI purity")


if __name__ == "__main__":
    main()
