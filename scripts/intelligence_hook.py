#!/usr/bin/env python3
# type: ignore
"""
Enhanced Intelligence Hook - Python Implementation

This script processes git changes and generates intelligence documents for the Archon system.
It analyzes commits, correlates changes across repositories, and submits intelligence data
via the Archon Intelligence API.

Version: 3.1.0 (Python Implementation with Poetry)
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Sized, cast

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback if pydantic not available - use typing.Protocol
    from typing import Protocol

    class BaseModel(Protocol):  # type: ignore[misc,no-redef]
        """Fallback BaseModel when pydantic is not available."""

        def model_dump(self, mode: str = "python") -> dict[str, Any]: ...
        def model_validate(self, data: Any) -> Any: ...

    PYDANTIC_AVAILABLE = False


def json_datetime_serializer(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


# Try to import httpx first (available in most ONEX repositories)
# Fall back to requests as a backup
try:
    import httpx

    HTTP_CLIENT = "httpx"
except ImportError:
    try:
        import requests

        HTTP_CLIENT = "requests"
    except ImportError:
        print(
            "❌ Error: Neither httpx nor requests is available. Please install one of these dependencies.",
            file=sys.stderr,
        )
        sys.exit(1)

# Intelligence Models - Included inline for cross-repository compatibility
from enum import Enum

try:
    from pydantic import BaseModel, Field

    PYDANTIC_AVAILABLE = True
except ImportError:
    print(
        "❌ Error: Pydantic is required for intelligence hooks but not available.",
        file=sys.stderr,
    )
    sys.exit(1)


class IntelligenceDocumentType(str, Enum):
    """Types of intelligence documents"""

    INTELLIGENCE = "intelligence"
    CORRELATION = "correlation"
    SECURITY_ANALYSIS = "security_analysis"
    CODE_ANALYSIS = "code_analysis"


class AnalysisType(str, Enum):
    """Types of analysis performed"""

    ENHANCED_CODE_CHANGES_WITH_CORRELATION = "enhanced_code_changes_with_correlation"
    BASIC_CODE_CHANGES = "basic_code_changes"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_ANALYSIS = "performance_analysis"


class RiskLevel(str, Enum):
    """Risk assessment levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityStatus(str, Enum):
    """Security scan results"""

    CLEAN = "clean"
    WARNINGS = "warnings"
    ISSUES = "issues"
    CRITICAL = "critical"


class IntelligenceMetadata(BaseModel):
    """Metadata for intelligence documents"""

    timestamp: datetime = Field(..., description="Analysis timestamp")
    repository: str = Field(..., description="Repository name")
    branch: str = Field(..., description="Git branch")
    commit: str = Field(..., description="Commit hash")
    author: str = Field(..., description="Commit author")
    hook_version: str = Field(..., description="Intelligence hook version")


class ChangeSummary(BaseModel):
    """Summary of code changes"""

    commit_message: str = Field(..., description="Git commit message")
    files_changed: int = Field(..., description="Number of files modified")
    lines_added: int = Field(0, description="Lines added")
    lines_removed: int = Field(0, description="Lines removed")
    security_status: SecurityStatus = Field(
        SecurityStatus.CLEAN, description="Security scan result"
    )


class ImpactAssessment(BaseModel):
    """Assessment of change impact"""

    coordination_required: bool = Field(
        False, description="Whether coordination is needed"
    )
    risk_level: RiskLevel = Field(RiskLevel.LOW, description="Overall risk level")
    affected_systems: List[str] = Field(
        default_factory=list, description="Systems that may be affected"
    )
    breaking_changes: List[str] = Field(
        default_factory=list, description="Potential breaking changes"
    )


class CrossRepositoryCorrelation(BaseModel):
    """Cross-repository correlation analysis"""

    enabled: bool = Field(
        True, description="Whether correlation analysis was performed"
    )
    correlation_id: str = Field(..., description="Unique correlation identifier")
    temporal_correlations: List[dict[str, Any]] = Field(
        default_factory=list, description="Time-based correlations"
    )
    semantic_correlations: List[dict[str, Any]] = Field(
        default_factory=list, description="Semantic correlations"
    )
    breaking_changes: List[dict[str, Any]] = Field(
        default_factory=list, description="Breaking change correlations"
    )
    impact_assessment: ImpactAssessment = Field(..., description="Impact assessment")


class SecurityAndPrivacy(BaseModel):
    """Security and privacy analysis"""

    sensitive_patterns: List[str] = Field(
        default_factory=list, description="Detected sensitive patterns"
    )
    security_score: float = Field(
        1.0, ge=0.0, le=1.0, description="Security confidence score"
    )
    privacy_concerns: List[str] = Field(
        default_factory=list, description="Privacy-related concerns"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Security recommendations"
    )


class TechnicalAnalysis(BaseModel):
    """Technical code analysis"""

    complexity_score: float = Field(0.0, ge=0.0, description="Code complexity score")
    quality_score: float = Field(1.0, ge=0.0, le=1.0, description="Code quality score")
    maintainability: str = Field("good", description="Maintainability assessment")
    test_coverage: Optional[float] = Field(None, description="Test coverage percentage")
    architecture_compliance: dict[str, Any] = Field(
        default_factory=dict, description="Architecture compliance"
    )


class IntelligenceDocumentContent(BaseModel):
    """Complete intelligence document content"""

    analysis_type: AnalysisType = Field(..., description="Type of analysis performed")
    metadata: IntelligenceMetadata = Field(..., description="Document metadata")
    change_summary: ChangeSummary = Field(..., description="Summary of changes")
    cross_repository_correlation: CrossRepositoryCorrelation = Field(
        ..., description="Correlation analysis"
    )
    security_and_privacy: SecurityAndPrivacy = Field(
        ..., description="Security analysis"
    )
    technical_analysis: Optional[TechnicalAnalysis] = Field(
        None, description="Technical analysis"
    )
    raw_diff: Optional[str] = Field(None, description="Raw git diff content")


