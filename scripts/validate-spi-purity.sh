#!/bin/bash
# Validate SPI Purity - Prevent implementation violations in Service Provider Interface
#
# This script ensures the SPI package contains only pure protocol definitions
# and no concrete implementations, enums, or ABC classes.

set -euo pipefail

echo "🔍 Validating SPI purity..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VIOLATIONS_FOUND=0

# Function to report violation
report_violation() {
    local file=$1
    local line=$2
    local violation=$3
    local message=$4
    
    echo -e "${RED}❌ SPI VIOLATION${NC} in ${file}:${line}"
    echo -e "   ${YELLOW}Found:${NC} ${violation}"
    echo -e "   ${YELLOW}Issue:${NC} ${message}"
    echo
    VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
}

# Check for concrete class implementations (inheriting from non-Protocol classes)
echo "Checking for concrete class implementations..."
while IFS=: read -r file line content; do
    if [[ $content =~ class.*\(.*[^Protocol][a-zA-Z]*\): ]] && [[ ! $content =~ class.*\(.*Protocol.*\): ]] && [[ ! $content =~ class.*\(str,.*Enum\): ]] && [[ ! $content =~ class.*\(ABC\): ]]; then
        report_violation "$file" "$line" "$content" "SPI should not contain concrete class implementations"
    fi
done < <(grep -rn "^class.*(" src/ --include="*.py" || true)

# Check for Enum classes (should use Literal instead)
echo "Checking for Enum usage..."
while IFS=: read -r file line content; do
    if [[ $content =~ class.*\(.*Enum\): ]]; then
        report_violation "$file" "$line" "$content" "SPI should use Literal types instead of Enums"
    fi
done < <(grep -rn "class.*Enum" src/ --include="*.py" || true)

# Check for ABC classes (should use Protocol instead)  
echo "Checking for ABC usage..."
while IFS=: read -r file line content; do
    if [[ $content =~ class.*\(ABC\): ]]; then
        report_violation "$file" "$line" "$content" "SPI should use Protocol instead of ABC"
    fi
done < <(grep -rn "class.*ABC" src/ --include="*.py" || true)

# Check for concrete method implementations (methods with actual code, not just ...)
echo "Checking for concrete method implementations..."
TEMP_FILE=$(mktemp)
# Find all method definitions and check if they have implementations
grep -rn "def.*\(self.*\):" src/ --include="*.py" > "$TEMP_FILE" || true
while IFS=: read -r file line content; do
    # Skip if it's just an abstract method with ...
    if [[ $content =~ def.*\(self.*\):$ ]]; then
        # Check the next few lines for actual implementation
        next_lines=$(sed -n "$((line+1)),$((line+5))p" "$file" 2>/dev/null || echo "")
        if [[ ! $next_lines =~ ^[[:space:]]*\.\.\.[[:space:]]*$ ]] && [[ ! $next_lines =~ ^[[:space:]]*\".*\"[[:space:]]*$ ]] && [[ ! $next_lines =~ ^[[:space:]]*pass[[:space:]]*$ ]]; then
            # Check if there's actual implementation code
            if echo "$next_lines" | grep -q -E "(return [^.]|raise [^N]|if |for |while |try:|except|print|=)" 2>/dev/null; then
                report_violation "$file" "$line" "$content" "SPI should not contain concrete method implementations"
            fi
        fi
    fi
done < "$TEMP_FILE"
rm "$TEMP_FILE"

# Check for imports that suggest implementation (not just type definitions)
echo "Checking for implementation imports..."
IMPLEMENTATION_IMPORTS=(
    "from abc import ABC"
    "from enum import Enum" 
    "import asyncio"
    "from datetime import datetime$"
    "import logging"
    "import os"
    "import sys"
    "import json"
    "import yaml"
    "import requests"
    "import sqlite3"
    "import psycopg2"
    "import redis"
)

for import_pattern in "${IMPLEMENTATION_IMPORTS[@]}"; do
    while IFS=: read -r file line content; do
        # Allow datetime import only in core_types.py for ProtocolDateTime
        if [[ $import_pattern == "from datetime import datetime$" ]] && [[ $file == *"core_types.py" ]]; then
            continue
        fi
        # Allow enum import temporarily during migration (but report as warning)
        if [[ $import_pattern == "from enum import Enum" ]]; then
            echo -e "${YELLOW}⚠️  WARNING${NC} in ${file}:${line}"
            echo -e "   ${YELLOW}Found:${NC} ${content}"
            echo -e "   ${YELLOW}Issue:${NC} Enum import detected - should be migrated to Literal types"
            echo
        else
            report_violation "$file" "$line" "$content" "SPI should not import implementation libraries"
        fi
    done < <(grep -rn "$import_pattern" src/ --include="*.py" || true)
done

# Check for hardcoded values that suggest implementation logic
echo "Checking for implementation logic patterns..."
IMPLEMENTATION_PATTERNS=(
    "print\("
    "logging\."
    "log\."
    "open\("
    "with open"
    "requests\."
    "json\.loads"
    "yaml\.load"
    "os\.path"
    "sys\."
    "time\.sleep"
    "asyncio\.sleep"
    "threading\."
)

for pattern in "${IMPLEMENTATION_PATTERNS[@]}"; do
    while IFS=: read -r file line content; do
        report_violation "$file" "$line" "$content" "SPI should not contain implementation logic"
    done < <(grep -rn "$pattern" src/ --include="*.py" || true)
done

# Summary
echo "----------------------------------------"
if [ $VIOLATIONS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ SPI purity validation PASSED${NC}"
    echo "All files contain only pure protocol definitions."
else
    echo -e "${RED}❌ SPI purity validation FAILED${NC}"
    echo "Found $VIOLATIONS_FOUND violations."
    echo
    echo "SPI (Service Provider Interface) should contain only:"
    echo "• Protocol definitions using typing.Protocol"
    echo "• Type aliases using typing.Literal"
    echo "• Type unions and generic types"
    echo "• Abstract method signatures with '...' implementation"
    echo
    echo "SPI should NOT contain:"
    echo "• Concrete class implementations"
    echo "• Enum classes (use Literal instead)"
    echo "• ABC classes (use Protocol instead)"
    echo "• Method implementations with actual logic"
    echo "• Implementation library imports"
    echo "• Business logic or concrete behavior"
    exit 1
fi