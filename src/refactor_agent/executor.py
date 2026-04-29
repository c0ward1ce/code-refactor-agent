from __future__ import annotations

import difflib

from refactor_agent.config import AgentConfig
from refactor_agent.models import ExecutionResult, FileChange, PlanStep
from refactor_agent.rules import build_rules


class Executor:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.rules = build_rules()

    def run(self, plan: list[PlanStep]) -> ExecutionResult:
        result = ExecutionResult()
        for step in plan:
            original = step.path.read_text(encoding="utf-8")
            updated = original
            applied_rules: list[str] = []
            for rule_id in step.rule_ids:
                rule = self.rules[rule_id]
                if not rule.supports(step.language):
                    continue
                new_content = rule.apply(updated, step.language)
                if new_content != updated:
                    applied_rules.append(rule_id)
                    updated = new_content

            change = FileChange(
                path=step.path,
                language=step.language,
                original=original,
                updated=updated,
                applied_rules=applied_rules,
                diff=_build_diff(step.path.name, original, updated),
            )

            if change.changed:
                if self.config.write:
                    step.path.write_text(change.updated, encoding="utf-8")
                result.changed_files.append(change)
            else:
                result.unchanged_files.append(step.path)
        return result


def _build_diff(file_name: str, original: str, updated: str) -> str:
    if original == updated:
        return ""
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{file_name}",
            tofile=f"b/{file_name}",
        )
    )
