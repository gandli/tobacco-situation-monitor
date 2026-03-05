"""Alert rules engine for tobacco case intelligence.

This module provides configurable alert rules for detecting high-priority
cases and generating notifications.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from tsm.intel.scoring import LEVEL_THRESHOLDS


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts."""
    HIGH_VALUE = "high_value"  # 涉案金额高
    HIGH_RISK = "high_risk"  # 高风险等级
    REGION_CLUSTER = "region_cluster"  # 同地区集中
    CASE_TYPE_CLUSTER = "case_type_cluster"  # 同类型集中
    TIME_CLUSTER = "time_cluster"  # 短期内多发
    CROSS_REGION = "cross_region"  # 跨区域案件
    REPEAT_OFFENDER = "repeat_offender"  # 惯犯


@dataclass
class AlertRule:
    """Configuration for an alert rule."""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    description: str
    conditions: Dict[str, Any]
    enabled: bool = True
    cooldown_hours: int = 1  # Minimum time between alerts for same rule


@dataclass
class Alert:
    """Generated alert instance."""
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    intel_ids: List[int]
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Default alert rules
DEFAULT_RULES: List[AlertRule] = [
    AlertRule(
        name="high_value_case",
        alert_type=AlertType.HIGH_VALUE,
        severity=AlertSeverity.CRITICAL,
        description="涉案金额超过50万元的案件",
        conditions={"min_monetary_value": 500000},
        cooldown_hours=2,
    ),
    AlertRule(
        name="high_risk_case",
        alert_type=AlertType.HIGH_RISK,
        severity=AlertSeverity.WARNING,
        description="风险等级为高的案件",
        conditions={"risk_level": "high"},
    ),
    AlertRule(
        name="cross_region_transport",
        alert_type=AlertType.CROSS_REGION,
        severity=AlertSeverity.WARNING,
        description="涉及跨省运输的案件",
        conditions={"keywords": ["跨省运输", "跨区域", "省际"]},
    ),
    AlertRule(
        name="smuggling_detected",
        alert_type=AlertType.HIGH_RISK,
        severity=AlertSeverity.CRITICAL,
        description="走私烟草案件",
        conditions={"case_type": "smuggling"},
    ),
    AlertRule(
        name="counterfeit_production",
        alert_type=AlertType.HIGH_RISK,
        severity=AlertSeverity.WARNING,
        description="假冒伪劣烟草案件",
        conditions={"case_type": "counterfeit"},
    ),
    AlertRule(
        name="large_quantity",
        alert_type=AlertType.HIGH_VALUE,
        severity=AlertSeverity.WARNING,
        description="查获数量超过1000条的案件",
        conditions={"min_quantity": 1000},
    ),
]


class AlertEngine:
    """Engine for evaluating intel against alert rules."""

    def __init__(self, rules: Optional[List[AlertRule]] = None, use_defaults: bool = True):
        """Initialize with optional custom rules.

        Args:
            rules: Custom alert rules. Uses DEFAULT_RULES if not provided and use_defaults is True.
            use_defaults: If True and rules is None, use DEFAULT_RULES. If False, start with empty rules.
        """
        if rules is None:
            self.rules = DEFAULT_RULES if use_defaults else []
        else:
            self.rules = rules
        self._alert_history: Dict[str, datetime] = {}

    def evaluate(self, intel: Dict[str, Any], entities: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """Evaluate an intel record against all enabled rules.

        Args:
            intel: Intel record dictionary with fields like risk_level, case_type.
            entities: Optional extracted entities like monetary_value, quantity.

        Returns:
            List of triggered alerts.
        """
        alerts = []
        entities = entities or {}

        for rule in self.rules:
            if not rule.enabled:
                continue

            # Check cooldown
            if self._is_in_cooldown(rule.name):
                continue

            # Evaluate conditions
            if self._matches_conditions(rule, intel, entities):
                alert = self._create_alert(rule, intel, entities)
                alerts.append(alert)
                self._record_alert(rule.name)

        return alerts

    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if a rule is in cooldown period."""
        if rule_name not in self._alert_history:
            return False

        rule = next((r for r in self.rules if r.name == rule_name), None)
        if not rule:
            return False

        from datetime import timedelta
        elapsed = datetime.now(timezone.utc) - self._alert_history[rule_name]
        return elapsed < timedelta(hours=rule.cooldown_hours)

    def _record_alert(self, rule_name: str) -> None:
        """Record when an alert was triggered."""
        self._alert_history[rule_name] = datetime.now(timezone.utc)

    def _matches_conditions(self, rule: AlertRule, intel: Dict[str, Any], entities: Dict[str, Any]) -> bool:
        """Check if intel matches rule conditions."""
        conditions = rule.conditions

        # Check risk level
        if "risk_level" in conditions:
            if intel.get("risk_level") != conditions["risk_level"]:
                return False

        # Check case type
        if "case_type" in conditions:
            if intel.get("case_type") != conditions["case_type"]:
                return False

        # Check monetary value threshold
        if "min_monetary_value" in conditions:
            monetary_value = entities.get("monetary_value", 0)
            if not monetary_value or monetary_value < conditions["min_monetary_value"]:
                return False

        # Check quantity threshold
        if "min_quantity" in conditions:
            quantity_value = entities.get("quantity_value", 0)
            if not quantity_value or quantity_value < conditions["min_quantity"]:
                return False

        # Check keywords
        if "keywords" in conditions:
            keywords_matched = intel.get("keywords_matched", "")
            if not keywords_matched:
                return False
            keyword_list = keywords_matched.split(",") if isinstance(keywords_matched, str) else keywords_matched
            if not any(kw in keyword_list for kw in conditions["keywords"]):
                return False

        return True

    def _create_alert(self, rule: AlertRule, intel: Dict[str, Any], entities: Dict[str, Any]) -> Alert:
        """Create an alert from a triggered rule."""
        intel_id = intel.get("id", 0)

        # Build title and message
        title = f"[{rule.severity.value.upper()}] {rule.description}"

        message_parts = []
        if intel.get("case_type"):
            message_parts.append(f"案件类型: {intel['case_type']}")
        if intel.get("risk_level"):
            message_parts.append(f"风险等级: {intel['risk_level']}")
        if entities.get("monetary_amount"):
            message_parts.append(f"涉案金额: {entities['monetary_amount']}")
        if entities.get("quantity"):
            message_parts.append(f"查获数量: {entities['quantity']}")
        if intel.get("region"):
            message_parts.append(f"地区: {intel['region']}")

        message = " | ".join(message_parts) if message_parts else rule.description

        return Alert(
            rule_name=rule.name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=title,
            message=message,
            intel_ids=[intel_id],
            details={
                "intel": intel,
                "entities": entities,
            }
        )

    def add_rule(self, rule: AlertRule) -> None:
        """Add a new alert rule."""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name. Returns True if found and removed."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                return True
        return False

    def enable_rule(self, rule_name: str) -> bool:
        """Enable a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                return True
        return False

    def disable_rule(self, rule_name: str) -> bool:
        """Disable a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                return True
        return False


def create_default_engine() -> AlertEngine:
    """Create an alert engine with default rules."""
    return AlertEngine(DEFAULT_RULES)