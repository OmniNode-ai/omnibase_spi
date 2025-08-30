#!/bin/bash

# Validate Forbidden Patterns - Check for patterns that violate SPI standards
# Exit codes: 0 = success, 1 = forbidden patterns found

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Validating forbidden patterns in SPI codebase..."

# Track violations
VIOLATIONS=0

# Function to check for patterns
check_pattern() {
    local pattern="$1"
    local description="$2"
    local files="$3"
    
    echo "  Checking for: $description"
    
    # Find matches
    local matches
    if matches=$(grep -n "$pattern" $files 2>/dev/null); then
        echo -e "${RED}❌ Found forbidden pattern: $description${NC}"
        echo "$matches" | while read -r line; do
            echo "    $line"
        done
        VIOLATIONS=$((VIOLATIONS + 1))
        return 1
    else
        echo -e "${GREEN}✅ No issues found: $description${NC}"
        return 0
    fi
}

# Get all Python files in src/
PYTHON_FILES=$(find src -name "*.py" -type f)

if [ -z "$PYTHON_FILES" ]; then
    echo "No Python files found in src/"
    exit 0
fi

echo "Checking files: $(echo $PYTHON_FILES | wc -w) Python files"

# Check for forbidden patterns
echo ""
echo "🚫 Checking for forbidden patterns..."

# Check for "model" terminology (case-insensitive word boundaries)
check_pattern '\bmodel\b' '"model" terminology (use "data", "object", or specific type names)' "$PYTHON_FILES" || true

# Check for Union types that should be protocols (unions of protocol/class types)
# Allow simple value unions and Dict/List with simple values
check_pattern 'Union\[.*Protocol.*,' 'Union types with protocols (create a common protocol instead)' "$PYTHON_FILES" || true

# Check for "Model" prefix in class names
check_pattern 'Model[A-Z]' '"Model" prefix in class names (use descriptive names without "Model")' "$PYTHON_FILES" || true

# Check for problematic Any usage (but allow in generic contexts like **kwargs: Any)
# Skip common acceptable patterns like **kwargs: Any, *args: Any, generic protocol methods
check_pattern 'def [^(]*\([^)]*[^:]: Any[^)]' 'Problematic Any usage in function parameters (use specific types)' "$PYTHON_FILES" || true

# Check for import violations - external dependencies
echo ""
echo "📦 Checking for external dependencies..."
check_pattern 'from \(requests\|numpy\|pandas\|fastapi\|flask\|django\)' 'external dependencies (SPI should be dependency-free)' "$PYTHON_FILES" || true

# Summary
echo ""
if [ $VIOLATIONS -eq 0 ]; then
    echo -e "${GREEN}✅ All validation checks passed!${NC}"
    echo "SPI codebase follows forbidden pattern standards."
    exit 0
else
    echo -e "${RED}❌ Found $VIOLATIONS forbidden pattern violation(s)${NC}"
    echo ""
    echo "To fix these issues:"
    echo "  1. Replace 'model' with 'data', 'object', or specific type names"
    echo "  2. Replace Union types of protocols with common protocol interfaces"
    echo "  3. Remove 'Model' prefixes from class names"
    echo "  4. Replace Any with specific types or object"
    echo "  5. Remove external dependencies from SPI"
    echo ""
    exit 1
fi