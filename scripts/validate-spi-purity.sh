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

# Check for @dataclass usage (should use Protocol instead)
echo "Checking for @dataclass usage..."
while IFS=: read -r file line content; do
    if [[ $content =~ @dataclass ]]; then
        report_violation "$file" "$line" "$content" "SPI should use @runtime_checkable Protocol instead of @dataclass"
    fi
done < <(grep -rn "@dataclass" src/ --include="*.py" || true)

# Check for dataclasses imports (should not be needed in pure SPI)
echo "Checking for dataclasses imports..."
while IFS=: read -r file line content; do
    if [[ $content =~ from\ dataclasses || $content =~ import\ dataclasses ]]; then
        report_violation "$file" "$line" "$content" "SPI should not import dataclasses - use Protocol instead"
    fi
done < <(grep -rn "dataclasses" src/ --include="*.py" || true)

# Check for __init__ methods in Protocol classes (not allowed in SPI)
echo "Checking for __init__ methods in Protocol classes..."
while IFS=: read -r file line content; do
    # Skip test files and validation utilities (not core SPI)
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    if [[ $content =~ def\ __init__ ]]; then
        report_violation "$file" "$line" "$content" "SPI Protocols should not have __init__ methods - use @property accessors instead"
    fi
done < <(grep -rn "def __init__" src/ --include="*.py" || true)

# Check for hardcoded default values in method signatures (implementation details)
echo "Checking for hardcoded default values..."
while IFS=: read -r file line content; do
    # Skip test files and validation utilities (not core SPI)
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    if [[ $content =~ :[[:space:]]*str[[:space:]]*=[[:space:]]*[\"\'] || $content =~ :[[:space:]]*int[[:space:]]*=[[:space:]]*[0-9] ]]; then
        report_violation "$file" "$line" "$content" "SPI should not contain hardcoded default values - use Protocol contracts only"
    fi
done < <(grep -rn ": *[a-zA-Z]* *= *" src/ --include="*.py" || true)

# Check for legacy Dict[str, str] header usage (should use ProtocolEventHeaders)
echo "Checking for legacy Dict[str, str] header usage..."
while IFS=: read -r file line content; do
    if [[ $content =~ Dict\[str,\ str\] && $content =~ headers ]]; then
        report_violation "$file" "$line" "$content" "SPI should use ProtocolEventHeaders instead of Dict[str, str] for headers"
    fi
done < <(grep -rn "Dict\[str, str\]" src/ --include="*.py" || true)

# Check for concrete method implementations (methods with actual code, not just ...)
echo "Checking for concrete method implementations..."
TEMP_FILE=$(mktemp)
# Use the standalone docstring checker
python3 scripts/docstring_checker.py > "$TEMP_FILE" 2>/dev/null || true

while IFS=: read -r file line content; do
    if [[ -n "$content" && $content =~ def.*\(self.*\): ]]; then
        report_violation "$file" "$line" "$content" "SPI should not contain concrete method implementations"
    fi
done < "$TEMP_FILE"
rm "$TEMP_FILE"

# Check for imports that suggest implementation (not just type definitions)
echo "Checking for implementation imports..."
TEMP_IMPORT_FILE=$(mktemp)
# Use the standalone docstring checker for import violations
python3 scripts/docstring_checker.py > "$TEMP_IMPORT_FILE" 2>/dev/null || true

while IFS=: read -r file line content; do
    if [[ -n "$content" && ( $content =~ import\ (yaml|os|sys|json|asyncio|logging|requests) || $content =~ from\ (abc|enum|datetime) ) ]]; then
        # Special handling for datetime in core_types.py
        if [[ $content =~ "from datetime import datetime" && $file == *"core_types.py" ]]; then
            continue
        fi

        # Special handling for datetime imports within TYPE_CHECKING blocks
        if [[ $content =~ "from datetime import datetime" ]]; then
            # Check if this import is within a TYPE_CHECKING block
            type_checking_context=$(grep -B 5 -A 0 "from datetime import datetime" "$file" 2>/dev/null | grep -c "if TYPE_CHECKING:" || echo "0")
            if [[ $type_checking_context -gt 0 ]]; then
                continue
            fi
        fi

        report_violation "$file" "$line" "$content" "SPI should not import implementation libraries"
    fi
done < "$TEMP_IMPORT_FILE"
rm "$TEMP_IMPORT_FILE"

# Check for hardcoded values that suggest implementation logic (excluding docstring examples)
echo "Checking for implementation logic patterns..."
TEMP_LOGIC_FILE=$(mktemp)
# Use the standalone docstring checker for logic violations
python3 scripts/docstring_checker.py > "$TEMP_LOGIC_FILE" 2>/dev/null || true

while IFS=: read -r file line content; do
    # Skip test files and validation utilities (not core SPI)
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    if [[ -n "$content" && ( $content =~ print\( || $content =~ open\( || $content =~ json\.loads || $content =~ yaml\.load || $content =~ with\ open || $content =~ await.*\. || $content =~ =\ await ) ]]; then
        report_violation "$file" "$line" "$content" "SPI should not contain implementation logic"
    fi
done < "$TEMP_LOGIC_FILE"
rm "$TEMP_LOGIC_FILE"

# Summary
echo "----------------------------------------"
if [ $VIOLATIONS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ SPI purity validation PASSED${NC}"
    echo "All files contain only pure protocol definitions."
else
    echo -e "${RED}❌ SPI purity validation FAILED${NC}"
    echo "Found $VIOLATIONS_FOUND violations."
    echo
    echo -e "${YELLOW}NOTE:${NC} This validation excludes test files and validation utilities."
    echo -e "${YELLOW}NOTE:${NC} Remaining violations may be in docstring examples (acceptable)."
    echo
    echo "SPI (Service Provider Interface) should contain only:"
    echo "• Protocol definitions using typing.Protocol"
    echo "• Type aliases using typing.Literal"
    echo "• Type unions and generic types"
    echo "• Abstract method signatures with '...' implementation"
    echo
    echo "SPI should NOT contain:"
    echo "• Concrete class implementations"
    echo "• @dataclass decorators (use @runtime_checkable Protocol instead)"
    echo "• dataclasses imports (not needed for pure protocols)"
    echo "• __init__ methods in Protocol classes (use @property accessors)"
    echo "• Hardcoded default values (e.g., str = 'default')"
    echo "• Legacy Dict[str, str] headers (use ProtocolEventHeaders)"
    echo "• Enum classes (use Literal instead)"
    echo "• ABC classes (use Protocol instead)"
    echo "• Method implementations with actual logic"
    echo "• Implementation library imports"
    echo "• Business logic or concrete behavior"
    exit 1
fi
