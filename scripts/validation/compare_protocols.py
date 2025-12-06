#!/usr/bin/env python3
"""
Protocol Comparison Utility

A simple utility to compare two protocols and understand why they are or aren't
considered duplicates by the enhanced signature hashing algorithm.

Usage:
    python scripts/validation/compare_protocols.py \
        --file1 src/path/to/file1.py --protocol1 ProtocolName1 \
        --file2 src/path/to/file2.py --protocol2 ProtocolName2

    # Compare protocols in the same file
    python scripts/validation/compare_protocols.py \
        --file src/path/to/file.py \
        --protocol1 ProtocolName1 --protocol2 ProtocolName2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add the validation directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from protocol_signature_hasher import compare_protocol_signatures


def print_comparison_report(comparison: dict) -> None:
    """Print a detailed comparison report."""

    if "error" in comparison:
        print(f"❌ Error: {comparison['error']}")
        return

    print("=" * 80)
    print("🔍 PROTOCOL COMPARISON REPORT")
    print("=" * 80)

    # Basic comparison result
    are_duplicates = comparison["are_duplicates"]
    print(
        f"\n📊 DUPLICATE STATUS: {'❌ DUPLICATES' if are_duplicates else '✅ UNIQUE'}"
    )

    # Protocol details
    p1 = comparison["protocol1"]
    p2 = comparison["protocol2"]

    print(f"\n📋 PROTOCOL 1: {p1['protocol_name']}")
    print(f"   Signature Hash: {p1['signature_hash']}")
    print(f"   Domain: {p1['domain']}")
    print(f"   Type: {p1['protocol_type']}")
    print(f"   Properties: {len(p1['properties'])}")
    print(f"   Methods: {len(p1['methods'])}")
    print(f"   Base Protocols: {p1['base_protocols']}")

    print(f"\n📋 PROTOCOL 2: {p2['protocol_name']}")
    print(f"   Signature Hash: {p2['signature_hash']}")
    print(f"   Domain: {p2['domain']}")
    print(f"   Type: {p2['protocol_type']}")
    print(f"   Properties: {len(p2['properties'])}")
    print(f"   Methods: {len(p2['methods'])}")
    print(f"   Base Protocols: {p2['base_protocols']}")

    # Hash comparison
    print("\n🔐 HASH COMPARISON:")
    print(f"   Hash 1: {comparison['hash_comparison']['hash1']}")
    print(f"   Hash 2: {comparison['hash_comparison']['hash2']}")
    print(
        f"   Match: {'✅ YES' if comparison['hash_comparison']['match'] else '❌ NO'}"
    )

    # Differences
    if comparison["differences"]:
        print("\n🔍 DIFFERENCES FOUND:")
        for diff in comparison["differences"]:
            print(f"\n   📝 {diff['component'].replace('_', ' ').title()}:")
            print(f"      Protocol 1: {diff['protocol1_value']}")
            print(f"      Protocol 2: {diff['protocol2_value']}")
    else:
        print("\n✅ NO DIFFERENCES DETECTED")

    # Detailed properties comparison
    if p1["properties"] or p2["properties"]:
        print("\n📊 PROPERTY DETAILS:")
        print("   Protocol 1 Properties:")
        for prop in p1["properties"]:
            print(f"      • {prop}")
        print("   Protocol 2 Properties:")
        for prop in p2["properties"]:
            print(f"      • {prop}")

    # Method comparison
    if p1["methods"] or p2["methods"]:
        print("\n🔧 METHOD DETAILS:")
        print("   Protocol 1 Methods:")
        for method in p1["methods"]:
            print(f"      • {method}")
        print("   Protocol 2 Methods:")
        for method in p2["methods"]:
            print(f"      • {method}")

    # Signature string comparison (for debugging)
    print("\n🔍 SIGNATURE STRINGS (for debugging):")
    print("   Protocol 1:")
    for line in p1["signature_string"].split("\n"):
        print(f"      {line}")
    print("   Protocol 2:")
    for line in p2["signature_string"].split("\n"):
        print(f"      {line}")


def main():
    """Main comparison function."""
    parser = argparse.ArgumentParser(
        description="Compare two protocols to understand duplication detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare protocols in different files
  python compare_protocols.py --file1 src/a.py --protocol1 ProtocolA --file2 src/b.py --protocol2 ProtocolB

  # Compare protocols in the same file
  python compare_protocols.py --file src/types.py --protocol1 ProtocolA --protocol2 ProtocolB

  # Save detailed output to JSON
  python compare_protocols.py --file src/types.py --protocol1 ProtocolA --protocol2 ProtocolB --json output.json
        """,
    )

    # File arguments
    parser.add_argument("--file1", help="Path to first protocol file")
    parser.add_argument(
        "--file2",
        help="Path to second protocol file (defaults to file1 if not specified)",
    )
    parser.add_argument(
        "--file",
        help="Path to file containing both protocols (alternative to file1/file2)",
    )

    # Protocol arguments
    parser.add_argument(
        "--protocol1", required=True, help="Name of first protocol to compare"
    )
    parser.add_argument(
        "--protocol2", required=True, help="Name of second protocol to compare"
    )

    # Output options
    parser.add_argument("--json", help="Save detailed comparison to JSON file")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output including signature strings",
    )

    args = parser.parse_args()

    # Determine file paths
    if args.file:
        file1_path = args.file
        file2_path = args.file
    elif args.file1:
        file1_path = args.file1
        file2_path = args.file2 or args.file1
    else:
        print("❌ Error: Must specify either --file or --file1")
        return 1

    # Validate file paths
    if not Path(file1_path).exists():
        print(f"❌ Error: File does not exist: {file1_path}")
        return 1

    if not Path(file2_path).exists():
        print(f"❌ Error: File does not exist: {file2_path}")
        return 1

    try:
        # Perform comparison
        print("🔍 Comparing protocols:")
        print(f"   {args.protocol1} in {file1_path}")
        print(f"   {args.protocol2} in {file2_path}")

        comparison = compare_protocol_signatures(
            file1_path, args.protocol1, file2_path, args.protocol2
        )

        # Print report
        print_comparison_report(comparison)

        # Save JSON if requested
        if args.json:
            with open(args.json, "w") as f:
                json.dump(comparison, f, indent=2, default=str)
            print(f"\n💾 Detailed comparison saved to: {args.json}")

        # Return appropriate exit code
        if "error" in comparison:
            return 1
        else:
            return 0

    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
