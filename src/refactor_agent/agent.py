from __future__ import annotations

from refactor_agent.analyzer import Analyzer
from refactor_agent.artifacts import ArtifactWriter
from refactor_agent.config import AgentConfig
from refactor_agent.executor import Executor
from refactor_agent.planner import Planner
from refactor_agent.verifier import Verifier


class RefactorAgent:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.analyzer = Analyzer(config)
        self.planner = Planner(config)
        self.executor = Executor(config)
        self.verifier = Verifier()

    def scan(self):
        analyses = self.analyzer.run()
        plan = self.planner.build(analyses)
        return analyses, plan

    def apply(self):
        analyses, plan = self.scan()
        result = self.executor.run(plan)
        if self.config.write:
            result = self.verifier.run(result)
            if self.config.artifact_dir and self.config.emit_diff:
                writer = ArtifactWriter(self.config.artifact_dir)
                result = writer.write(result, plan)
            if self.config.artifact_dir and self.config.emit_pr_report:
                writer = ArtifactWriter(self.config.artifact_dir)
                result = writer.write_pr_report(result, plan)
        return analyses, plan, result