class MCPCreateDocumentRequest(BaseModel):
    """MCP request for creating intelligence documents"""

    method: str = Field("create_document", description="MCP method name")
    params: dict[str, Any] = Field(..., description="MCP method parameters")

    @classmethod
    def create_intelligence_document(
        cls, project_id: str, content: IntelligenceDocumentContent, repository_name: str
    ) -> "MCPCreateDocumentRequest":
        """Create an MCP request for intelligence document"""
        return cls(
            method="create_document",
            params={
                "project_id": project_id,
                "title": f"Intelligence: {repository_name} Code Changes with Analysis",
                "document_type": "intelligence",
                "content": content.model_dump(),
                "author": "Intelligence Hook v3.1",
                "tags": [
                    "intelligence",
                    "automation",
                    "git-hook",
                    repository_name.lower(),
                ],
            },
        )


class MCPResponse(BaseModel):
    """Standard MCP response"""

    success: bool = Field(..., description="Operation success status")
    document_id: Optional[str] = Field(None, description="Created document ID")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")


class IntelligenceServiceRequest(BaseModel):
    """Request for intelligence service document processing"""

    content: str = Field(..., description="Raw document content as JSON string")
    source_path: str = Field(..., description="Source path identifier")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    store_entities: bool = Field(
        True, description="Whether to store extracted entities"
    )
    extract_relationships: bool = Field(
        True, description="Whether to extract relationships"
    )
    trigger_freshness_analysis: bool = Field(
        True, description="Whether to trigger freshness analysis"
    )

    @classmethod
    def from_intelligence_document(
        cls,
        content: IntelligenceDocumentContent,
        repository_name: str,
        commit_hash: str,
    ) -> "IntelligenceServiceRequest":
        """Create intelligence service request from document content"""
        return cls(
            content=json.dumps(
                content.model_dump(), indent=2, default=json_datetime_serializer
            ),
            source_path=f"git://{repository_name}/commit/{commit_hash}",
            metadata={
                "type": "intelligence_document",
                "repository": repository_name,
                "commit_hash": commit_hash,
                "timestamp": content.metadata.timestamp.isoformat(),
                "generated_by": "intelligence_hook_v3.1",
            },
        )


# Helper functions
def validate_intelligence_document(
    content: dict[str, Any],
) -> IntelligenceDocumentContent:
    """Validate and parse intelligence document content"""
    return IntelligenceDocumentContent(**content)


def create_intelligence_metadata(
    repository: str, branch: str, commit: str, author: str, hook_version: str = "3.1"
) -> IntelligenceMetadata:
    """Create intelligence metadata with current timestamp"""
    return IntelligenceMetadata(
        timestamp=datetime.now(),
        repository=repository,
        branch=branch,
        commit=commit,
        author=author,
        hook_version=f"intelligence_hook_v{hook_version}",
    )


def create_change_summary(
    commit_message: str,
    files_changed: int,
    lines_added: int = 0,
    lines_removed: int = 0,
    security_status: SecurityStatus = SecurityStatus.CLEAN,
) -> ChangeSummary:
    """Create change summary from git information"""
    return ChangeSummary(
        commit_message=commit_message,
        files_changed=files_changed,
        lines_added=lines_added,
        lines_removed=lines_removed,
        security_status=security_status,
    )


# Models are now always available
CONFIG_AVAILABLE = False  # No centralized config in other repositories


def get_archon_config() -> Any:
    """Dummy function for archon config - not available in SPI repo."""
    return None


