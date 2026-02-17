"""Custom exception for rule violations.

Separating this from the rules module keeps imports clean
and lets routes catch violations without importing the rules directly.

rule_code provides a machine-readable identifier for the violation
(e.g., DUPLICATE_JOIN, NOT_FIRST_IN_QUEUE) so frontends can display
structured feedback without parsing human-readable messages.
"""


class RuleViolation(Exception):
    """Raised when a queue business rule is violated."""

    def __init__(self, reason: str, rule_code: str = "RULE_VIOLATION"):
        self.reason = reason
        self.rule_code = rule_code
        super().__init__(reason)
