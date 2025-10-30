# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- _No changes yet_

### Changed
- _No changes yet_

### Deprecated
- _No changes yet_

### Removed
- _No changes yet_

### Fixed
- _No changes yet_

### Security
- _No changes yet_

## [0.2.0] - 2025-10-30

### Added
- **ProtocolContainer** - Generic value container protocol with metadata support (Issue #1)
- **ProtocolServiceResolver** - Service resolution interface for dependency injection
- **ProtocolContract** - Full contract interface with versioning and serialization (Issue #3)
- **ProtocolOnexError** - Standardized error object protocol with categories and context (Issue #4)
- **ProtocolOrchestratorNode** - Node-specific protocol for workflow coordination (Issue #8)
- **ProtocolReducerNode** - Node-specific protocol for data aggregation (Issue #8)
- **ProtocolEffectNode** - Node-specific protocol for side-effecting operations (Issue #8)
- **ProtocolComputeNode** - Node-specific protocol for pure transformations (Issue #8)
- **ProtocolEnvelope** - Alias for ProtocolOnexEnvelope for naming consistency (Issue #5)
- **Comprehensive Tests** - 46 tests covering all new protocols (100% pass rate)
- **Documentation Updates** - API reference documentation for all new protocols
- **SPI Validation** - All new protocols validated for purity (0 violations)

### Changed
- **Protocol Count** - Increased from 165 to 176 protocols (+11)
- **Container Domain** - Updated from 21 to 14 protocols with generic containers
- **ONEX Domain** - Added 4 node-specific protocols for type-safe node execution
- **Type Definitions** - Expanded to 14 comprehensive type modules

### Fixed
- **Protocol Import Consistency** - Standardized to use `typing.Protocol` instead of `typing_extensions`
- **Type Checking Issues** - Removed unused type ignore comments for mypy compliance

## [0.1.0] - 2025-01-30

### Added
- **Complete Documentation Rebuild** - Comprehensive API reference with 165 protocols across 22 domains
- **MIT License** - Open source licensing for community use
- **Badge System** - Repository status indicators for license, Python version, code style, and more
- **Pre-commit Hooks** - Enhanced SPI-specific validation with .git directory exclusion
- **Protocol Type Safety** - Improved type definitions with UUID types for better type safety
- **Memory Protocols Guide** - Comprehensive memory system implementation patterns
- **Protocol Composition Patterns** - Advanced protocol design patterns and selection guide
- **Node Templates** - ONEX 4-node architecture templates
- **Standards Documentation** - Code quality guidelines and best practices
- **Changelog** - Version history and release notes following Keep a Changelog format
- **Link Validation Script** - Automated markdown link checking for documentation integrity

### Changed
- **Repository Structure** - Complete documentation reorganization and consolidation
- **Documentation Links** - Fixed all 137 markdown links for perfect navigation
- **Integration Guide** - Merged into comprehensive developer guide
- **Memory Guide** - Moved to examples directory for better categorization
- **Pre-commit Configuration** - Added .git directory exclusion to prevent formatter issues

### Removed
- **Duplicate Documentation** - Consolidated integration guide into developer guide
- **Empty Directories** - Cleaned up unused guides and integration directories
- **Broken Links** - Fixed all 77 broken markdown links
- **Placeholder Content** - Replaced template placeholders with real protocol references

### Fixed
- **Relative Path Issues** - Added proper `../` prefixes for cross-directory links
- **Non-existent File References** - Removed links to files that don't exist
- **Template Placeholders** - Replaced placeholder links with actual protocol references
- **Validation Directory** - Updated references to non-existent example files
- **Documentation Navigation** - All 137 links now work perfectly

---

**Legend:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes
