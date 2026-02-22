import json
import datetime
from dataclasses import dataclass, field
from pathlib import Path

_RULES_PATH = Path(__file__).parent / "visa_rules.json"


@dataclass
class RuleResult:
    passed: bool
    failure_codes: list[str] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)

    def add_failure(self, code: str, explanation: str) -> None:
        self.passed = False
        self.failure_codes.append(code)
        self.explanations.append(explanation)


def _load_rules() -> dict:
    with _RULES_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def evaluate(
    *,
    visa_type_code: str,
    nationality: str,
    intended_entry_date: datetime.date,
    supplied_document_types: list[str],
    reference_date: datetime.date | None = None,  # injectable for deterministic tests
) -> RuleResult:
    rules = _load_rules()
    result = RuleResult(passed=True)

    today = reference_date or datetime.date.today()
    global_rules: dict = rules.get("global", {})
    type_rules: dict = rules.get("visa_types", {}).get(visa_type_code, {})

    # Global blocked list takes precedence over visa-type-specific rules.
    global_blocked: list[str] = [n.upper() for n in global_rules.get("blocked_nationalities", [])]
    if nationality.upper() in global_blocked:
        result.add_failure(
            "NATIONALITY_GLOBALLY_BLOCKED",
            f"Nationality '{nationality}' is not eligible for any visa type.",
        )

    type_blocked: list[str] = [n.upper() for n in type_rules.get("blocked_nationalities", [])]
    if nationality.upper() in type_blocked:
        result.add_failure(
            "NATIONALITY_BLOCKED_FOR_VISA_TYPE",
            f"Nationality '{nationality}' is not eligible for visa type '{visa_type_code}'.",
        )

    # Non-empty eligible_nationalities acts as an allowlist; empty means all allowed.
    eligible: list[str] = [n.upper() for n in type_rules.get("eligible_nationalities", [])]
    if eligible and nationality.upper() not in eligible:
        result.add_failure(
            "NATIONALITY_NOT_IN_ALLOWLIST",
            f"Visa type '{visa_type_code}' is restricted to specific nationalities "
            f"and '{nationality}' is not on that list.",
        )

    # Visa-type required_documents overrides the global default list.
    default_docs: list[str] = rules.get("default_required_documents", [])
    required_docs: list[str] = type_rules.get("required_documents", default_docs)

    supplied_upper = {d.upper() for d in supplied_document_types}
    missing = [doc for doc in required_docs if doc.upper() not in supplied_upper]
    if missing:
        result.add_failure(
            "MISSING_REQUIRED_DOCUMENTS",
            f"The following documents are required for '{visa_type_code}' but are absent: "
            + ", ".join(missing),
        )

    # Visa-type min_days_before_entry takes precedence over the global default.
    global_min_days: int = global_rules.get("min_days_before_entry", 0)
    min_days: int = type_rules.get("min_days_before_entry", global_min_days)
    days_until_entry: int = (intended_entry_date - today).days

    if days_until_entry < min_days:
        result.add_failure(
            "ENTRY_DATE_TOO_SOON",
            f"Intended entry date must be at least {min_days} day(s) from today. "
            f"Currently only {days_until_entry} day(s) away.",
        )

    return result


def get_required_documents(visa_type_code: str) -> list[str]:
    rules = _load_rules()
    default_docs: list[str] = rules.get("default_required_documents", [])
    return rules.get("visa_types", {}).get(visa_type_code, {}).get(
        "required_documents", default_docs
    )
