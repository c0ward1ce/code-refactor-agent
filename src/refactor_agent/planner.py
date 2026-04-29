from __future__ import annotations

from collections import Counter

from refactor_agent.config import AgentConfig
from refactor_agent.models import FileAnalysis, PlanStep
from refactor_agent.multi_agent import MultiAgentCoordinator


class Planner:
    def __init__(self, config: AgentConfig) -> None:
        self.coordinator = MultiAgentCoordinator(config)

    def build(self, analyses: list[FileAnalysis]) -> list[PlanStep]:
        steps: list[PlanStep] = []
        for analysis in analyses:
            if not analysis.findings:
                continue
            counts = Counter(f.rule_id for f in analysis.findings)
            score = sum(f.severity for f in analysis.findings)
            summary = ", ".join(f"{rule_id}: {count}" for rule_id, count in sorted(counts.items()))
            step = PlanStep(
                path=analysis.path,
                language=analysis.language,
                summary=summary,
                rule_ids=sorted(counts.keys()),
                finding_count=len(analysis.findings),
                score=score,
            )
            steps.append(self.coordinator.plan_step(step))
        return sorted(steps, key=lambda item: (-item.score, str(item.path)))
