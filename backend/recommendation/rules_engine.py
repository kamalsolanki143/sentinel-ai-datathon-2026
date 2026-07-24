"""
Sentinel AI - Policy & Business Rules Engine
============================================
File: backend/recommendation/rules_engine.py
Purpose: Evaluates police operational policies, legal boundaries, shift limits,
         mandatory response rules, duo dispatch requirements, and emergency overrides.

Dependencies: pydantic, typing, enum, loguru
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from loguru import logger
from pydantic import BaseModel, Field


class RuleSeverity(str, Enum):
    """Rule severity classification for policy compliance."""

    CRITICAL = "CRITICAL"  # Mandatory rule violation (hard block)
    WARNING = "WARNING"    # Operational guidance advisory (soft warning)
    INFO = "INFO"          # Informational notice


class RuleCategory(str, Enum):
    """Categorization of operational rules."""

    BUSINESS = "BUSINESS"
    GOVERNMENT_POLICY = "GOVERNMENT_POLICY"
    EMERGENCY = "EMERGENCY"
    HIGH_PRIORITY_CRIME = "HIGH_PRIORITY_CRIME"
    OFFICER_SAFETY = "OFFICER_SAFETY"
    JURISDICTION = "JURISDICTION"


class PolicyRule(BaseModel):
    """Model representing an individual business or policy rule."""

    rule_id: str = Field(description="Unique rule identifier e.g. RUL-001")
    name: str = Field(description="Human-readable rule title")
    description: str = Field(description="Detailed rule explanation")
    category: RuleCategory = Field(default=RuleCategory.BUSINESS)
    severity: RuleSeverity = Field(default=RuleSeverity.CRITICAL)
    enabled: bool = Field(default=True)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ComplianceResult(BaseModel):
    """Result of rule engine evaluation over a proposed recommendation or assignment."""

    is_compliant: bool = Field(description="True if no CRITICAL rules are violated")
    passed_rules: List[str] = Field(default_factory=list)
    violated_rules: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    applied_overrides: List[str] = Field(default_factory=list)


# Pre-defined Enterprise Policy Rules
DEFAULT_RULES: List[PolicyRule] = [
    PolicyRule(
        rule_id="RUL-001",
        name="Mandatory Duo Dispatch for High Severity Incidents",
        description="Incidents with crime severity >= 0.80 require assignment of at least 2 officers.",
        category=RuleCategory.HIGH_PRIORITY_CRIME,
        severity=RuleSeverity.CRITICAL,
        parameters={"min_severity": 0.80, "min_officers": 2},
    ),
    PolicyRule(
        rule_id="RUL-002",
        name="Maximum Shift Hours Fatigue Prevention",
        description="Officers who have worked >= 12 consecutive hours cannot be assigned to new active patrols.",
        category=RuleCategory.OFFICER_SAFETY,
        severity=RuleSeverity.CRITICAL,
        parameters={"max_shift_hours": 12.0},
    ),
    PolicyRule(
        rule_id="RUL-003",
        name="Station Jurisdiction Radius Boundary",
        description="Patrol units should not be routinely assigned beyond 25km of their home station unless in emergency mode.",
        category=RuleCategory.JURISDICTION,
        severity=RuleSeverity.WARNING,
        parameters={"max_radius_km": 25.0},
    ),
    PolicyRule(
        rule_id="RUL-004",
        name="SWAT / Tactical Unit Requirement",
        description="Violent incidents involving firearms or terrorism must include a SWAT/Tactical specialized unit.",
        category=RuleCategory.EMERGENCY,
        severity=RuleSeverity.CRITICAL,
        parameters={"required_specialization": "SWAT"},
    ),
    PolicyRule(
        rule_id="RUL-005",
        name="Cyber Crime Specialist Allocation",
        description="Cyber attacks or high-value financial fraud incidents require at least 1 Cyber Crime Specialist.",
        category=RuleCategory.GOVERNMENT_POLICY,
        severity=RuleSeverity.WARNING,
        parameters={"required_specialization": "Cyber Crime"},
    ),
    PolicyRule(
        rule_id="RUL-006",
        name="Minimum Patrol Vehicle Fuel Level",
        description="Patrol vehicles assigned to long-range routes must maintain at least 25% fuel/battery level.",
        category=RuleCategory.BUSINESS,
        severity=RuleSeverity.WARNING,
        parameters={"min_fuel_pct": 25.0},
    ),
]


class PolicyRuleEngine:
    """
    Enterprise Rule Engine for evaluating Sentinel AI operational recommendations
    against government policies, emergency safety protocols, and officer shift regulations.
    """

    def __init__(self, custom_rules: Optional[List[PolicyRule]] = None) -> None:
        """Initialize Rule Engine with default or custom policy rules."""
        self.rules: Dict[str, PolicyRule] = {}
        rules_to_load = custom_rules if custom_rules is not None else DEFAULT_RULES
        for rule in rules_to_load:
            self.rules[rule.rule_id] = rule
        logger.info(f"PolicyRuleEngine initialized with {len(self.rules)} active policy rules.")

    def add_rule(self, rule: PolicyRule) -> None:
        """Add or update a policy rule dynamically."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Rule {rule.rule_id} ({rule.name}) registered.")

    def remove_rule(self, rule_id: str) -> None:
        """Remove a rule by its ID."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Rule {rule_id} removed.")

    def evaluate_officer_assignment(
        self,
        officer: Dict[str, Any],
        incident_or_zone: Dict[str, Any],
        assigned_officer_count: int = 1,
        emergency_override: bool = False,
    ) -> ComplianceResult:
        """
        Evaluate a proposed officer assignment against active policy rules.

        Args:
            officer: Officer record dict.
            incident_or_zone: Incident/hotspot data dict.
            assigned_officer_count: Number of officers assigned to this task.
            emergency_override: Flag to bypass WARNING level rules during active crisis.

        Returns:
            ComplianceResult detailing status, passed rules, violations, and warnings.
        """
        result = ComplianceResult(is_compliant=True)

        if emergency_override:
            result.applied_overrides.append("EMERGENCY_OVERRIDE_ACTIVE")

        severity_score = incident_or_zone.get("crime_severity_score", 0.5)
        crime_type = incident_or_zone.get("crime_type", "").lower()
        distance_km = incident_or_zone.get("distance_km", 0.0)
        weapons_involved = incident_or_zone.get("weapons_involved", False)
        specialization = officer.get("specialization", "General")
        shift_hours = officer.get("shift_hours_worked", 0.0)
        fuel_pct = officer.get("vehicle_fuel_pct", 100.0)

        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            # RUL-001: Mandatory Duo Dispatch
            if rule_id == "RUL-001":
                min_sev = rule.parameters.get("min_severity", 0.80)
                min_offs = rule.parameters.get("min_officers", 2)
                if severity_score >= min_sev and assigned_officer_count < min_offs:
                    violation_detail = {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "reason": f"High severity ({severity_score}) requires at least {min_offs} officers, but {assigned_officer_count} assigned.",
                    }
                    if rule.severity == RuleSeverity.CRITICAL:
                        result.is_compliant = False
                        result.violated_rules.append(violation_detail)
                    else:
                        result.warnings.append(violation_detail)
                else:
                    result.passed_rules.append(rule_id)

            # RUL-002: Fatigue Prevention
            elif rule_id == "RUL-002":
                max_hrs = rule.parameters.get("max_shift_hours", 12.0)
                if shift_hours >= max_hrs and not emergency_override:
                    violation_detail = {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "reason": f"Officer {officer.get('name', 'ID')} worked {shift_hours} hrs, exceeding maximum shift limit of {max_hrs} hrs.",
                    }
                    result.is_compliant = False
                    result.violated_rules.append(violation_detail)
                else:
                    result.passed_rules.append(rule_id)

            # RUL-003: Station Radius Boundary
            elif rule_id == "RUL-003":
                max_rad = rule.parameters.get("max_radius_km", 25.0)
                if distance_km > max_rad and not emergency_override:
                    violation_detail = {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "reason": f"Target location distance ({distance_km}km) exceeds station radius boundary ({max_rad}km).",
                    }
                    result.warnings.append(violation_detail)
                else:
                    result.passed_rules.append(rule_id)

            # RUL-004: SWAT / Tactical Requirement
            elif rule_id == "RUL-004":
                req_spec = rule.parameters.get("required_specialization", "SWAT")
                if weapons_involved or crime_type in ["active_shooter", "terrorism", "hostage"]:
                    if specialization.upper() != req_spec.upper():
                        violation_detail = {
                            "rule_id": rule_id,
                            "rule_name": rule.name,
                            "reason": f"High-risk incident requires specialized {req_spec} officer. Assigned: {specialization}.",
                        }
                        if rule.severity == RuleSeverity.CRITICAL:
                            result.is_compliant = False
                            result.violated_rules.append(violation_detail)
                        else:
                            result.warnings.append(violation_detail)
                    else:
                        result.passed_rules.append(rule_id)

            # RUL-005: Cyber Crime Specialist
            elif rule_id == "RUL-005":
                if crime_type in ["cyber_attack", "financial_fraud", "ransomware"]:
                    if specialization.lower() not in ["cyber", "cyber crime", "financial crime"]:
                        violation_detail = {
                            "rule_id": rule_id,
                            "rule_name": rule.name,
                            "reason": f"Cyber/financial incident requires Cyber specialist. Assigned: {specialization}.",
                        }
                        result.warnings.append(violation_detail)
                    else:
                        result.passed_rules.append(rule_id)

            # RUL-006: Vehicle Fuel Level
            elif rule_id == "RUL-006":
                min_fuel = rule.parameters.get("min_fuel_pct", 25.0)
                if fuel_pct < min_fuel:
                    violation_detail = {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "reason": f"Assigned vehicle fuel level ({fuel_pct}%) is below required minimum threshold ({min_fuel}%).",
                    }
                    result.warnings.append(violation_detail)
                else:
                    result.passed_rules.append(rule_id)

        return result

    def get_all_rules(self) -> List[PolicyRule]:
        """Return list of all registered policy rules."""
        return list(self.rules.values())
