"""Tests for pipeline enum types."""

import pytest

from omnibase_spi.contracts.pipeline.enum_auth_reason_code import AuthReasonCode
from omnibase_spi.enums.enum_rrh_rule import RRHRule


@pytest.mark.unit
class TestRRHRule:
    """Tests for RRHRule enum."""

    def test_values_are_strings(self) -> None:
        for rule in RRHRule:
            assert isinstance(rule.value, str)
            assert rule.value.startswith("RRH-")

    def test_specific_rules_exist(self) -> None:
        # Repo checks (10xx)
        assert RRHRule.RRH_1001.value == "RRH-1001"
        assert RRHRule.RRH_1002.value == "RRH-1002"
        # Environment checks (11xx)
        assert RRHRule.RRH_1101.value == "RRH-1101"
        assert RRHRule.RRH_1102.value == "RRH-1102"
        # Kafka checks (12xx)
        assert RRHRule.RRH_1201.value == "RRH-1201"
        # Kubernetes checks (13xx)
        assert RRHRule.RRH_1301.value == "RRH-1301"
        # Toolchain checks (14xx)
        assert RRHRule.RRH_1401.value == "RRH-1401"
        assert RRHRule.RRH_1402.value == "RRH-1402"
        assert RRHRule.RRH_1403.value == "RRH-1403"
        assert RRHRule.RRH_1404.value == "RRH-1404"
        # Cross-checks (15xx, 16xx)
        assert RRHRule.RRH_1501.value == "RRH-1501"
        assert RRHRule.RRH_1601.value == "RRH-1601"
        # Repo-boundary checks (17xx)
        assert RRHRule.RRH_1701.value == "RRH-1701"

    def test_is_str_enum(self) -> None:
        assert isinstance(RRHRule.RRH_1001, str)
        assert RRHRule.RRH_1001 == "RRH-1001"

    def test_has_13_rules(self) -> None:
        assert len(RRHRule) == 13


@pytest.mark.unit
class TestAuthReasonCode:
    """Tests for AuthReasonCode enum."""

    def test_values_are_strings(self) -> None:
        for code in AuthReasonCode:
            assert isinstance(code.value, str)

    def test_allow_reasons(self) -> None:
        assert AuthReasonCode.ALLOW_DEFAULT == "ALLOW_DEFAULT"
        assert AuthReasonCode.ALLOW_EXPLICIT == "ALLOW_EXPLICIT"
        assert AuthReasonCode.ALLOW_OVERRIDE == "ALLOW_OVERRIDE"

    def test_deny_reasons(self) -> None:
        assert AuthReasonCode.DENY_SCOPE == "DENY_SCOPE"
        assert AuthReasonCode.DENY_CROSS_REPO == "DENY_CROSS_REPO"
        assert AuthReasonCode.DENY_DESTRUCTIVE == "DENY_DESTRUCTIVE"

    def test_escalate_reasons(self) -> None:
        assert AuthReasonCode.ESCALATE_HUMAN_REQUIRED == "ESCALATE_HUMAN_REQUIRED"
        assert AuthReasonCode.ESCALATE_RISK == "ESCALATE_RISK"
