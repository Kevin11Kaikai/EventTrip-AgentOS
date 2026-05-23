"""Optional OhMyGPT OpenAI-compatible LLM client."""

from __future__ import annotations

import os

try:  # pragma: no cover - optional dependency behavior
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


DEFAULT_BASE_URL = "https://api.ohmygpt.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def configured_model() -> str:
    """Return the configured model name without reading or exposing secrets."""
    return os.getenv("OHMYGPT_MODEL", DEFAULT_MODEL)


def generate_text(system_prompt: str, user_prompt: str) -> str:
    """Generate text through OhMyGPT when explicitly configured.

    The default demo does not call this function. It is only used when
    orchestrator is run with --use-llm.
    """
    api_key = os.getenv("OHMYGPT_API_KEY")
    if not api_key:
        return (
            "ERROR: OHMYGPT_API_KEY is missing. Set it in the environment or .env "
            "before running with --use-llm."
        )

    base_url = os.getenv("OHMYGPT_BASE_URL", DEFAULT_BASE_URL)
    model = os.getenv("OHMYGPT_MODEL", DEFAULT_MODEL)

    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover - depends on local environment
        return f"ERROR: OpenAI Python SDK is unavailable: {exc}"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:  # pragma: no cover - real API path
        return f"ERROR: LLM request failed: {exc}"
