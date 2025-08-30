#!/bin/bash
# Validate No Deprecated Code - Prevent legacy patterns and deprecated keywords
#
# This script ensures the codebase doesn't contain deprecated patterns,
# legacy code, or outdated implementations that should be removed.

set -euo pipefail

echo "🔍 Validating for deprecated/legacy code..."

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
    
    echo -e "${RED}❌ DEPRECATED CODE${NC} in ${file}:${line}"
    echo -e "   ${YELLOW}Found:${NC} ${violation}"
    echo -e "   ${YELLOW}Issue:${NC} ${message}"
    echo
    VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
}

# Check for deprecated keywords in comments
echo "Checking for deprecated/legacy keywords in comments..."
while IFS=: read -r file line content; do
    # Skip test files and validation utilities (not core SPI)
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    
    if [[ $content =~ (deprecated|legacy|DEPRECATED|LEGACY|TODO.*deprecated|TODO.*legacy|FIXME.*deprecated|FIXME.*legacy) ]]; then
        report_violation "$file" "$line" "$content" "Remove deprecated/legacy code - clean up or modernize implementation"
    fi
done < <(grep -rn -E "(deprecated|legacy|DEPRECATED|LEGACY)" src/ --include="*.py" || true)

# Check for specific deprecated patterns
echo "Checking for deprecated type aliases..."
while IFS=: read -r file line content; do
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    
    if [[ $content =~ (RegistrationStatus|ServiceStatus|Legacy.*=|.*Status.*=.*Literal.*registered.*unregistered) ]]; then
        report_violation "$file" "$line" "$content" "Replace deprecated status types with comprehensive protocol definitions"
    fi
done < <(grep -rn -E "(RegistrationStatus|ServiceStatus|Legacy.*=)" src/ --include="*.py" || true)

# Check for deprecated import patterns
echo "Checking for deprecated import patterns..."
while IFS=: read -r file line content; do
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    
    if [[ $content =~ (from.*legacy|import.*legacy|from.*deprecated|import.*deprecated) ]]; then
        report_violation "$file" "$line" "$content" "Remove deprecated imports - update to modern protocol imports"
    fi
done < <(grep -rn -E "(from.*legacy|import.*legacy|from.*deprecated|import.*deprecated)" src/ --include="*.py" || true)

# Check for deprecated class names
echo "Checking for deprecated class/function names..."
while IFS=: read -r file line content; do
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    
    if [[ $content =~ (class.*Legacy|def.*legacy|class.*Deprecated|def.*deprecated) ]]; then
        report_violation "$file" "$line" "$content" "Remove deprecated classes/functions - migrate to modern implementations"
    fi
done < <(grep -rn -E "(class.*Legacy|def.*legacy|class.*Deprecated|def.*deprecated)" src/ --include="*.py" || true)

# Check for old-style type hints
echo "Checking for old-style type patterns..."
while IFS=: read -r file line content; do
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    
    # Check for Dict instead of dict (Python 3.9+ style)
    if [[ $content =~ (Dict\[|List\[|Tuple\[|Set\[) && ! $content =~ (from typing import|import.*Dict|import.*List|import.*Tuple|import.*Set) ]]; then
        # Only flag if it's not an import line
        if [[ ! $content =~ (from typing|import) ]]; then
            report_violation "$file" "$line" "$content" "Use lowercase built-in types (dict, list, tuple, set) instead of typing.Dict, etc."
        fi
    fi
done < <(grep -rn -E "(Dict\[|List\[|Tuple\[|Set\[)" src/ --include="*.py" || true)

# Check for hardcoded legacy values
echo "Checking for hardcoded legacy values..."
while IFS=: read -r file line content; do
    if [[ $file == *"/test_"* || $file == *"validation"* ]]; then
        continue
    fi
    
    if [[ $content =~ (\"legacy\"|\'legacy\'|\"deprecated\"|\'deprecated\'|\"old_\"|\'old_\'|\"v1\"|\'v1\'|\"version_1\"|\'version_1\') ]]; then
        # Skip if it's in a docstring or comment
        if [[ ! $content =~ (^\s*#|^\s*\"\"\"|^\s*\'\'\') ]]; then
            report_violation "$file" "$line" "$content" "Remove hardcoded legacy/deprecated values from code"
        fi
    fi
done < <(grep -rn -E "(\"legacy\"|'legacy'|\"deprecated\"|'deprecated'|\"old_\"|'old_'|\"v1\"|'v1'|\"version_1\"|'version_1')" src/ --include="*.py" || true)

# Summary
echo "----------------------------------------"
if [ $VIOLATIONS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No deprecated/legacy code validation PASSED${NC}"
    echo "Codebase is clean of deprecated patterns."
else
    echo -e "${RED}❌ Deprecated/legacy code validation FAILED${NC}"
    echo "Found $VIOLATIONS_FOUND violations."
    echo
    echo -e "${YELLOW}ACTION REQUIRED:${NC}"
    echo "• Remove all deprecated/legacy code comments and patterns"
    echo "• Replace deprecated type aliases with modern protocol definitions"
    echo "• Update old-style type hints to use built-in types (Python 3.9+)"
    echo "• Clean up hardcoded legacy values"
    echo "• Migrate deprecated classes/functions to modern implementations"
    echo
    echo "This validation enforces a clean, modern codebase without technical debt."
    exit 1
fi