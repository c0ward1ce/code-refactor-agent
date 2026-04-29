from __future__ import annotations

from refactor_agent.config import AgentConfig
from refactor_agent.discovery import discover_files
from refactor_agent.languages import detect_language
from refactor_agent.models import FileAnalysis
from refactor_agent.multi_agent import MultiAgentCoordinator
from refactor_agent.rules import build_rules


class Analyzer:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.rules = build_rules()
        self.coordinator = MultiAgentCoordinator(config)

    def run(self) -> list[FileAnalysis]:
        analyses: list[FileAnalysis] = []
        for path in discover_files(self.config):
            content = path.read_text(encoding="utf-8")
            language = detect_language(path)
            analysis = FileAnalysis(path=path, language=language)
            for rule_id in self.config.enabled_rules:
                rule = self.rules[rule_id]
                if not rule.supports(language):
                    continue
                analysis.findings.extend(rule.find(content, str(path), language))
            analysis.agent_insights.extend(self.coordinator.analyze_file(analysis))
            analyses.append(analysis)
        return analyses
