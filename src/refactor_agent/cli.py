from __future__ import annotations

import argparse
from pathlib import Path

from refactor_agent.agent import RefactorAgent
from refactor_agent.config import AgentConfig
from refactor_agent.reporting import (
    format_execution_json,
    format_execution_table,
    format_scan_json,
    format_scan_table,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Code Refactor Agent on a codebase.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Analyze files and print a refactoring plan.")
    _add_common_args(scan_parser)

    apply_parser = subparsers.add_parser("apply", help="Apply refactors to files.")
    _add_common_args(apply_parser)
    apply_parser.add_argument(
        "--write",
        action="store_true",
        help="Persist refactor changes to disk. Without this flag, apply runs in preview mode.",
    )
    apply_parser.add_argument(
        "--artifacts-dir",
        default=None,
        help="Directory where unified diff and PR report artifacts will be written.",
    )
    apply_parser.add_argument(
        "--emit-diff",
        action="store_true",
        help="Write a unified patch artifact when changes are applied.",
    )
    apply_parser.add_argument(
        "--emit-pr-report",
        action="store_true",
        help="Write a pull request style markdown summary when changes are applied.",
    )

    return parser


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="Target project path")
    parser.add_argument(
        "--report",
        choices=("table", "json"),
        default="table",
        help="Output format",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Limit the number of scanned files.",
    )
    parser.add_argument(
        "--provider",
        choices=("local", "openai", "anthropic", "claude"),
        default="local",
        help="Planning provider for multi-agent reasoning.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name for the selected provider.",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="Optional custom API endpoint for the selected provider.",
    )
    parser.add_argument(
        "--enable-llm-planning",
        action="store_true",
        help="Use the selected provider to generate planner and reviewer notes.",
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = AgentConfig(
        root=Path(args.path).resolve(),
        write=getattr(args, "write", False),
        max_files=args.max_files,
        provider=args.provider,
        model=args.model,
        api_base=args.api_base,
        enable_llm_planning=args.enable_llm_planning,
        artifact_dir=Path(args.artifacts_dir).resolve() if getattr(args, "artifacts_dir", None) else None,
        emit_diff=getattr(args, "emit_diff", False),
        emit_pr_report=getattr(args, "emit_pr_report", False),
    )
    agent = RefactorAgent(config)

    if args.command == "scan":
        analyses, plan = agent.scan()
        output = format_scan_json(analyses, plan) if args.report == "json" else format_scan_table(analyses, plan)
    else:
        _, _, result = agent.apply()
        output = format_execution_json(result) if args.report == "json" else format_execution_table(result)

    print(output)


if __name__ == "__main__":
    main()
