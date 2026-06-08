"""LLM provider abstraction for structured chart interpretation."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib import request

from astro.ai_analysis import (
    CEREBRAS_MODEL_OPTIONS,
    CerebrasClient,
    RateLimitError,
)

DEFAULT_CEREBRAS_MODEL = CEREBRAS_MODEL_OPTIONS[1]
DEFAULT_OLLAMA_MODEL = "qwen2.5:7b-instruct"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"


class InterpretationProviderError(RuntimeError):
    """Raised when an interpretation provider request cannot be completed."""


@dataclass(frozen=True)
class InterpretationProviderConfig:
    """Runtime provider configuration for AI-enhanced interpretations."""

    provider: str = "cerebras"
    model: str | None = None
    temperature: float = 0.4
    max_tokens: int = 2048
    ollama_host: str = DEFAULT_OLLAMA_HOST


def get_provider_label(config: InterpretationProviderConfig) -> str:
    """Return a human-readable label for the active interpretation provider."""
    if config.provider == "ollama":
        return f"Ollama · {config.model or DEFAULT_OLLAMA_MODEL}"
    return f"Cerebras · {config.model or DEFAULT_CEREBRAS_MODEL}"


def request_llm_completion(
    *,
    messages: list[dict[str, str]],
    config: InterpretationProviderConfig,
) -> str:
    """Request an interpretation completion from the configured provider."""
    provider = config.provider.strip().lower()
    if provider == "ollama":
        return _request_ollama_completion(messages=messages, config=config)
    return _request_cerebras_completion(messages=messages, config=config)


def _request_cerebras_completion(
    *,
    messages: list[dict[str, str]],
    config: InterpretationProviderConfig,
) -> str:
    """Call Cerebras for AI-enhanced interpretation text."""
    api_key = os.environ.get("CEREBRAS_API_KEY", "").strip()
    if not api_key:
        raise InterpretationProviderError(
            "CEREBRAS_API_KEY is missing for AI-enhanced interpretation."
        )
    try:
        client = CerebrasClient(api_key=api_key)
        return client.chat(
            messages=messages,
            model=config.model or DEFAULT_CEREBRAS_MODEL,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
    except RateLimitError as exc:
        raise InterpretationProviderError(
            "Cerebras rate limit reached during interpretation."
        ) from exc
    except Exception as exc:  # pragma: no cover - network/runtime safety
        raise InterpretationProviderError(str(exc)) from exc


def _request_ollama_completion(
    *,
    messages: list[dict[str, str]],
    config: InterpretationProviderConfig,
) -> str:
    """Call a local Ollama server via its HTTP API."""
    payload = json.dumps(
        {
            "model": config.model or DEFAULT_OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }
    ).encode("utf-8")
    endpoint = config.ollama_host.rstrip("/") + "/api/chat"
    http_request = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
            message = body.get("message", {})
            content = str(message.get("content", "")).strip()
            if not content:
                raise InterpretationProviderError(
                    "Ollama returned an empty interpretation response."
                )
            return content
    except InterpretationProviderError:
        raise
    except Exception as exc:  # pragma: no cover - network/runtime safety
        raise InterpretationProviderError(
            f"Failed to reach Ollama at {endpoint}: {exc}"
        ) from exc


__all__ = [
    "DEFAULT_CEREBRAS_MODEL",
    "DEFAULT_OLLAMA_HOST",
    "DEFAULT_OLLAMA_MODEL",
    "InterpretationProviderConfig",
    "InterpretationProviderError",
    "get_provider_label",
    "request_llm_completion",
]
