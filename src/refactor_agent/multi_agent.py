from __future__ import annotations

from collections import Counter

from refactor_agent.config import AgentConfig
from refactor_agent.llm import LLMProvider, build_provider
from refactor_agent.models import AgentInsight, FileAnalysis, PlanStep


class MultiAgentCoordinator:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.provider: LLMProvider = build_provider(config.provider, config.model, config.api_base)

    def analyze_file(self, analysis: FileAnalysis) -> list[AgentInsight]:
        findings = Counter(f.rule_id for f in analysis.findings)
        summary = ", ".join(f"{rule_id} x{count}" for rule_id, count in sorted(findings.items())) or "no findings"
        architect = AgentInsight(
            agent_name="architect-agent",
            role="architecture review",
            content=f"{analysis.language} file reviewed. Hotspots: {summary}.",
        )
        reviewer = AgentInsight(
            agent_name="reviewer-agent",
            role="risk review",
            content="Prefer minimal edits, preserve semantics, and verify syntax after each refactor.",
        )
        insights = [architect, reviewer]

        if self.config.enable_llm_planning:
            llm_note = self.provider.complete(
                "You are a refactoring planner.",
                (
                    f"Language: {analysis.language}\n"
                    f"File: {analysis.path.name}\n"
                    f"Findings: {summary}\n"
                    "Return a short refactor strategy."
                ),
            )
            insights.append(
                AgentInsight(
                    agent_name="planner-agent",
                    role="llm strategy",
                    content=llm_note.strip(),
                )
            )
        return insights

    def plan_step(self, step: PlanStep) -> PlanStep:
        rationale = (
            f"Prioritize {step.language} refactor because score={step.score} across "
            f"{step.finding_count} findings. Keep changes grouped by {', '.join(step.rule_ids)}."
        )
        owner = "writer-agent" if step.score <= 3 else "senior-writer-agent"
        if self.config.enable_llm_planning:
            llm_rationale = self.provider.complete(
                "You are a senior refactor orchestrator.",
                (
                    f"Create a short execution rationale for a {step.language} refactor.\n"
                    f"Rule ids: {', '.join(step.rule_ids)}\n"
                    f"Finding count: {step.finding_count}\n"
                ),
            )
            rationale = llm_rationale.strip()
        step.owner_agent = owner
        step.rationale = rationale
        return step
