import re
from typing import Any, Dict
from schema import ActionType, Step

class SecurityException(Exception):
    pass

class GuardrailEngine:
    def __init__(self, allowed_domains: list[str]):
        self.allowed_domains = allowed_domains
        self.restricted_actions = [ActionType.CLICK]  # Example restricted actions monitored for risk

    def validate_url(self, url: str) -> bool:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc or urlparse(url).path.split('/')[0]
        # Strip port numbers if present
        domain = domain.split(':')[0]
        
        for allowed in self.allowed_domains:
            if domain == allowed or domain.endswith("." + allowed) or allowed == "localhost":
                return True
        raise SecurityException(f"Access to domain '{domain}' blocked by guardrails.")

    def inspect_step(self, step: Step) -> bool:
        if step.is_risky:
            print(f"[GUARDRAIL WARNING] Step '{step.step_id}' marked as risky action. Approval required.")
        return True

    @staticmethod
    def redact_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Redacts sensitive PII and credential patterns from dictionaries."""
        redacted = {}
        sensitive_keys = {"ssn", "password", "secret", "token", "cvv", "credit_card"}
        for k, v in data.items():
            if any(s in k.lower() for s in sensitive_keys):
                redacted[k] = "[REDACTED]"
            elif isinstance(v, str) and re.match(r"^\d{3}-\d{2}-\d{4}$", v):  # SSN pattern
                redacted[k] = "***-**-****"
            else:
                redacted[k] = v
        return redacted