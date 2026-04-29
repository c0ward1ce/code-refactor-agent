from __future__ import annotations

from abc import ABC, abstractmethod

from refactor_agent.models import Finding


class RefactorRule(ABC):
    rule_id: str
    title: str
    languages: tuple[str, ...] = ("text",)

    def supports(self, language: str) -> bool:
        return "*" in self.languages or language in self.languages

    @abstractmethod
    def find(self, content: str, file_path: str, language: str) -> list[Finding]:
        raise NotImplementedError

    @abstractmethod
    def apply(self, content: str, language: str) -> str:
        raise NotImplementedError
