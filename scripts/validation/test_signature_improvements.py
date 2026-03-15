#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Test script to verify that the enhanced signature hashing eliminates false positives.

This script specifically tests protocols that were previously considered duplicates
to verify they now have unique signatures.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Add the validation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from protocol_signature_hasher import (
    EnhancedProtocolSignatureHasher,
    compare_protocol_signatures,
)


def test_workflow_value_protocols():
    """Test that different ProtocolWorkflowValue protocols have unique signatures."""
    file_path = (
        "src/omnibase_spi/protocols/types/protocol_workflow_orchestration_types.py"
    )

    protocols_to_test = [
        "ProtocolWorkflowStringValue",
        "ProtocolWorkflowStringListValue",
        "ProtocolWorkflowStringDictValue",
        "ProtocolWorkflowNumericValue",
        "ProtocolWorkflowStructuredValue",
    ]

    hasher = EnhancedProtocolSignatureHasher()
    signatures = {}

    print("🔍 Testing ProtocolWorkflowValue inheritance hierarchy:")
    print("=" * 60)

    # Parse the file and extract protocols
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)

        # Find and hash each protocol
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in protocols_to_test:
                signature_hash = hasher.generate_signature_hash(node, file_path)
                debug_info = hasher.debug_signature_components(node, file_path)
                signatures[node.name] = signature_hash

                print(f"\n📋 {node.name}:")
                print(f"   Signature Hash: {signature_hash}")
                print(f"   Domain: {debug_info['domain']}")
                print(f"   Type: {debug_info['protocol_type']}")
                print(f"   Properties: {debug_info['properties']}")
                print(f"   Base Protocols: {debug_info['base_protocols']}")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        raise AssertionError(f"Error processing {file_path}: {e}") from e

    # Check for uniqueness
    unique_signatures = set(signatures.values())

    print("\n📊 RESULTS:")
    print(f"   Total protocols tested: {len(signatures)}")
    print(f"   Unique signatures: {len(unique_signatures)}")
    print(
        f"   All signatures unique: {'✅ YES' if len(signatures) == len(unique_signatures) else '❌ NO'}"
    )

    if len(signatures) != len(unique_signatures):
        print("\n🚨 DUPLICATE SIGNATURES DETECTED:")
        signature_groups = {}
        for name, sig in signatures.items():
            if sig not in signature_groups:
                signature_groups[sig] = []
            signature_groups[sig].append(name)

        for sig, names in signature_groups.items():
            if len(names) > 1:
                print(f"   Signature {sig}: {', '.join(names)}")

    assert len(signatures) == len(unique_signatures), (
        "Duplicate signatures detected for workflow value protocols"
    )


def test_stamp_validation_options():
    """Test that ProtocolStampOptions and ProtocolValidationOptions have unique signatures."""
    file_path = "src/omnibase_spi/protocols/file_handling/protocol_file_type_handler.py"

    print("\n🔍 Testing StampOptions vs ValidationOptions:")
    print("=" * 60)

    comparison = compare_protocol_signatures(
        file_path, "ProtocolStampOptions", file_path, "ProtocolValidationOptions"
    )

    if "error" in comparison:
        print(f"❌ Error: {comparison['error']}")
        raise AssertionError(comparison["error"]) from Exception(comparison["error"])

    print("\n📋 ProtocolStampOptions:")
    print(f"   Signature Hash: {comparison['protocol1']['signature_hash']}")
    print(f"   Properties: {comparison['protocol1']['properties']}")

    print("\n📋 ProtocolValidationOptions:")
    print(f"   Signature Hash: {comparison['protocol2']['signature_hash']}")
    print(f"   Properties: {comparison['protocol2']['properties']}")

    print("\n📊 COMPARISON RESULT:")
    print(f"   Are duplicates: {'❌ YES' if comparison['are_duplicates'] else '✅ NO'}")
    print(f"   Hash1: {comparison['hash_comparison']['hash1']}")
    print(f"   Hash2: {comparison['hash_comparison']['hash2']}")

    if comparison["differences"]:
        print("\n🔍 DIFFERENCES DETECTED:")
        for diff in comparison["differences"]:
            print(
                f"   {diff['component']}: {diff['protocol1_value']} vs {diff['protocol2_value']}"
            )

    assert not comparison["are_duplicates"], (
        "StampOptions and ValidationOptions should not be duplicates"
    )