class IntelligenceHook:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the intelligence hook with configuration."""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()

        # API configuration - use centralized config system if available
        if CONFIG_AVAILABLE:
            try:
                archon_config = get_archon_config()
                # Use Intelligence service for document creation (port 8053)
                self.api_url = f"http://localhost:{archon_config.intelligence_service.port}/extract/document"
                self.use_mcp_format = False
                self.logger.info(
                    f"Using centralized config - Intelligence service: {self.api_url}"
                )
            except Exception as e:
                self.logger.warning(f"Failed to load centralized config: {e}")
                # Fallback to legacy configuration - use intelligence service
                self.api_url = "http://localhost:8053/extract/document"
                self.use_mcp_format = False
        else:
            # Legacy configuration loading
            archon_endpoint = self.config.get(
                "archon_mcp_endpoint", "http://localhost:8051/mcp"
            )
            intelligence_api_url = self.config.get("intelligence_api", {}).get(
                "url", "http://localhost:8053/extract/document"
            )

            # Use MCP endpoint for document creation (proper format)
            if "archon_mcp_endpoint" in self.config:
                self.api_url = archon_endpoint
                self.use_mcp_format = True
            else:
                self.api_url = intelligence_api_url
                self.use_mcp_format = False

        self.api_timeout = self.config.get("intelligence_api", {}).get("timeout", 10)
        self.retry_attempts = self.config.get("intelligence_api", {}).get(
            "retry_attempts", 2
        )

        # Project ID for document creation
        self.project_id = self.config.get("archon_project_id")

        # Feature flags
        self.correlations_enabled = self.config.get("features", {}).get(
            "correlations", True
        )
        self.file_analysis_enabled = self.config.get("features", {}).get(
            "file_analysis", True
        )
        self.commit_analysis_enabled = self.config.get("features", {}).get(
            "commit_analysis", True
        )

        # Repository configuration
        self.repo_root = Path.cwd()
        self.repo_name = self.repo_root.name

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "intelligence_api": {
                "url": "http://localhost:8053/extract/document",
                "timeout": 30,
                "retry_attempts": 3,
            },
            "features": {
                "correlations": True,
                "file_analysis": True,
                "commit_analysis": True,
                "cross_repo_analysis": True,
            },
            "analysis": {
                "max_commits": 10,
                "max_files_per_commit": 50,
                "correlation_lookback_days": 3,
                "min_correlation_strength": 0.3,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
                # Merge with defaults
                self._deep_merge(default_config, file_config)
            except Exception as e:
                print(f"Warning: Failed to load config from {config_path}: {e}")

        return default_config

    def _deep_merge(self, base: dict[str, Any], update: dict[str, Any]) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("intelligence_hook")
        log_level = getattr(
            logging, self.config.get("logging", {}).get("level", "INFO").upper()
        )
        logger.setLevel(log_level)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                self.config.get("logging", {}).get(
                    "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def run_git_command(self, cmd: List[str], cwd: Optional[Path] = None) -> str:
        """Run a git command and return the output."""
        self.logger.debug(
            f"Executing git command: {' '.join(cmd)} in {cwd or self.repo_root}"
        )
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            self.logger.debug(
                f"Git command output ({len(output)} chars): {output[:200]}..."
            )
            return output
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {' '.join(cmd)}, error: {e.stderr}")
            return ""

    def get_commit_info(self, commit_hash: str) -> dict[str, Any]:
        """Get detailed information about a commit."""
        self.logger.debug(f"Getting commit info for: {commit_hash}")
        try:
            # Get commit metadata
            commit_data = self.run_git_command(
                [
                    "git",
                    "show",
                    "--format=%H|%s|%an|%ae|%at|%B",
                    "--name-status",
                    commit_hash,
                ]
            )

            if not commit_data:
                self.logger.warning(f"No commit data returned for {commit_hash}")
                return {}

            lines = commit_data.split("\n")
            header = lines[0].split("|")
            self.logger.debug(f"Parsed commit header: {len(header)} fields")

            if len(header) < 6:
                self.logger.warning(
                    f"Invalid commit header format for {commit_hash}: {header}"
                )
                return {}

            commit_hash, subject, author_name, author_email, timestamp = header[:5]
            commit_message = "|".join(header[5:]) if len(header) > 5 else subject

            # Parse timestamp safely - handle cases where it might not be a valid integer
            try:
                parsed_timestamp = int(timestamp)
            except (ValueError, TypeError) as e:
                self.logger.warning(
                    f"Invalid timestamp format '{timestamp}' for commit {commit_hash}, using current time: {e}"
                )
                parsed_timestamp = int(time.time())

            # Parse file changes
            file_changes = []
            in_files = False
            for line_idx, line in enumerate(lines[1:], 1):
                if line.strip() == "":
                    in_files = True
                    continue
                if in_files and "\t" in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        status = parts[0]
                        filename = parts[1]
                        file_changes.append(
                            {
                                "status": status,
                                "filename": filename,
                                "file_type": Path(filename).suffix.lstrip(".")
                                or "no_extension",
                            }
                        )

            self.logger.debug(
                f"Parsed {len(file_changes)} file changes for commit {commit_hash}"
            )

            return {
                "commit_hash": commit_hash,
                "subject": subject,
                "message": commit_message,
                "author_name": author_name,
                "author_email": author_email,
                "timestamp": parsed_timestamp,
                "file_changes": file_changes,
            }
        except Exception as e:
            self.logger.error(f"Failed to get commit info for {commit_hash}: {e}")
            return {}

    def analyze_file_changes(
        self, file_changes: List[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze file changes to extract patterns and technologies."""
        self.logger.debug(f"Analyzing {len(file_changes)} file changes")
        if not self.file_analysis_enabled:
            self.logger.debug("File analysis disabled, returning empty result")
            return {}

        file_types: dict[str, int] = {}
        directories = set()
        technologies_detected: list[str] = []

        for change in file_changes:
            filename = change.get("filename", "")
            file_type = change.get("file_type", "unknown")

            # Count file types
            file_types[file_type] = file_types.get(file_type, 0) + 1

            # Extract directories
            if "/" in filename:
                directories.add(filename.split("/")[0])

            # Detect technologies based on file patterns
            if file_type in ["py", "pyx", "pyi"]:
                technologies_detected.append("Python")
            elif file_type in ["js", "jsx", "ts", "tsx"]:
                technologies_detected.append("JavaScript/TypeScript")
            elif file_type in ["rs", "toml"] and "Cargo" in filename:
                technologies_detected.append("Rust")
            elif file_type in ["go", "mod"]:
                technologies_detected.append("Go")
            elif file_type == "yml" or file_type == "yaml":
                if "docker" in filename.lower() or "compose" in filename.lower():
                    technologies_detected.append("Docker")
                else:
                    technologies_detected.append("YAML Configuration")
            elif filename == "Dockerfile" or filename.startswith("Dockerfile."):
                technologies_detected.append("Docker")
            elif filename in ["package.json", "package-lock.json"]:
                technologies_detected.append("Node.js")
            elif filename in ["pyproject.toml", "setup.py", "requirements.txt"]:
                technologies_detected.append("Python Packaging")

        result = {
            "file_types": file_types,
            "directories_affected": list(directories),
            "technologies_detected": list(set(technologies_detected)),
            "total_files_changed": len(file_changes),
        }
        self.logger.debug(
            f"File analysis complete: {len(result['technologies_detected'])} technologies, {len(result['directories_affected'])} directories"
        )
        return result

    def find_cross_repo_correlations(
        self, commit_info: dict[str, Any]
    ) -> List[dict[str, Any]]:
        """Find correlations with other repositories."""
        self.logger.debug(
            f"Finding cross-repo correlations for commit: {commit_info.get('commit_hash', 'unknown')}"
        )
        if not self.correlations_enabled:
            self.logger.debug("Correlations disabled, returning empty result")
            return []

        correlations: list[dict[str, Any]] = []

        try:
            # Extract keywords from commit message and subject
            message_text = f"{commit_info.get('subject', '')} {commit_info.get('message', '')}".lower()
            keywords = []
            self.logger.debug(f"Processing commit message: {message_text[:100]}...")

            # Extract meaningful keywords (longer than 3 chars, not common words)
            common_words = {
                "the",
                "and",
                "for",
                "are",
                "but",
                "not",
                "you",
                "all",
                "can",
                "her",
                "was",
                "one",
                "our",
                "had",
                "day",
                "get",
                "use",
                "man",
                "new",
                "now",
                "way",
                "may",
                "say",
                "each",
                "which",
                "their",
                "time",
                "will",
                "about",
                "would",
                "there",
                "could",
                "other",
                "after",
                "first",
                "well",
                "many",
                "some",
                "what",
                "only",
                "his",
                "has",
                "more",
                "two",
                "like",
                "into",
                "him",
                "see",
                "how",
                "its",
                "who",
                "than",
                "been",
                "call",
                "come",
                "made",
                "over",
                "also",
                "back",
                "were",
                "out",
                "very",
                "your",
                "when",
                "much",
                "before",
                "through",
                "just",
                "where",
                "too",
                "any",
                "same",
                "right",
                "under",
                "while",
            }

            for word in message_text.split():
                word = word.strip('.,!?";()[]{}:')
                if len(word) > 3 and word not in common_words:
                    keywords.append(word)

            if not keywords:
                self.logger.debug("No meaningful keywords found in commit message")
                return correlations

            self.logger.debug(f"Extracted {len(keywords)} keywords: {keywords[:5]}")

            # Look for sibling repositories
            parent_dir = self.repo_root.parent
            sibling_repos = [
                s
                for s in parent_dir.iterdir()
                if (s.is_dir() and s != self.repo_root and (s / ".git").exists())
            ]
            self.logger.debug(
                f"Found {len(sibling_repos)} sibling repositories to check"
            )

            for sibling in sibling_repos:
                self.logger.debug(
                    f"Checking correlations with repository: {sibling.name}"
                )
                if (
                    sibling.is_dir()
                    and sibling != self.repo_root
                    and (sibling / ".git").exists()
                ):

                    # Search for similar commits in sibling repos
                    matching_commits = self._find_matching_commits_in_repo(
                        sibling, keywords
                    )

                    if matching_commits:
                        strength = min(len(matching_commits) * 0.2, 1.0)
                        self.logger.debug(
                            f"Found {len(matching_commits)} matching commits in {sibling.name}, strength: {strength}"
                        )
                        correlations.append(
                            {
                                "type": "semantic_keyword",
                                "repository": sibling.name,
                                "shared_keywords": keywords[:5],  # Limit keywords
                                "matching_commits": matching_commits[
                                    :3
                                ],  # Limit matches
                                "correlation_strength": strength,
                            }
                        )
                    else:
                        self.logger.debug(
                            f"No matching commits found in {sibling.name}"
                        )

        except Exception as e:
            self.logger.error(f"Failed to find cross-repo correlations: {e}")

        return correlations

    def _find_matching_commits_in_repo(
        self, repo_path: Path, keywords: List[str]
    ) -> List[dict[str, Any]]:
        """Find matching commits in a specific repository."""
        matching_commits = []

        try:
            # Build grep pattern for keywords
            grep_pattern = "|".join(
                keywords[:5]
            )  # Limit keywords to avoid long commands

            # Search recent commits for keyword matches
            cmd = [
                "git",
                "log",
                "--since=3 days ago",
                f"--grep={grep_pattern}",
                "--pretty=format:%H|%s|%an",
                "--max-count=5",
            ]

            output = self.run_git_command(cmd, cwd=repo_path)

            if output:
                for line in output.split("\n"):
                    parts = line.split("|")
                    if len(parts) >= 3:
                        matching_commits.append(
                            {
                                "commit": parts[0],
                                "message": parts[1],
                                "author": parts[2],
                            }
                        )

        except Exception as e:
            self.logger.debug(f"Failed to search commits in {repo_path}: {e}")

        return matching_commits

    def build_intelligence_document(self, commits_to_push: List[str]) -> dict[str, Any]:
        """Build the complete intelligence document."""
        self.logger.info(
            f"Building intelligence document for {len(commits_to_push)} commits"
        )

        # Get commit information
        commits_data = []
        all_file_changes = []
        all_correlations = []

        for idx, commit_hash in enumerate(commits_to_push, 1):
            self.logger.debug(
                f"Processing commit {idx}/{len(commits_to_push)}: {commit_hash}"
            )
            commit_info = self.get_commit_info(commit_hash)
            if commit_info:
                commits_data.append(commit_info)
                file_changes = commit_info.get("file_changes", [])
                all_file_changes.extend(file_changes)
                self.logger.debug(
                    f"Commit {commit_hash} has {len(file_changes)} file changes"
                )

                # Find correlations for this commit
                if self.correlations_enabled:
                    correlations = self.find_cross_repo_correlations(commit_info)
                    all_correlations.extend(correlations)
                    self.logger.debug(
                        f"Found {len(correlations)} correlations for commit {commit_hash}"
                    )
            else:
                self.logger.warning(f"Failed to get commit info for {commit_hash}")

        if not commits_data:
            self.logger.warning("No valid commits found to analyze")
            return {}

        self.logger.info(
            f"Successfully processed {len(commits_data)} commits with {len(all_file_changes)} total file changes"
        )

        # Analyze file changes
        self.logger.debug("Starting file analysis")
        file_analysis = self.analyze_file_changes(all_file_changes)

        # Build the intelligence document
        self.logger.debug("Building final intelligence document structure")
        intelligence_doc = {
            "repository_name": self.repo_name,
            "repository_path": str(self.repo_root),
            "timestamp": int(time.time()),
            "commit_hash": (
                commits_data[0]["commit_hash"] if commits_data else "unknown"
            ),
            "commits_analyzed": len(commits_data),
            "intelligence_data": {
                "technologies_detected": file_analysis.get("technologies_detected", []),
                "architecture_patterns": self._detect_architecture_patterns(
                    all_file_changes
                ),
                "file_analysis": file_analysis,
                "commit_analysis": {
                    "total_commits": len(commits_data),
                    "commits": commits_data,
                    "summary": self._generate_commit_summary(commits_data),
                },
                "correlation_analysis": {
                    "temporal_correlations": all_correlations,
                    "cross_repository_insights": self._generate_cross_repo_insights(
                        all_correlations
                    ),
                },
            },
        }

        # Log document summary
        tech_count = len(intelligence_doc["intelligence_data"]["technologies_detected"])
        pattern_count = len(
            intelligence_doc["intelligence_data"]["architecture_patterns"]
        )
        correlation_count = len(
            intelligence_doc["intelligence_data"]["correlation_analysis"][
                "temporal_correlations"
            ]
        )

        self.logger.info(
            f"Intelligence document built: {tech_count} technologies, {pattern_count} patterns, {correlation_count} correlations"
        )
        self.logger.debug(f"Document size: {len(str(intelligence_doc))} characters")

        return intelligence_doc

    def _detect_architecture_patterns(
        self, file_changes: List[dict[str, Any]]
    ) -> List[str]:
        """Detect architectural patterns from file changes."""
        patterns = []
        filenames = [change.get("filename", "") for change in file_changes]

        # Microservices patterns
        if any("service" in f.lower() for f in filenames):
            patterns.append("Microservices")

        # API patterns
        if any("api" in f.lower() or "endpoint" in f.lower() for f in filenames):
            patterns.append("REST API")

        # Database patterns
        if any(
            "model" in f.lower() or "schema" in f.lower() or "migration" in f.lower()
            for f in filenames
        ):
            patterns.append("Database Layer")

        # Frontend patterns
        if any(f.endswith((".tsx", ".jsx", ".vue", ".svelte")) for f in filenames):
            patterns.append("Component-Based UI")

        # Configuration patterns
        if any(
            f.endswith((".yml", ".yaml", ".toml", ".json")) and "config" in f.lower()
            for f in filenames
        ):
            patterns.append("Configuration Management")

        # Docker patterns
        if any("docker" in f.lower() or f == "Dockerfile" for f in filenames):
            patterns.append("Containerization")

        return patterns

    def _generate_commit_summary(self, commits_data: List[dict[str, Any]]) -> str:
        """Generate a summary of the commits."""
        if not commits_data:
            return "No commits to analyze"

        # Extract action keywords
        actions = []
        for commit in commits_data:
            subject = commit.get("subject", "").lower()
            if subject.startswith(("feat:", "feature:")):
                actions.append("feature development")
            elif subject.startswith(("fix:", "bugfix:")):
                actions.append("bug fixes")
            elif subject.startswith(("refactor:", "refact:")):
                actions.append("code refactoring")
            elif subject.startswith(("docs:", "doc:")):
                actions.append("documentation updates")
            elif subject.startswith(("test:", "tests:")):
                actions.append("testing improvements")
            elif subject.startswith(("chore:", "build:", "ci:")):
                actions.append("maintenance tasks")
            else:
                actions.append("general development")

        unique_actions = list(set(actions))
        if len(unique_actions) == 1:
            return f"Batch commit focused on {unique_actions[0]}"
        else:
            return f"Mixed development including {', '.join(unique_actions)}"

    def _generate_cross_repo_insights(
        self, correlations: List[dict[str, Any]]
    ) -> List[str]:
        """Generate insights from cross-repository correlations."""
        insights: list[str] = []

        if not correlations:
            return insights

        # Group correlations by repository
        repo_correlations: dict[str, list[dict[str, Any]]] = {}
        for corr in correlations:
            repo = corr.get("repository", "unknown")
            if repo not in repo_correlations:
                repo_correlations[repo] = []
            repo_correlations[repo].append(corr)

        # Generate insights
        for repo, corrs in repo_correlations.items():
            strength = sum(c.get("correlation_strength", 0) for c in corrs) / len(corrs)
            if strength > 0.5:
                insights.append(
                    f"Strong correlation with {repo} (strength: {strength:.2f})"
                )
            elif strength > 0.3:
                insights.append(
                    f"Moderate correlation with {repo} (strength: {strength:.2f})"
                )

        if len(repo_correlations) > 2:
            insights.append(
                f"Cross-repository development activity detected across {len(repo_correlations)} repositories"
            )

        return insights

    def _create_intelligence_document_content(
        self, doc: dict[str, Any]
    ) -> IntelligenceDocumentContent:
        """Transform dictionary document into validated Pydantic IntelligenceDocumentContent."""
        if not PYDANTIC_AVAILABLE:
            raise ImportError(
                "Pydantic models not available - cannot create validated document"
            )

        # Return type is IntelligenceDocumentContent when Pydantic is available

        # Get basic document info
        repository_name = doc.get("repository_name", "unknown")
        commit_hash = doc.get("commit_hash", "unknown")
        timestamp = doc.get("timestamp", int(time.time()))

        # Extract commits data
        intelligence_data = doc.get("intelligence_data", {})
        commit_analysis = intelligence_data.get("commit_analysis", {})
        commits = commit_analysis.get("commits", [])

        # Get first commit for metadata (most recent)
        first_commit = commits[0] if commits else {}
        branch = first_commit.get("branch", "main")
        author = first_commit.get("author", "unknown")
        commit_message = first_commit.get("commit_message", "Multiple commits")

        # Create metadata using helper function
        metadata = create_intelligence_metadata(
            repository=repository_name,
            branch=branch,
            commit=commit_hash,
            author=author,
            hook_version="3.1",
        )

        # Create change summary
        files_changed = sum(len(commit.get("file_changes", [])) for commit in commits)
        lines_added = sum(
            change.get("additions", 0)
            for commit in commits
            for change in commit.get("file_changes", [])
        )
        lines_removed = sum(
            change.get("deletions", 0)
            for commit in commits
            for change in commit.get("file_changes", [])
        )

        change_summary = create_change_summary(
            commit_message=commit_message,
            files_changed=files_changed,
            lines_added=lines_added,
            lines_removed=lines_removed,
            security_status=SecurityStatus.CLEAN,
        )

        # Create correlation analysis
        correlation_data = intelligence_data.get("correlation_analysis", {})
        temporal_correlations = correlation_data.get("temporal_correlations", [])
        cross_repo_insights = correlation_data.get("cross_repository_insights", [])

        # Determine impact assessment
        breaking_changes = []
        affected_systems = []
        risk_level = RiskLevel.LOW

        # Analyze file changes for breaking changes and affected systems
        for commit in commits:
            for change in commit.get("file_changes", []):
                filename = change.get("filename", "")
                if any(
                    keyword in filename.lower()
                    for keyword in ["api", "interface", "schema"]
                ):
                    breaking_changes.append(f"Potential breaking change in {filename}")
                    risk_level = RiskLevel.MEDIUM
                if any(keyword in filename.lower() for keyword in ["config", "env"]):
                    affected_systems.append("Configuration")
                if any(filename.endswith(ext) for ext in [".sql", ".migration"]):
                    affected_systems.append("Database")

        impact_assessment = ImpactAssessment(
            coordination_required=len(temporal_correlations) > 0,
            risk_level=risk_level,
            affected_systems=list(set(affected_systems)),
            breaking_changes=breaking_changes,
        )

        cross_repository_correlation = CrossRepositoryCorrelation(
            enabled=self.correlations_enabled,
            correlation_id=f"{repository_name}-{commit_hash}-{timestamp}",
            temporal_correlations=temporal_correlations,
            semantic_correlations=[],  # Not implemented yet
            breaking_changes=[],  # Could be enhanced
            impact_assessment=impact_assessment,
        )

        # Create security and privacy analysis
        file_analysis = intelligence_data.get("file_analysis", {})
        security_and_privacy = SecurityAndPrivacy(
            sensitive_patterns=[],  # Could be enhanced with actual pattern detection
            security_score=1.0,
            privacy_concerns=[],
            recommendations=[],
        )

        # Create technical analysis
        technologies_detected = intelligence_data.get("technologies_detected", [])
        architecture_patterns = intelligence_data.get("architecture_patterns", [])

        technical_analysis = TechnicalAnalysis(
            complexity_score=float(len(commits)),  # Simple metric
            quality_score=1.0,
            maintainability="good",
            test_coverage=None,
            architecture_compliance={
                "technologies": technologies_detected,
                "patterns": architecture_patterns,
                "total_files": files_changed,
            },
        )

        # Create the complete intelligence document
        return IntelligenceDocumentContent(
            analysis_type=AnalysisType.ENHANCED_CODE_CHANGES_WITH_CORRELATION,
            metadata=metadata,
            change_summary=change_summary,
            cross_repository_correlation=cross_repository_correlation,
            security_and_privacy=security_and_privacy,
            technical_analysis=technical_analysis,
            raw_diff=None,  # Could be added if needed
        )

    def submit_intelligence_document(self, doc: dict[str, Any]) -> bool:
        """Submit the intelligence document to the Archon system."""
        if not doc:
            self.logger.warning("No document to submit")
            return False

        # Keep original document for Pydantic models (they expect datetime objects)
        # Only serialize for JSON fallback cases

        # Transform intelligence document into the appropriate format
        self.logger.debug("Transforming intelligence document for API submission")

        if self.use_mcp_format:
            # Use MCP format for document creation with Pydantic validation
            try:
                # First create a validated intelligence document content
                intelligence_content = self._create_intelligence_document_content(doc)

                # Create MCP request using Pydantic model
                project_id_str = cast(str, self.project_id or "default-project")
                mcp_request = MCPCreateDocumentRequest.create_intelligence_document(
                    project_id=project_id_str,
                    content=intelligence_content,
                    repository_name=doc.get("repository_name", "Unknown"),
                )
                payload = mcp_request.model_dump(mode="json")
            except Exception as e:
                self.logger.error(f"Failed to create validated MCP payload: {e}")

                # Fallback to dictionary format if validation fails
                # Use JSON serialization for datetime objects in fallback
                def serialize_datetime_objects(obj: Any) -> Any:
                    """Recursively convert datetime objects to ISO format strings."""
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    elif isinstance(obj, dict):
                        return {
                            k: serialize_datetime_objects(v) for k, v in obj.items()
                        }
                    elif isinstance(obj, list):
                        return [serialize_datetime_objects(item) for item in obj]
                    else:
                        return obj

                serializable_doc = serialize_datetime_objects(doc)
                payload = {
                    "method": "tools/call",
                    "params": {
                        "name": "mcp__archon__create_document",
                        "arguments": {
                            "project_id": cast(
                                str, self.project_id or "default-project"
                            ),
                            "title": f"Intelligence: {serializable_doc.get('repository_name', 'Unknown')} Code Changes with Analysis",
                            "document_type": "intelligence",
                            "content": serializable_doc,
                            "author": "Intelligence Hook v3.1",
                            "tags": ["intelligence", "automation", "git-hook"],
                        },
                    },
                }
            self.logger.debug(
                f"Using MCP format for document creation in project {self.project_id}"
            )
        else:
            # Use intelligence service format with Pydantic validation
            try:
                # First create a validated intelligence document content
                intelligence_content = self._create_intelligence_document_content(doc)

                # Create intelligence service request using Pydantic model
                service_request = IntelligenceServiceRequest.from_intelligence_document(
                    content=intelligence_content,
                    repository_name=doc.get("repository_name", "unknown"),
                    commit_hash=doc.get("commit_hash", "unknown"),
                )
                # Use model_dump with serialization mode to handle datetime objects
                payload = service_request.model_dump(mode="json")
            except Exception as e:
                self.logger.error(f"Failed to create validated service payload: {e}")

                # Fallback to dictionary format if validation fails
                # Use JSON serialization for datetime objects in fallback
                def serialize_datetime_objects(obj: Any) -> Any:
                    """Recursively convert datetime objects to ISO format strings."""
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    elif isinstance(obj, dict):
                        return {
                            k: serialize_datetime_objects(v) for k, v in obj.items()
                        }
                    elif isinstance(obj, list):
                        return [serialize_datetime_objects(item) for item in obj]
                    else:
                        return obj

                serializable_doc = serialize_datetime_objects(doc)
                content = json.dumps(
                    serializable_doc, indent=2, default=json_datetime_serializer
                )
                source_path = f"git://{serializable_doc.get('repository_name', 'unknown')}/commit/{serializable_doc.get('commit_hash', 'unknown')}"

                payload = {
                    "content": content,
                    "source_path": source_path,
                    "metadata": {
                        "type": "intelligence_document",
                        "repository": serializable_doc.get("repository_name"),
                        "commit_hash": serializable_doc.get("commit_hash"),
                        "timestamp": serializable_doc.get("timestamp"),
                        "commits_analyzed": serializable_doc.get("commits_analyzed"),
                        "generated_by": "intelligence_hook_v3.1",
                    },
                    "store_entities": True,
                    "extract_relationships": True,
                    "trigger_freshness_analysis": True,
                }
            self.logger.debug(f"Using intelligence service format")

        # Wrap payload in JSON-RPC format only for MCP endpoint
        if self.use_mcp_format:
            jsonrpc_payload = {
                "jsonrpc": "2.0",
                "id": f"intelligence_hook_{int(time.time())}",
                "method": payload.get("method", "tools/call"),
                "params": payload.get("params", payload),
            }
        else:
            # Intelligence service expects direct JSON payload
            jsonrpc_payload = payload

        payload_size = len(
            json.dumps(jsonrpc_payload, default=json_datetime_serializer)
        )
        self.logger.debug(f"API payload prepared: size={payload_size} chars")
        self.logger.debug(
            f"Using API endpoint: {self.api_url} with timeout: {self.api_timeout}s"
        )
        self.logger.debug(f"HTTP client: {HTTP_CLIENT}")
        self.logger.debug(
            f"JSON-RPC payload: {json.dumps(jsonrpc_payload, default=json_datetime_serializer, indent=2)[:1000]}..."
        )

        for attempt in range(self.retry_attempts + 1):
            try:
                self.logger.info(
                    f"Submitting intelligence document (attempt {attempt + 1}/{self.retry_attempts + 1})"
                )

                start_time = time.time()

                # Use the appropriate HTTP client
                if HTTP_CLIENT == "httpx":
                    with httpx.Client() as client:
                        response = client.post(
                            self.api_url,
                            data=json.dumps(
                                jsonrpc_payload, default=json_datetime_serializer
                            ),
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/event-stream",
                            },
                            timeout=self.api_timeout,
                        )
                        response_time = time.time() - start_time

                        self.logger.debug(
                            f"API response received in {response_time:.2f}s, status: {response.status_code}"
                        )

                        if response.status_code == 200:
                            try:
                                result = response.json()
                                self.logger.debug(
                                    f"API response content: {str(result)[:200]}..."
                                )

                                # Intelligence service returns different success format
                                if "entities" in result or "document_id" in result:
                                    self.logger.info(
                                        f"✅ Intelligence document submitted successfully"
                                    )
                                    if "entities" in result:
                                        self.logger.info(
                                            f"Extracted {len(result.get('entities', []))} entities"
                                        )
                                    if "document_id" in result:
                                        self.logger.info(
                                            f"Document ID: {result['document_id']}"
                                        )
                                    return True
                                else:
                                    self.logger.error(
                                        f"Unexpected API response format: {result}"
                                    )
                            except Exception as e:
                                self.logger.error(
                                    f"Invalid JSON response: {e}, raw response: {response.text[:500]}"
                                )
                        else:
                            self.logger.error(
                                f"HTTP {response.status_code}: {response.text[:500]}"
                            )
                else:
                    # Using requests
                    response = requests.post(
                        self.api_url,
                        data=json.dumps(
                            jsonrpc_payload, default=json_datetime_serializer
                        ),
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json, text/event-stream",
                        },
                        timeout=self.api_timeout,
                    )
                    response_time = time.time() - start_time

                    self.logger.debug(
                        f"API response received in {response_time:.2f}s, status: {response.status_code}"
                    )

                    if response.status_code == 200:
                        try:
                            result = response.json()
                            self.logger.debug(
                                f"API response content: {str(result)[:200]}..."
                            )

                            # Intelligence service returns different success format
                            if "entities" in result or "document_id" in result:
                                self.logger.info(
                                    f"✅ Intelligence document submitted successfully"
                                )
                                if "entities" in result:
                                    self.logger.info(
                                        f"Extracted {len(result.get('entities', []))} entities"
                                    )
                                if "document_id" in result:
                                    self.logger.info(
                                        f"Document ID: {result['document_id']}"
                                    )
                                return True
                            else:
                                self.logger.error(
                                    f"Unexpected API response format: {result}"
                                )
                        except json.JSONDecodeError as e:
                            self.logger.error(
                                f"Invalid JSON response: {e}, raw response: {response.text[:500]}"
                            )
                    else:
                        self.logger.error(
                            f"HTTP {response.status_code}: {response.text[:500]}"
                        )

            except Exception as e:
                # Handle both httpx and requests exceptions
                if HTTP_CLIENT == "httpx" and "timeout" in str(e).lower():
                    self.logger.warning(f"Request timeout (attempt {attempt + 1})")
                elif (
                    HTTP_CLIENT == "requests"
                    and hasattr(e, "__module__")
                    and "requests" in e.__module__
                ):
                    if "timeout" in str(type(e)).lower():
                        self.logger.warning(f"Request timeout (attempt {attempt + 1})")
                    else:
                        self.logger.error(
                            f"Request failed (attempt {attempt + 1}): {e}"
                        )
                else:
                    self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")

            if attempt < self.retry_attempts:
                self.logger.info(f"Retrying in 1 second...")
                time.sleep(1)

        self.logger.error(
            "❌ Failed to submit intelligence document after all attempts"
        )
        return False

    def process_pre_push_hook(self, remote_name: str, remote_url: str) -> int:
        """Process the pre-push hook."""
        self.logger.info(
            f"🚀 Processing pre-push hook for {remote_name} ({remote_url})"
        )
        self.logger.info(f"Repository: {self.repo_name} at {self.repo_root}")
        self.logger.info(
            f"Features enabled - correlations: {self.correlations_enabled}, file_analysis: {self.file_analysis_enabled}"
        )

        try:
            # Get commits being pushed
            commits_to_push = []
            self.logger.debug("Reading commit data from stdin")

            # Read from stdin if available (standard pre-push hook interface)
            if not sys.stdin.isatty():
                for line in sys.stdin:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        # local_ref local_sha remote_ref remote_sha
                        local_ref, local_sha, remote_ref, remote_sha = parts[:4]

                        if local_sha != "0000000000000000000000000000000000000000":
                            # Get commits being pushed
                            if remote_sha == "0000000000000000000000000000000000000000":
                                # New branch, get recent commits
                                commit_list = self.run_git_command(
                                    ["git", "rev-list", "--max-count=10", local_sha]
                                )
                            else:
                                # Existing branch, get commits between remote and local
                                commit_list = self.run_git_command(
                                    ["git", "rev-list", f"{remote_sha}..{local_sha}"]
                                )

                            if commit_list:
                                commits_to_push.extend(commit_list.split("\n"))

            # If no commits from stdin, get recent commits
            if not commits_to_push:
                self.logger.info("No commits from stdin, analyzing recent commits")
                recent_commits = self.run_git_command(
                    ["git", "rev-list", "--max-count=5", "HEAD"]
                )
                if recent_commits:
                    commits_to_push = recent_commits.split("\n")
                    self.logger.debug(
                        f"Found {len(commits_to_push)} recent commits to analyze"
                    )

            if not commits_to_push:
                self.logger.warning(
                    "No commits to analyze, skipping intelligence processing"
                )
                return 0

            # Remove duplicates and limit
            original_count = len(commits_to_push)
            commits_to_push = list(set(commits_to_push))[
                : self.config.get("analysis", {}).get("max_commits", 10)
            ]
            if len(commits_to_push) != original_count:
                self.logger.debug(
                    f"Deduplicated commits: {original_count} → {len(commits_to_push)}"
                )

            self.logger.info(
                f"📊 Analyzing {len(commits_to_push)} commits: {commits_to_push[:3]}{'...' if len(commits_to_push) > 3 else ''}"
            )

            # Build intelligence document
            self.logger.debug("Starting intelligence document generation")
            intelligence_doc = self.build_intelligence_document(commits_to_push)

            if intelligence_doc:
                self.logger.info("✅ Intelligence document generated successfully")
                # Submit to Archon system
                success = self.submit_intelligence_document(intelligence_doc)
                if success:
                    self.logger.info("🎉 Pre-push hook completed successfully")
                    return 0
                else:
                    self.logger.error(
                        "❌ Pre-push hook failed during document submission"
                    )
                    return 1
            else:
                self.logger.warning(
                    "No intelligence document generated, continuing without intelligence update"
                )
                return 0

        except Exception as e:
            self.logger.error(f"💥 Pre-push hook processing failed with exception: {e}")
            import traceback

            self.logger.debug(f"Full traceback: {traceback.format_exc()}")
            return 1


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enhanced Intelligence Hook")
    parser.add_argument("remote_name", nargs="?", default="origin", help="Remote name")
    parser.add_argument("remote_url", nargs="?", default="", help="Remote URL")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Initialize hook
    hook = IntelligenceHook(config_path=args.config)

    if args.verbose:
        hook.logger.setLevel(logging.DEBUG)

    if args.dry_run:
        hook.logger.info("🔍 DRY RUN MODE - No data will be submitted")

        # Override submit method for dry run
        def dry_run_submit(doc: dict[str, Any]) -> bool:
            hook.logger.info(
                f"Would submit document with {len(doc.get('intelligence_data', {}).get('commit_analysis', {}).get('commits', []))} commits"
            )
            return True

        # Type ignore to avoid mypy method assignment error
        hook.submit_intelligence_document = cast(Any, dry_run_submit)

    # Process the hook
    exit_code = hook.process_pre_push_hook(args.remote_name, args.remote_url)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
