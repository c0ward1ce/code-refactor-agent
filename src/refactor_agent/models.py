from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Finding:
    rule_id: str
    title: str
    description: str
    file_path: Path
    line: int
    severity: int = 1
    language: str = "text"


@dataclass(slots=True)
class AgentInsight:
    agent_name: str
    role: str
    content: str


@dataclass(slots=True)
class FileAnalysis:
    path: Path
    language: str
    findings: list[Finding] = field(default_factory=list)
    agent_insights: list[AgentInsight] = field(default_factory=list)


@dataclass(slots=True)
class FileChange:
    path: Path
    language: str
    original: str
    updated: str
    applied_rules: list[str] = field(default_factory=list)
    diff: str = ""

    @property
    def changed(self) -> bool:
        return self.original != self.updated


@dataclass(slots=True)
class PlanStep:
    path: Path
    language: str
    summary: str
    rule_ids: list[str]
    finding_count: int
    score: int
    owner_agent: str = "planner"
    rationale: str = ""


@dataclass(slots=True)
class PullRequestArtifact:
    title: str
    body: str
    changed_files: int


@dataclass(slots=True)
class ExecutionResult:
    changed_files: list[FileChange] = field(default_factory=list)
    unchanged_files: list[Path] = field(default_factory=list)
    verification_errors: list[str] = field(default_factory=list)
    pr_artifact: PullRequestArtifact | None = None
    artifact_paths: list[Path] = field(default_factory=list)

