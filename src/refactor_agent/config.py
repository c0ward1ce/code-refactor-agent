from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_INCLUDE = (
    "*.py",
    "*.js",
    "*.jsx",
    "*.ts",
    "*.tsx",
    "*.java",
    "*.go",
)


@dataclass(slots=True)
class AgentConfig:
    root: Path
    include: tuple[str, ...] = DEFAULT_INCLUDE
    exclude_dirs: tuple[str, ...] = (
        ".git",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        ".tmp-tests",
        ".tmp-pip",
    )
    enabled_rules: tuple[str, ...] = (
        "python-none-comparison",
        "redundant-boolean-comparison",
        "trailing-whitespace",
        "eof-newline",
    )
    write: bool = False
    max_files: int | None = None
    provider: str = "local"
    model: str | None = None
    api_base: str | None = None
    enable_llm_planning: bool = False
    artifact_dir: Path | None = None
    emit_diff: bool = False
    emit_pr_report: bool = False
    extra_metadata: dict[str, str] = field(default_factory=dict)
