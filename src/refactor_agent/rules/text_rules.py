from __future__ import annotations

import re
from pathlib import Path

from refactor_agent.models import Finding
from refactor_agent.rules.base import RefactorRule


class PythonNoneComparisonRule(RefactorRule):
    rule_id = "python-none-comparison"
    title = "Normalize Python None comparisons"
    languages = ("python",)

    _eq_pattern = re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*==\s*None\b")
    _ne_pattern = re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*!=\s*None\b")

    def find(self, content: str, file_path: str, language: str) -> list[Finding]:
        findings: list[Finding] = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if "== None" in line or "!= None" in line:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title=self.title,
                        description="Use 'is None' or 'is not None' for identity checks.",
                        file_path=Path(file_path),
                        line=line_number,
                        severity=2,
                        language=language,
                    )
                )
        return findings

    def apply(self, content: str, language: str) -> str:
        content = self._eq_pattern.sub(r"\g<left> is None", content)
        content = self._ne_pattern.sub(r"\g<left> is not None", content)
        return content


class RedundantBooleanComparisonRule(RefactorRule):
    rule_id = "redundant-boolean-comparison"
    title = "Remove redundant boolean comparisons"
    languages = ("python", "javascript", "typescript", "java", "go")

    _py_patterns = (
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*==\s*True\b"), r"\g<left>"),
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*==\s*False\b"), r"not \g<left>"),
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*!=\s*True\b"), r"not \g<left>"),
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*!=\s*False\b"), r"\g<left>"),
    )
    _c_like_patterns = (
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*(===|==)\s*true\b"), r"\g<left>"),
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*(===|==)\s*false\b"), r"!\g<left>"),
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*(!==|!=)\s*true\b"), r"!\g<left>"),
        (re.compile(r"(?P<left>\b[\w\]\)\.'\"]+\b)\s*(!==|!=)\s*false\b"), r"\g<left>"),
    )

    def find(self, content: str, file_path: str, language: str) -> list[Finding]:
        tokens = ("== True", "== False", "!= True", "!= False") if language == "python" else (
            "=== true",
            "=== false",
            "!== true",
            "!== false",
            "== true",
            "== false",
            "!= true",
            "!= false",
        )
        findings: list[Finding] = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if any(token in line for token in tokens):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title=self.title,
                        description="Prefer direct boolean expressions over explicit comparisons.",
                        file_path=Path(file_path),
                        line=line_number,
                        severity=1,
                        language=language,
                    )
                )
        return findings

    def apply(self, content: str, language: str) -> str:
        patterns = self._py_patterns if language == "python" else self._c_like_patterns
        for pattern, replacement in patterns:
            content = pattern.sub(replacement, content)
        return content


class TrailingWhitespaceRule(RefactorRule):
    rule_id = "trailing-whitespace"
    title = "Remove trailing whitespace"
    languages = ("*",)

    def find(self, content: str, file_path: str, language: str) -> list[Finding]:
        findings: list[Finding] = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if line.rstrip() != line:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title=self.title,
                        description="Trailing spaces make diffs noisy and reduce readability.",
                        file_path=Path(file_path),
                        line=line_number,
                        severity=1,
                        language=language,
                    )
                )
        return findings

    def apply(self, content: str, language: str) -> str:
        lines = content.splitlines()
        if not lines:
            return content
        trimmed = [line.rstrip() for line in lines]
        trailing_newline = "\n" if content.endswith("\n") else ""
        return "\n".join(trimmed) + trailing_newline


class EndOfFileNewlineRule(RefactorRule):
    rule_id = "eof-newline"
    title = "Normalize final newline"
    languages = ("*",)

    def find(self, content: str, file_path: str, language: str) -> list[Finding]:
        if not content:
            return []
        if content.endswith("\n") and not content.endswith("\n\n"):
            return []
        line_number = max(1, len(content.splitlines()))
        return [
            Finding(
                rule_id=self.rule_id,
                title=self.title,
                description="Files should end with exactly one newline.",
                file_path=Path(file_path),
                line=line_number,
                severity=1,
                language=language,
            )
        ]

    def apply(self, content: str, language: str) -> str:
        if not content:
            return content
        return content.rstrip("\n") + "\n"
