#!/usr/bin/env python3
"""
Script to systematically add validation methods to remaining property-only protocols.
This will complete the fix for the 177 protocols causing validation confusion.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def get_protocol_method_mapping() -> Dict[str, List[str]]:
    """Map protocol names to appropriate validation methods."""
    return {
        # Workflow and orchestration protocols
        "ProtocolWorkflowSnapshot": ["validate_snapshot", "is_consistent"],
        "ProtocolWorkflowDefinition": ["validate_definition", "is_valid_schema"],
        "ProtocolTaskResult": ["validate_result", "is_success"],
        "ProtocolCompensationAction": ["validate_compensation", "can_execute"],
        "ProtocolNodeCapability": ["validate_capability", "is_supported"],
        "ProtocolWorkflowServiceInstance": ["validate_service_instance", "is_healthy"],
        "ProtocolRecoveryPoint": ["validate_recovery_point", "is_restorable"],
        "ProtocolReplayStrategy": ["validate_replay_strategy", "is_executable"],
        "ProtocolEventStream": ["validate_stream", "is_complete_stream"],
        "ProtocolEventProjection": ["validate_projection", "is_up_to_date"],
        # MCP protocols
        "ProtocolMCPSubsystemMetadata": ["validate_metadata", "has_required_fields"],
        "ProtocolMCPSubsystemRegistration": ["validate_registration", "is_active"],
        "ProtocolMCPToolExecution": ["validate_execution", "is_completed"],
        "ProtocolMCPRegistryMetrics": ["validate_metrics", "is_healthy"],
        "ProtocolMCPRegistryStatus": ["validate_status", "is_operational"],
        "ProtocolMCPRegistryConfig": ["validate_config", "is_valid_configuration"],
        "ProtocolMCPHealthCheck": ["validate_health_check", "is_passing"],
        "ProtocolMCPDiscoveryInfo": ["validate_discovery_info", "is_available"],
        "ProtocolMCPValidationError": ["validate_error", "is_critical"],
        "ProtocolMCPValidationResult": ["validate_validation_result", "has_errors"],
        # Event bus protocols
        "ProtocolEvent": ["validate_event", "has_required_fields"],
        "ProtocolEventResult": ["validate_result", "is_successful"],
        "ProtocolSecurityContext": ["validate_security_context", "is_authenticated"],
        "ProtocolEventSubscription": ["validate_subscription", "is_active"],
        "ProtocolOnexEvent": ["validate_onex_event", "is_well_formed"],
        "ProtocolEventBusCredentials": ["validate_credentials", "is_secure"],
        "ProtocolEventHeaders": ["validate_headers", "has_required_headers"],
        # Core system protocols
        "ProtocolLogEntry": ["validate_log_entry", "is_complete"],
        "ProtocolSerializationResult": ["validate_serialization", "has_data"],
        "ProtocolNodeMetadata": ["validate_node_metadata", "is_complete"],
        "ProtocolCacheStatistics": ["validate_statistics", "is_current"],
        "ProtocolMetadata": ["validate_metadata", "is_up_to_date"],
        "ProtocolActionPayload": ["validate_payload", "has_valid_parameters"],
        "ProtocolAction": ["validate_action", "is_executable"],
        "ProtocolState": ["validate_state", "is_consistent"],
        "ProtocolNodeMetadataBlock": ["validate_metadata_block", "is_complete"],
        "ProtocolSchemaObject": ["validate_schema", "is_valid_schema"],
        "ProtocolErrorInfo": ["validate_error_info", "is_retryable"],
        "ProtocolSystemEvent": ["validate_system_event", "is_well_formed"],
        "ProtocolNodeResult": ["validate_result", "is_successful"],
        "ProtocolServiceMetadata": ["validate_service_metadata", "has_capabilities"],
        "ProtocolServiceInstance": ["validate_service_instance", "is_available"],
        "ProtocolServiceHealthStatus": ["validate_health_status", "is_healthy"],
        "ProtocolCheckpointData": ["validate_checkpoint", "is_restorable"],
        "ProtocolStorageCredentials": ["validate_credentials", "is_secure"],
        "ProtocolStorageConfiguration": ["validate_configuration", "is_connectable"],
        "ProtocolStorageResult": ["validate_storage_result", "is_successful"],
        "ProtocolStorageListResult": ["validate_list_result", "has_items"],
        "ProtocolStorageHealthStatus": ["validate_health_status", "is_available"],
        "ProtocolErrorContext": ["validate_error_context", "has_trace"],
        "ProtocolRecoveryAction": ["validate_recovery_action", "is_applicable"],
        "ProtocolErrorResult": ["validate_error", "is_retryable"],
        "ProtocolVersionInfo": ["validate_version_info", "is_compatible"],
        "ProtocolCompatibilityCheck": ["validate_compatibility", "is_compatible"],
        "ProtocolHealthCheck": ["validate_health_check", "is_passing"],
        "ProtocolHealthMetrics": ["validate_metrics", "is_within_thresholds"],
        "ProtocolHealthMonitoring": ["validate_monitoring_config", "is_reasonable"],
        "ProtocolMetricsPoint": ["validate_metrics_point", "is_valid_measurement"],
        "ProtocolTraceSpan": ["validate_trace_span", "is_complete"],
        "ProtocolAuditEvent": ["validate_audit_event", "is_complete"],
        # Performance and analytics
        "ProtocolAnalyticsMetric": ["validate_metric", "is_valid_measurement"],
        "ProtocolAnalyticsProvider": ["validate_provider", "is_available"],
        "ProtocolAnalyticsSummary": ["validate_summary", "is_complete"],
        "ProtocolPerformanceMetric": ["validate_performance_metric", "is_valid"],
        "ProtocolPerformanceMetrics": ["validate_performance_metrics", "is_healthy"],
        # Connection and networking
        "ProtocolConnectionConfig": ["validate_connection_config", "is_connectable"],
        "ProtocolConnectionStatus": ["validate_connection_status", "is_connected"],
        # Retry and timeout
        "ProtocolRetryConfig": ["validate_retry_config", "is_reasonable"],
        "ProtocolRetryPolicy": ["validate_retry_policy", "is_applicable"],
        "ProtocolRetryAttempt": ["validate_retry_attempt", "is_valid_attempt"],
        "ProtocolRetryResult": ["validate_retry_result", "is_final"],
        "ProtocolTimeBased": ["validate_time_based", "is_valid_timing"],
        "ProtocolTimeout": ["validate_timeout", "is_reasonable"],
        "ProtocolDuration": ["validate_duration", "is_measurable"],
    }


def generate_method_signature(method_name: str, protocol_name: str) -> str:
    """Generate a method signature with appropriate docstring."""
    if method_name.startswith("validate_"):
        return f"""
    def {method_name}(self) -> bool:
        \"\"\"Validate {protocol_name.replace('Protocol', '').lower()} data integrity and consistency.\"\"\"
        ..."""
    elif method_name.startswith("is_"):
        property_name = method_name[3:].replace("_", " ")
        return f"""
    def {method_name}(self) -> bool:
        \"\"\"Check if {protocol_name.replace('Protocol', '').lower()} {property_name}.\"\"\"
        ..."""
    elif method_name.startswith("has_"):
        property_name = method_name[4:].replace("_", " ")
        return f"""
    def {method_name}(self) -> bool:
        \"\"\"Check if {protocol_name.replace('Protocol', '').lower()} {property_name}.\"\"\"
        ..."""
    elif method_name.startswith("can_"):
        action_name = method_name[4:].replace("_", " ")
        return f"""
    def {method_name}(self) -> bool:
        \"\"\"Check if {protocol_name.replace('Protocol', '').lower()} {action_name}.\"\"\"
        ..."""
    else:
        return f"""
    def {method_name}(self) -> bool:
        \"\"\"Execute {method_name.replace('_', ' ')} operation for {protocol_name.replace('Protocol', '').lower()}.\"\"\"
        ..."""


def find_protocol_in_file(
    file_path: Path, protocol_name: str
) -> Optional[Tuple[int, int]]:
    """Find the line range for a protocol definition in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        lines = content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == protocol_name:
                # Check if it's a protocol
                is_protocol = False
                has_runtime_checkable = False

                for decorator in node.decorator_list:
                    if (
                        isinstance(decorator, ast.Name)
                        and decorator.id == "runtime_checkable"
                    ):
                        has_runtime_checkable = True

                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Protocol":
                        is_protocol = True
                    elif isinstance(base, ast.Attribute) and base.attr == "Protocol":
                        is_protocol = True

                if is_protocol and has_runtime_checkable:
                    # Find the end of the class
                    start_line = node.lineno - 1  # Convert to 0-based
                    end_line = (
                        node.end_lineno - 1 if node.end_lineno else start_line + 10
                    )

                    # Find the actual end by looking for the last non-empty line in the class
                    for i in range(end_line, start_line, -1):
                        if (
                            i < len(lines)
                            and lines[i].strip()
                            and not lines[i].strip().startswith("@")
                        ):
                            end_line = i
                            break

                    return (start_line, end_line)

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

    return None


