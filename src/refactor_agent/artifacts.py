from __future__ import annotations

from pathlib import Path

from refactor_agent.models import ExecutionResult, PlanStep, PullRequestArtifact


class ArtifactWriter:
    def __init__(self, artifact_dir: Path) -> None:
        self.artifact_dir = artifact_dir
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def write(self, result: ExecutionResult, plan: list[PlanStep]) -> ExecutionResult:
        if result.changed_files:
            diff_path = self.artifact_dir / "refactor.patch"
            diff_payload = "\n".join(change.diff for change in result.changed_files if change.diff)
            diff_path.write_text(diff_payload, encoding="utf-8")
            result.artifact_paths.append(diff_path)

        return result

    def write_pr_report(self, result: ExecutionResult, plan: list[PlanStep]) -> ExecutionResult:
        pr_artifact = build_pr_artifact(result, plan)
        report_path = self.artifact_dir / "pull_request.md"
        report_path.write_text(f"# {pr_artifact.title}\n\n{pr_artifact.body}\n", encoding="utf-8")
        result.pr_artifact = pr_artifact
        result.artifact_paths.append(report_path)
        return result


def build_pr_artifact(result: ExecutionResult, plan: list[PlanStep]) -> PullRequestArtifact:
    language_summary: dict[str, int] = {}
    for step in plan:
        language_summary[step.language] = language_summary.get(step.language, 0) + 1
    language_text = ", ".join(f"{language}: {count}" for language, count in sorted(language_summary.items())) or "none"
    body_lines = [
        "## Summary",
        f"- Refactored {len(result.changed_files)} files with safe automated rules.",
        f"- Languages touched: {language_text}.",
        "",
        "## What Changed",
    ]
    for change in result.changed_files:
        body_lines.append(f"- `{change.path.name}`: {', '.join(change.applied_rules)}")
    if result.verification_errors:
        body_lines.extend(["", "## Verification Risks"])
        for error in result.verification_errors:
            body_lines.append(f"- {error}")
    else:
        body_lines.extend(["", "## Verification", "- Python files were compiled after rewrite and non-Python files passed a delimiter balance check."])
    return PullRequestArtifact(
        title="refactor: apply safe multi-language cleanup",
        body="\n".join(body_lines),
        changed_files=len(result.changed_files),
    )
