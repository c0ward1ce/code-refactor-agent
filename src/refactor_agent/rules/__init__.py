from refactor_agent.rules.text_rules import (
    EndOfFileNewlineRule,
    PythonNoneComparisonRule,
    RedundantBooleanComparisonRule,
    TrailingWhitespaceRule,
)


def build_rules() -> dict[str, object]:
    rules = [
        PythonNoneComparisonRule(),
        RedundantBooleanComparisonRule(),
        TrailingWhitespaceRule(),
        EndOfFileNewlineRule(),
    ]
    return {rule.rule_id: rule for rule in rules}
