"""Test alert rules engine."""

import pytest

from tsm.intel.alert_engine import (
    Alert,
    AlertEngine,
    AlertRule,
    AlertSeverity,
    AlertType,
    create_default_engine,
    DEFAULT_RULES,
)


def test_default_rules_exist():
    """Test that default rules are defined."""
    assert len(DEFAULT_RULES) >= 1
    
    rule_names = [r.name for r in DEFAULT_RULES]
    assert "high_risk_case" in rule_names
    assert "high_value_case" in rule_names


def test_create_default_engine():
    """Test creating engine with default rules."""
    engine = create_default_engine()
    
    assert len(engine.rules) > 0


def test_alert_engine_high_risk():
    """Test triggering high risk alert."""
    engine = AlertEngine([
        AlertRule(
            name="high_risk",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.WARNING,
            description="High risk case",
            conditions={"risk_level": "high"},
        )
    ])
    
    intel = {"id": 1, "risk_level": "high", "case_type": "counterfeit"}
    alerts = engine.evaluate(intel)
    
    assert len(alerts) == 1
    assert alerts[0].rule_name == "high_risk"
    assert alerts[0].severity == AlertSeverity.WARNING


def test_alert_engine_no_match():
    """Test when no rules match."""
    engine = AlertEngine([
        AlertRule(
            name="high_risk",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.WARNING,
            description="High risk case",
            conditions={"risk_level": "high"},
        )
    ])
    
    intel = {"id": 1, "risk_level": "low", "case_type": "counterfeit"}
    alerts = engine.evaluate(intel)
    
    assert len(alerts) == 0


def test_alert_engine_case_type():
    """Test triggering case type alert."""
    engine = AlertEngine([
        AlertRule(
            name="smuggling",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            description="Smuggling case detected",
            conditions={"case_type": "smuggling"},
        )
    ])
    
    intel = {"id": 1, "risk_level": "medium", "case_type": "smuggling"}
    alerts = engine.evaluate(intel)
    
    assert len(alerts) == 1
    assert alerts[0].alert_type == AlertType.HIGH_RISK
    assert alerts[0].severity == AlertSeverity.CRITICAL


def test_alert_engine_monetary_value():
    """Test triggering monetary value threshold alert."""
    engine = AlertEngine([
        AlertRule(
            name="large_value",
            alert_type=AlertType.HIGH_VALUE,
            severity=AlertSeverity.CRITICAL,
            description="Large monetary value",
            conditions={"min_monetary_value": 500000},
        )
    ])
    
    intel = {"id": 1, "risk_level": "medium"}
    entities = {"monetary_value": 800000}
    alerts = engine.evaluate(intel, entities)
    
    assert len(alerts) == 1
    assert "large_value" in alerts[0].rule_name


def test_alert_engine_monetary_value_below_threshold():
    """Test not triggering when below threshold."""
    engine = AlertEngine([
        AlertRule(
            name="large_value",
            alert_type=AlertType.HIGH_VALUE,
            severity=AlertSeverity.CRITICAL,
            description="Large monetary value",
            conditions={"min_monetary_value": 500000},
        )
    ])
    
    intel = {"id": 1, "risk_level": "medium"}
    entities = {"monetary_value": 100000}
    alerts = engine.evaluate(intel, entities)
    
    assert len(alerts) == 0


def test_alert_engine_quantity_threshold():
    """Test triggering quantity threshold alert."""
    engine = AlertEngine([
        AlertRule(
            name="large_qty",
            alert_type=AlertType.HIGH_VALUE,
            severity=AlertSeverity.WARNING,
            description="Large quantity",
            conditions={"min_quantity": 1000},
        )
    ])
    
    intel = {"id": 1, "risk_level": "low"}
    entities = {"quantity_value": 5000}
    alerts = engine.evaluate(intel, entities)
    
    assert len(alerts) == 1


def test_alert_engine_disabled_rule():
    """Test that disabled rules don't trigger."""
    engine = AlertEngine([
        AlertRule(
            name="disabled_rule",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.WARNING,
            description="This rule is disabled",
            conditions={"risk_level": "high"},
            enabled=False,
        )
    ])
    
    intel = {"id": 1, "risk_level": "high"}
    alerts = engine.evaluate(intel)
    
    assert len(alerts) == 0


def test_alert_engine_add_rule():
    """Test adding a new rule."""
    engine = AlertEngine([])
    assert len(engine.rules) == 0
    
    engine.add_rule(AlertRule(
        name="new_rule",
        alert_type=AlertType.HIGH_RISK,
        severity=AlertSeverity.WARNING,
        description="New rule",
        conditions={"risk_level": "high"},
    ))
    
    assert len(engine.rules) == 1


def test_alert_engine_remove_rule():
    """Test removing a rule."""
    engine = AlertEngine([
        AlertRule(
            name="test_rule",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.WARNING,
            description="Test rule",
            conditions={"risk_level": "high"},
        )
    ])
    
    result = engine.remove_rule("test_rule")
    assert result is True
    assert len(engine.rules) == 0
    
    result = engine.remove_rule("nonexistent")
    assert result is False


def test_alert_engine_enable_disable():
    """Test enabling and disabling rules."""
    engine = AlertEngine([
        AlertRule(
            name="test_rule",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.WARNING,
            description="Test rule",
            conditions={"risk_level": "high"},
            enabled=True,
        )
    ])
    
    result = engine.disable_rule("test_rule")
    assert result is True
    
    result = engine.enable_rule("test_rule")
    assert result is True


def test_alert_dataclass():
    """Test Alert dataclass."""
    alert = Alert(
        rule_name="test_alert",
        alert_type=AlertType.HIGH_RISK,
        severity=AlertSeverity.CRITICAL,
        title="Test Alert",
        message="This is a test alert",
        intel_ids=[1, 2, 3],
    )
    
    assert alert.rule_name == "test_alert"
    assert len(alert.intel_ids) == 3


def test_multiple_rules_trigger():
    """Test that multiple rules can trigger for same intel."""
    engine = AlertEngine([
        AlertRule(
            name="high_risk",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.WARNING,
            description="High risk",
            conditions={"risk_level": "high"},
        ),
        AlertRule(
            name="smuggling",
            alert_type=AlertType.HIGH_RISK,
            severity=AlertSeverity.CRITICAL,
            description="Smuggling",
            conditions={"case_type": "smuggling"},
        ),
    ])
    
    intel = {"id": 1, "risk_level": "high", "case_type": "smuggling"}
    alerts = engine.evaluate(intel)
    
    assert len(alerts) == 2