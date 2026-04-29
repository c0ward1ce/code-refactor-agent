from __future__ import annotations

from pathlib import Path

from refactor_agent.config import AgentConfig


def discover_files(config: AgentConfig) -> list[Path]:
    files: list[Path] = []
    for pattern in config.include:
        for candidate in config.root.rglob(pattern):
            if _is_excluded(candidate, config):
                continue
            if candidate.is_file():
                files.append(candidate)

    files = sorted(set(files))
    if config.max_files is not None:
        return files[: config.max_files]
    return files


def _is_excluded(path: Path, config: AgentConfig) -> bool:
    return any(part in config.exclude_dirs for part in path.parts)

