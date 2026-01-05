"""Unit tests for default handler contract YAML templates.

This module provides comprehensive test coverage for the default handler contract
YAML templates located in src/omnibase_spi/contracts/defaults/. Tests verify:
- Valid YAML structure
- Required fields presence
- ModelHandlerContract validation
- Conservative/safe defaults
- Golden tests for change detection
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from omnibase_core.models.contracts.model_handler_contract import ModelHandlerContract


# Path to default contract templates
DEFAULTS_DIR = (
    Path(__file__).parent.parent.parent.parent
    / "src"
    / "omnibase_spi"
    / "contracts"
    / "defaults"
)


def load_yaml_template(filename: str) -> dict[str, Any]:
    """Load a YAML template file.

    Args:
        filename: Name of the template file to load

    Returns:
        Parsed YAML content as dictionary

    Raises:
        FileNotFoundError: If template file does not exist
        yaml.YAMLError: If template is not valid YAML
    """
    template_path = DEFAULTS_DIR / filename
    with open(template_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.unit
class TestDefaultComputeHandlerContract:
    """Tests for default_compute_handler.yaml template."""

    @pytest.fixture
    def template(self) -> dict[str, Any]:
        """Load the compute handler template."""
        return load_yaml_template("default_compute_handler.yaml")

    def test_template_loads_valid_yaml(self, template: dict[str, Any]) -> None:
        """Test template is valid YAML."""
        assert template is not None
        assert isinstance(template, dict)

    def test_template_has_required_fields(self, template: dict[str, Any]) -> None:
        """Test template has all required top-level fields."""
        required_fields = ["handler_id", "name", "version", "descriptor"]
        for field in required_fields:
            assert field in template, f"Missing required field: {field}"

    def test_template_validates_as_model(self, template: dict[str, Any]) -> None:
        """Test template can be validated as ModelHandlerContract."""
        contract = ModelHandlerContract.model_validate(template)
        assert contract.handler_id == "template.compute.default"

    def test_compute_handler_is_pure(self, template: dict[str, Any]) -> None:
        """Test compute handler has pure purity setting."""
        assert template["descriptor"]["purity"] == "pure"

    def test_compute_handler_is_idempotent(self, template: dict[str, Any]) -> None:
        """Test compute handler is marked as idempotent."""
        assert template["descriptor"]["idempotent"] is True

    def test_compute_handler_allows_parallel(self, template: dict[str, Any]) -> None:
        """Test compute handler allows parallel execution."""
        assert template["execution_constraints"]["can_run_parallel"] is True

    def test_compute_handler_no_nondeterministic_effect(
        self, template: dict[str, Any]
    ) -> None:
        """Test compute handler has no nondeterministic effect."""
        assert template["execution_constraints"]["nondeterministic_effect"] is False

    def test_compute_handler_no_timeout(self, template: dict[str, Any]) -> None:
        """Test compute handler has no timeout (pure compute bounded by input size)."""
        assert template["descriptor"]["timeout_ms"] is None

    def test_compute_handler_no_retry_policy(self, template: dict[str, Any]) -> None:
        """Test compute handler has no retry policy (pure functions should not fail)."""
        assert template["descriptor"]["retry_policy"] is None

    def test_compute_handler_kind(self, template: dict[str, Any]) -> None:
        """Test compute handler kind is set correctly."""
        assert template["descriptor"]["handler_kind"] == "compute"

    def test_compute_handler_concurrency_policy(
        self, template: dict[str, Any]
    ) -> None:
        """Test compute handler has parallel_ok concurrency policy."""
        assert template["descriptor"]["concurrency_policy"] == "parallel_ok"

    def test_compute_handler_no_capability_inputs(
        self, template: dict[str, Any]
    ) -> None:
        """Test compute handler has no capability inputs (pure, no external deps)."""
        assert template["capability_inputs"] == []


@pytest.mark.unit
class TestDefaultEffectHandlerContract:
    """Tests for default_effect_handler.yaml template."""

    @pytest.fixture
    def template(self) -> dict[str, Any]:
        """Load the effect handler template."""
        return load_yaml_template("default_effect_handler.yaml")

    def test_template_loads_valid_yaml(self, template: dict[str, Any]) -> None:
        """Test template is valid YAML."""
        assert template is not None
        assert isinstance(template, dict)

    def test_template_has_required_fields(self, template: dict[str, Any]) -> None:
        """Test template has all required top-level fields."""
        required_fields = ["handler_id", "name", "version", "descriptor"]
        for field in required_fields:
            assert field in template, f"Missing required field: {field}"

    def test_template_validates_as_model(self, template: dict[str, Any]) -> None:
        """Test template can be validated as ModelHandlerContract."""
        contract = ModelHandlerContract.model_validate(template)
        assert contract.handler_id == "template.effect.default"

    def test_effect_handler_is_side_effecting(
        self, template: dict[str, Any]
    ) -> None:
        """Test effect handler has side_effecting purity setting."""
        assert template["descriptor"]["purity"] == "side_effecting"

    def test_effect_handler_not_idempotent_by_default(
        self, template: dict[str, Any]
    ) -> None:
        """Test effect handler is NOT marked as idempotent (conservative)."""
        assert template["descriptor"]["idempotent"] is False

    def test_effect_handler_has_timeout(self, template: dict[str, Any]) -> None:
        """Test effect handler has a timeout configured."""
        assert template["descriptor"]["timeout_ms"] is not None
        assert template["descriptor"]["timeout_ms"] > 0
        # Default is 30 seconds
        assert template["descriptor"]["timeout_ms"] == 30000

    def test_effect_handler_has_retry_policy(self, template: dict[str, Any]) -> None:
        """Test effect handler has retry policy configured."""
        retry_policy = template["descriptor"]["retry_policy"]
        assert retry_policy is not None
        assert retry_policy["enabled"] is True
        assert retry_policy["max_retries"] >= 1
        assert retry_policy["max_retries"] == 3
        assert retry_policy["backoff_strategy"] == "exponential"

    def test_effect_handler_disallows_parallel(
        self, template: dict[str, Any]
    ) -> None:
        """Test effect handler disallows parallel execution (conservative)."""
        assert template["execution_constraints"]["can_run_parallel"] is False

    def test_effect_handler_has_nondeterministic_effect(
        self, template: dict[str, Any]
    ) -> None:
        """Test effect handler is marked as nondeterministic effect."""
        assert template["execution_constraints"]["nondeterministic_effect"] is True

    def test_effect_handler_kind(self, template: dict[str, Any]) -> None:
        """Test effect handler kind is set correctly."""
        assert template["descriptor"]["handler_kind"] == "effect"

    def test_effect_handler_concurrency_policy(
        self, template: dict[str, Any]
    ) -> None:
        """Test effect handler has serialized concurrency policy (conservative)."""
        assert template["descriptor"]["concurrency_policy"] == "serialized"

    def test_effect_handler_has_circuit_breaker(
        self, template: dict[str, Any]
    ) -> None:
        """Test effect handler has circuit breaker configured."""
        circuit_breaker = template["descriptor"]["circuit_breaker"]
        assert circuit_breaker is not None
        assert circuit_breaker["enabled"] is True
        assert circuit_breaker["failure_threshold"] == 5


@pytest.mark.unit
class TestDefaultNondeterministicComputeHandlerContract:
    """Tests for default_nondeterministic_compute_handler.yaml template."""

    @pytest.fixture
    def template(self) -> dict[str, Any]:
        """Load the nondeterministic compute handler template."""
        return load_yaml_template("default_nondeterministic_compute_handler.yaml")

    def test_template_loads_valid_yaml(self, template: dict[str, Any]) -> None:
        """Test template is valid YAML."""
        assert template is not None
        assert isinstance(template, dict)

    def test_template_has_required_fields(self, template: dict[str, Any]) -> None:
        """Test template has all required top-level fields."""
        required_fields = ["handler_id", "name", "version", "descriptor"]
        for field in required_fields:
            assert field in template, f"Missing required field: {field}"

    def test_template_validates_as_model(self, template: dict[str, Any]) -> None:
        """Test template can be validated as ModelHandlerContract."""
        contract = ModelHandlerContract.model_validate(template)
        assert contract.handler_id == "template.nondeterministic_compute.default"

    def test_nondeterministic_handler_not_idempotent(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler is NOT idempotent (stochastic)."""
        assert template["descriptor"]["idempotent"] is False

    def test_nondeterministic_handler_has_longer_timeout(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler has longer timeout for LLM calls."""
        # Should have longer timeout than effect handlers (2 minutes = 120000ms)
        assert template["descriptor"]["timeout_ms"] >= 60000
        assert template["descriptor"]["timeout_ms"] == 120000

    def test_nondeterministic_handler_has_nondeterministic_effect(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler is marked as nondeterministic effect."""
        assert template["execution_constraints"]["nondeterministic_effect"] is True

    def test_nondeterministic_handler_kind_is_compute(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler kind is compute (architecturally)."""
        assert template["descriptor"]["handler_kind"] == "compute"

    def test_nondeterministic_handler_purity_is_side_effecting(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler purity is side_effecting (for replay)."""
        assert template["descriptor"]["purity"] == "side_effecting"

    def test_nondeterministic_handler_allows_parallel(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler allows parallel LLM calls."""
        assert template["execution_constraints"]["can_run_parallel"] is True
        assert template["descriptor"]["concurrency_policy"] == "parallel_ok"

    def test_nondeterministic_handler_has_retry_policy(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler has retry policy for transient failures."""
        retry_policy = template["descriptor"]["retry_policy"]
        assert retry_policy is not None
        assert retry_policy["enabled"] is True
        # Fewer retries than effect handlers (LLM errors often persistent)
        assert retry_policy["max_retries"] == 2
        assert retry_policy["backoff_strategy"] == "exponential"
        # Higher base delay for LLM rate limiting
        assert retry_policy["base_delay_ms"] == 1000

    def test_nondeterministic_handler_has_llm_capability_input(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler requires LLM capability."""
        capability_inputs = template["capability_inputs"]
        assert len(capability_inputs) > 0
        llm_input = capability_inputs[0]
        assert llm_input["alias"] == "llm"
        assert llm_input["capability"] == "inference.language_model"

    def test_nondeterministic_handler_has_tags(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler has appropriate tags."""
        tags = template.get("tags", [])
        assert "nondeterministic" in tags
        assert "llm" in tags
        assert "ai-inference" in tags

    def test_nondeterministic_handler_metadata(
        self, template: dict[str, Any]
    ) -> None:
        """Test nondeterministic handler has expected metadata."""
        metadata = template.get("metadata", {})
        assert metadata.get("handler_category") == "nondeterministic_compute"
        assert metadata.get("caching_recommended") is True
        assert metadata.get("track_temperature") is True
        assert metadata.get("track_seed") is True


@pytest.mark.unit
class TestDefaultContractConservativeDefaults:
    """Tests verifying conservative/safe defaults across all templates."""

    @pytest.fixture(
        params=[
            "default_compute_handler.yaml",
            "default_effect_handler.yaml",
            "default_nondeterministic_compute_handler.yaml",
        ]
    )
    def template(self, request: pytest.FixtureRequest) -> dict[str, Any]:
        """Load each template."""
        return load_yaml_template(request.param)

    def test_all_templates_have_version(self, template: dict[str, Any]) -> None:
        """Test all templates have version field."""
        assert "version" in template
        assert template["version"] == "1.0.0"

    def test_all_templates_have_descriptor(self, template: dict[str, Any]) -> None:
        """Test all templates have descriptor section."""
        assert "descriptor" in template
        assert isinstance(template["descriptor"], dict)

    def test_all_templates_validate_as_model(self, template: dict[str, Any]) -> None:
        """Test all templates can be validated as ModelHandlerContract."""
        contract = ModelHandlerContract.model_validate(template)
        assert contract is not None

    def test_all_templates_have_execution_constraints(
        self, template: dict[str, Any]
    ) -> None:
        """Test all templates have execution constraints section."""
        assert "execution_constraints" in template
        assert isinstance(template["execution_constraints"], dict)

    def test_all_templates_have_model_references(
        self, template: dict[str, Any]
    ) -> None:
        """Test all templates have input/output model references."""
        assert "input_model" in template
        assert "output_model" in template
        # Default references to base model
        assert "BaseModel" in template["input_model"]
        assert "BaseModel" in template["output_model"]

    def test_all_templates_have_capability_outputs(
        self, template: dict[str, Any]
    ) -> None:
        """Test all templates have capability outputs defined."""
        assert "capability_outputs" in template
        assert isinstance(template["capability_outputs"], list)
        assert len(template["capability_outputs"]) > 0

    def test_all_templates_have_description(self, template: dict[str, Any]) -> None:
        """Test all templates have description field."""
        assert "description" in template
        assert isinstance(template["description"], str)
        assert len(template["description"]) > 0


@pytest.mark.unit
class TestYamlTemplateGoldenTests:
    """Golden tests to detect unexpected changes in default templates.

    These tests verify that template IDs and critical values haven't changed
    unexpectedly, which could indicate accidental modifications or breaking changes.
    """

    def test_compute_handler_id_unchanged(self) -> None:
        """Test compute handler ID hasn't changed unexpectedly."""
        template = load_yaml_template("default_compute_handler.yaml")
        assert template["handler_id"] == "template.compute.default"

    def test_effect_handler_id_unchanged(self) -> None:
        """Test effect handler ID hasn't changed unexpectedly."""
        template = load_yaml_template("default_effect_handler.yaml")
        assert template["handler_id"] == "template.effect.default"

    def test_nondeterministic_handler_id_unchanged(self) -> None:
        """Test nondeterministic compute handler ID hasn't changed unexpectedly."""
        template = load_yaml_template("default_nondeterministic_compute_handler.yaml")
        assert template["handler_id"] == "template.nondeterministic_compute.default"

    def test_compute_handler_name_unchanged(self) -> None:
        """Test compute handler name hasn't changed unexpectedly."""
        template = load_yaml_template("default_compute_handler.yaml")
        assert template["name"] == "Default Compute Handler"

    def test_effect_handler_name_unchanged(self) -> None:
        """Test effect handler name hasn't changed unexpectedly."""
        template = load_yaml_template("default_effect_handler.yaml")
        assert template["name"] == "Default Effect Handler"

    def test_nondeterministic_handler_name_unchanged(self) -> None:
        """Test nondeterministic handler name hasn't changed unexpectedly."""
        template = load_yaml_template("default_nondeterministic_compute_handler.yaml")
        assert template["name"] == "Default Nondeterministic Compute Handler"


@pytest.mark.unit
class TestYamlTemplateSchemaCompliance:
    """Tests for schema compliance and ModelHandlerContract field mapping."""

    def test_compute_handler_model_fields(self) -> None:
        """Test compute handler produces valid ModelHandlerContract fields."""
        template = load_yaml_template("default_compute_handler.yaml")
        contract = ModelHandlerContract.model_validate(template)

        assert contract.handler_id == "template.compute.default"
        assert contract.name == "Default Compute Handler"
        assert contract.version == "1.0.0"
        assert contract.descriptor is not None
        assert contract.capability_outputs == ["compute.result"]

    def test_effect_handler_model_fields(self) -> None:
        """Test effect handler produces valid ModelHandlerContract fields."""
        template = load_yaml_template("default_effect_handler.yaml")
        contract = ModelHandlerContract.model_validate(template)

        assert contract.handler_id == "template.effect.default"
        assert contract.name == "Default Effect Handler"
        assert contract.version == "1.0.0"
        assert contract.descriptor is not None
        assert contract.capability_outputs == ["effect.result"]

    def test_nondeterministic_handler_model_fields(self) -> None:
        """Test nondeterministic handler produces valid ModelHandlerContract fields."""
        template = load_yaml_template("default_nondeterministic_compute_handler.yaml")
        contract = ModelHandlerContract.model_validate(template)

        assert contract.handler_id == "template.nondeterministic_compute.default"
        assert contract.name == "Default Nondeterministic Compute Handler"
        assert contract.version == "1.0.0"
        assert contract.descriptor is not None
        assert contract.capability_outputs == ["inference.result"]
        assert len(contract.capability_inputs) == 1
        assert contract.tags == ["nondeterministic", "llm", "ai-inference"]

    def test_execution_constraints_mapped_correctly(self) -> None:
        """Test execution constraints are mapped to ModelExecutionConstraints."""
        template = load_yaml_template("default_compute_handler.yaml")
        contract = ModelHandlerContract.model_validate(template)

        assert contract.execution_constraints is not None
        assert contract.execution_constraints.can_run_parallel is True
        assert contract.execution_constraints.nondeterministic_effect is False
        assert contract.execution_constraints.must_run is False


@pytest.mark.unit
class TestTemplateFileExistence:
    """Tests to ensure all expected template files exist."""

    def test_defaults_directory_exists(self) -> None:
        """Test that the defaults directory exists."""
        assert DEFAULTS_DIR.exists(), f"Defaults directory not found: {DEFAULTS_DIR}"
        assert DEFAULTS_DIR.is_dir()

    def test_compute_handler_template_exists(self) -> None:
        """Test that compute handler template file exists."""
        path = DEFAULTS_DIR / "default_compute_handler.yaml"
        assert path.exists(), f"Compute handler template not found: {path}"

    def test_effect_handler_template_exists(self) -> None:
        """Test that effect handler template file exists."""
        path = DEFAULTS_DIR / "default_effect_handler.yaml"
        assert path.exists(), f"Effect handler template not found: {path}"

    def test_nondeterministic_handler_template_exists(self) -> None:
        """Test that nondeterministic handler template file exists."""
        path = DEFAULTS_DIR / "default_nondeterministic_compute_handler.yaml"
        assert path.exists(), f"Nondeterministic handler template not found: {path}"


@pytest.mark.unit
class TestTemplateYamlStructure:
    """Tests for YAML structure consistency across templates."""

    @pytest.fixture(
        params=[
            "default_compute_handler.yaml",
            "default_effect_handler.yaml",
            "default_nondeterministic_compute_handler.yaml",
        ]
    )
    def template_path(self, request: pytest.FixtureRequest) -> Path:
        """Get path to each template."""
        return DEFAULTS_DIR / request.param

    def test_yaml_has_comments(self, template_path: Path) -> None:
        """Test that templates have descriptive comments."""
        content = template_path.read_text(encoding="utf-8")
        # Templates should have comments explaining their purpose
        assert "#" in content, f"Template {template_path.name} should have comments"

    def test_yaml_no_tabs(self, template_path: Path) -> None:
        """Test that templates use spaces, not tabs."""
        content = template_path.read_text(encoding="utf-8")
        assert "\t" not in content, f"Template {template_path.name} should not have tabs"

    def test_yaml_no_trailing_whitespace_on_content_lines(
        self, template_path: Path
    ) -> None:
        """Test that content lines don't have excessive trailing whitespace."""
        content = template_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Skip empty lines
            if line.strip():
                # Allow single trailing newline but no other trailing space
                stripped = line.rstrip()
                if len(line) - len(stripped) > 1:
                    pytest.fail(
                        f"Line {i} in {template_path.name} has trailing whitespace"
                    )