def test_memory_request_protocols():
    """Test memory request protocols that were previously duplicates."""
    file_path = "src/omnibase_spi/protocols/memory/protocol_memory_requests.py"
    advanced_file_path = (
        "src/omnibase_spi/protocols/memory/protocol_memory_advanced_requests.py"
    )

    print("\n🔍 Testing Memory Request protocols:")
    print("=" * 60)

    comparison = compare_protocol_signatures(
        file_path,
        "ProtocolMemoryRetrieveRequest",
        advanced_file_path,
        "ProtocolBatchMemoryRetrieveRequest",
    )

    if "error" in comparison:
        print(f"❌ Error: {comparison['error']}")
        raise AssertionError(comparison["error"]) from Exception(comparison["error"])

    print("\n📋 ProtocolMemoryRetrieveRequest:")
    print(f"   Signature Hash: {comparison['protocol1']['signature_hash']}")
    print(f"   Methods: {len(comparison['protocol1']['methods'])}")

    print("\n📋 ProtocolBatchMemoryRetrieveRequest:")
    print(f"   Signature Hash: {comparison['protocol2']['signature_hash']}")
    print(f"   Methods: {len(comparison['protocol2']['methods'])}")

    print("\n📊 COMPARISON RESULT:")
    print(f"   Are duplicates: {'❌ YES' if comparison['are_duplicates'] else '✅ NO'}")

    assert not comparison["are_duplicates"], (
        "Memory request protocols should not be duplicates"
    )


def test_performance_impact():
    """Test the performance of the enhanced hashing algorithm."""
    import time

    from validate_protocol_duplicates import find_all_protocols

    print("\n🔍 Testing Performance Impact:")
    print("=" * 60)

    base_path = Path("src/")

    start_time = time.time()
    protocols = find_all_protocols(base_path)
    end_time = time.time()

    processing_time = end_time - start_time

    print("\n📊 PERFORMANCE METRICS:")
    print(f"   Total protocols processed: {len(protocols)}")
    print(f"   Processing time: {processing_time:.3f} seconds")
    print(f"   Protocols per second: {len(protocols) / processing_time:.1f}")
    print(
        f"   Average time per protocol: {(processing_time / len(protocols) * 1000):.2f} ms"
    )

    # Performance expectations
    expected_max_time = 30.0  # seconds
    expected_min_throughput = 10  # protocols per second

    performance_ok = (
        processing_time < expected_max_time
        and (len(protocols) / processing_time) > expected_min_throughput
    )

    print("\n📈 PERFORMANCE ASSESSMENT:")
    print(
        f"   Within expected time limit: {'✅ YES' if processing_time < expected_max_time else '❌ NO'}"
    )
    print(
        f"   Meets throughput requirements: {'✅ YES' if (len(protocols) / processing_time) > expected_min_throughput else '❌ NO'}"
    )
    print(
        f"   Overall performance: {'✅ ACCEPTABLE' if performance_ok else '⚠️ NEEDS OPTIMIZATION'}"
    )

    assert performance_ok, "Enhanced hashing performance outside expected thresholds"


def main():
    """Run all signature improvement tests."""
    print("🧪 SIGNATURE HASHING IMPROVEMENT VERIFICATION")
    print("=" * 80)

    tests = [
        ("Workflow Value Protocols", test_workflow_value_protocols),
        ("Stamp vs Validation Options", test_stamp_validation_options),
        ("Memory Request Protocols", test_memory_request_protocols),
        ("Performance Impact", test_performance_impact),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")

    print("\n📈 OVERALL RESULTS:")
    print(f"   Tests passed: {passed}/{total}")
    print(f"   Success rate: {(passed / total) * 100:.1f}%")

    if passed == total:
        print("   🎉 ALL TESTS PASSED - Signature improvements working correctly!")
        return 0
    print("   ⚠️ Some tests failed - Review implementation")
    return 1


if __name__ == "__main__":
    sys.exit(main())
