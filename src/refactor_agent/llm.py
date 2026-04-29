from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol
from urllib import error, request


class LLMProvider(Protocol):
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        ...


@dataclass(slots=True)
class LocalProvider:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "Local provider fallback: prioritize low-risk edits, group changes by language, "
            "and keep refactors reviewable in a single pull request."
        )


@dataclass(slots=True)
class OpenAIProvider:
    model: str
    api_base: str = "https://api.openai.com/v1/responses"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.api_base,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc
        try:
            return body["output"][0]["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected OpenAI response shape: {body}") from exc


@dataclass(slots=True)
class AnthropicProvider:
    model: str
    api_base: str = "https://api.anthropic.com/v1/messages"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set.")
        payload = {
            "model": self.model,
            "max_tokens": 600,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.api_base,
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"Anthropic request failed: {exc}") from exc
        try:
            return body["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Anthropic response shape: {body}") from exc


def build_provider(provider: str, model: str | None, api_base: str | None) -> LLMProvider:
    provider_name = provider.lower()
    if provider_name == "openai":
        return OpenAIProvider(model=model or "gpt-4.1-mini", api_base=api_base or "https://api.openai.com/v1/responses")
    if provider_name in {"anthropic", "claude"}:
        return AnthropicProvider(
            model=model or "claude-3-5-sonnet-latest",
            api_base=api_base or "https://api.anthropic.com/v1/messages",
        )
    return LocalProvider()
