from __future__ import annotations

import py_compile

from refactor_agent.models import ExecutionResult


class Verifier:
    def run(self, result: ExecutionResult) -> ExecutionResult:
        for change in result.changed_files:
            if change.language == "python":
                try:
                    py_compile.compile(str(change.path), doraise=True)
                except py_compile.PyCompileError as exc:
                    result.verification_errors.append(f"{change.path}: {exc.msg}")
            else:
                if not _basic_balance_check(change.updated):
                    result.verification_errors.append(
                        f"{change.path}: basic delimiter balance check failed for {change.language}."
                    )
        return result


def _basic_balance_check(content: str) -> bool:
    pairs = {"(": ")", "{": "}", "[": "]"}
    closing = {value: key for key, value in pairs.items()}
    stack: list[str] = []
    for char in content:
        if char in pairs:
            stack.append(char)
        elif char in closing:
            if not stack or stack[-1] != closing[char]:
                return False
            stack.pop()
    return not stack