def add_methods_to_protocol(
    file_path: Path, protocol_name: str, methods: List[str]
) -> bool:
    """Add validation methods to a protocol in a file."""
    protocol_range = find_protocol_in_file(file_path, protocol_name)
    if not protocol_range:
        print(f"  ⚠️  Protocol {protocol_name} not found in {file_path}")
        return False

    start_line, end_line = protocol_range

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check if methods already exist
        protocol_content = "".join(lines[start_line : end_line + 1])
        existing_methods = set()
        for method in methods:
            if f"def {method}(" in protocol_content:
                existing_methods.add(method)

        methods_to_add = [m for m in methods if m not in existing_methods]
        if not methods_to_add:
            print(f"  ✅ Protocol {protocol_name} already has all required methods")
            return True

        # Generate method signatures
        method_signatures = [
            generate_method_signature(method, protocol_name)
            for method in methods_to_add
        ]
        methods_text = "".join(method_signatures)

        # Insert methods before the end of the class
        # Find the last property line
        insert_line = end_line
        for i in range(end_line, start_line, -1):
            line = lines[i].strip()
            if (
                line
                and ":" in line
                and not line.startswith("def ")
                and not line.startswith('"""')
                and not line.startswith("#")
            ):
                insert_line = i + 1
                break

        # Insert the methods
        lines.insert(insert_line, methods_text + "\n")

        # Write the file back
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(
            f"  ✅ Added {len(methods_to_add)} methods to {protocol_name}: {', '.join(methods_to_add)}"
        )
        return True

    except Exception as e:
        print(f"  ❌ Error modifying {file_path}: {e}")
        return False


