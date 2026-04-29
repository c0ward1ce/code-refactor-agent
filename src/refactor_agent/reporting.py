from __future__ import annotations

import json

from refactor_agent.models import ExecutionResult, FileAnalysis, PlanStep


def format_scan_table(analyses: list[FileAnalysis], plan: list[PlanStep]) -> str:
    lines = ["Refactor Scan Report", "====================", ""]
    lines.append(f"Files analyzed: {len(analyses)}")
    lines.append(f"Files with findings: {len(plan)}")
    lines.append("")
    for step in plan:
        lines.append(f"- {step.path}")
        lines.append(
            f"  language={step.language} findings={step.finding_count} score={step.score} owner={step.owner_agent}"
        )
        lines.append(f"  rules={', '.join(step.rule_ids)}")
        lines.append(f"  rationale={step.rationale}")
    if not plan:
        lines.append("No issues found.")
    return "\n".join(lines)


def format_execution_table(result: ExecutionResult) -> str:
    lines = ["Refactor Execution Report", "=========================", ""]
    lines.append(f"Changed files: {len(result.changed_files)}")
    lines.append(f"Unchanged files: {len(result.unchanged_files)}")
    for change in result.changed_files:
        lines.append(f"- {change.path}")
        lines.append(f"  language={change.language} applied_rules={', '.join(change.applied_rules)}")
    if result.pr_artifact is not None:
        lines.append("")
        lines.append(f"PR title: {result.pr_artifact.title}")
    if result.artifact_paths:
        lines.append("Artifacts:")
        for path in result.artifact_paths:
            lines.append(f"- {path}")
    if result.verification_errors:
        lines.append("")
        lines.append("Verification errors:")
        for error in result.verification_errors:
            lines.append(f"- {error}")
    return "\n".join(lines)


def format_scan_json(analyses: list[FileAnalysis], plan: list[PlanStep]) -> str:
    payload = {
        "files_analyzed": len(analyses),
        "files_with_findings": len(plan),
        "plan": [
            {
                "path": str(step.path),
                "language": step.language,
                "summary": step.summary,
                "rule_ids": step.rule_ids,
                "finding_count": step.finding_count,
                "score": step.score,
                "owner_agent": step.owner_agent,
                "rationale": step.rationale,
            }
            for step in plan
        ],
        "agent_insights": {
            str(analysis.path): [
                {
                    "agent_name": insight.agent_name,
                    "role": insight.role,
                    "content": insight.content,
                }
                for insight in analysis.agent_insights
            ]
            for analysis in analyses
        },
    }
    return json.dumps(payload, indent=2)


def format_execution_json(result: ExecutionResult) -> str:
    payload = {
        "changed_files": [
            {
                "path": str(change.path),
                "language": change.language,
                "applied_rules": change.applied_rules,
                "diff": change.diff,
            }
            for change in result.changed_files
        ],
        "unchanged_files": [str(path) for path in result.unchanged_files],
        "verification_errors": result.verification_errors,
        "pull_request": (
            {
                "title": result.pr_artifact.title,
                "body": result.pr_artifact.body,
            }
            if result.pr_artifact
            else None
        ),
        "artifact_paths": [str(path) for path in result.artifact_paths],
    }
    return json.dumps(payload, indent=2)