def find_protocol_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the protocols directory."""
    protocol_files = []
    protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"

    if protocols_dir.exists():
        for py_file in protocols_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                protocol_files.append(py_file)

    return protocol_files


def main():
    """Main function to fix remaining protocols."""
    print("SYSTEMATIC PROTOCOL VALIDATION METHOD ADDITION")
    print("=" * 80)

    root_dir = Path("/Volumes/PRO-G40/Code/omnibase_spi")
    protocol_files = find_protocol_files(root_dir)
    protocol_methods = get_protocol_method_mapping()

    print(f"Found {len(protocol_files)} protocol files")
    print(f"Will process {len(protocol_methods)} protocols")
    print()

    # Group protocols by file for efficient processing
    protocol_to_file = {}
    for file_path in protocol_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for protocol_name in protocol_methods.keys():
                if f"class {protocol_name}(" in content:
                    protocol_to_file[protocol_name] = file_path

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"Found {len(protocol_to_file)} protocols in files")
    print()

    # Process each protocol
    success_count = 0
    error_count = 0

    for protocol_name, methods in protocol_methods.items():
        if protocol_name in protocol_to_file:
            file_path = protocol_to_file[protocol_name]
            rel_path = file_path.relative_to(root_dir)
            print(f"Processing {protocol_name} in {rel_path}")

            if add_methods_to_protocol(file_path, protocol_name, methods):
                success_count += 1
            else:
                error_count += 1
        else:
            print(f"⚠️  Protocol {protocol_name} not found in any file")
            error_count += 1

        print()

    print("SUMMARY:")
    print("=" * 80)
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total protocols: {len(protocol_methods)}")

    if success_count > 0:
        print(
            "\n✅ Validation methods have been added to reduce protocol signature hash collisions!"
        )
        print("Run the analysis script again to verify the fix.")


if __name__ == "__main__":
    main()
