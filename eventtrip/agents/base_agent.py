"""Base class for deterministic Markdown-writing agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import re
from typing import Any

from eventtrip.llm_client import generate_text
from eventtrip.markdown_io import list_agent_outputs, read_markdown, write_markdown


class BaseAgent(ABC):
    name: str = "base_agent"

    def __init__(self, use_llm: bool = False) -> None:
        self.use_llm = use_llm

    def read_memory(self, run_dir: Path) -> dict[str, tuple[dict, str]]:
        memory: dict[str, tuple[dict, str]] = {}
        for path in list_agent_outputs(run_dir):
            memory[path.name] = read_markdown(path)
        return memory

    def write_output(
        self,
        run_dir: Path,
        filename: str,
        frontmatter: dict[str, Any],
        body: str,
    ) -> Path:
        metadata = {
            "agent": self.name,
            "status": "completed",
            "confidence": "medium",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            **frontmatter,
        }
        path = run_dir / filename
        write_markdown(path, metadata, body)
        return path

    def polish_if_enabled(self, body: str) -> str:
        if not self.use_llm:
            return body
        polished = generate_text(
            system_prompt=(
                "You polish Markdown for an event-trip planning system. Preserve all "
                "numbers, dates, costs, headings, option names, and recommendation labels exactly."
            ),
            user_prompt=body,
        )
        if polished.startswith("ERROR:"):
            return body + f"\n\n> LLM polishing unavailable: {polished}"
        if not self._preserves_protected_tokens(body, polished):
            return body + "\n\n> LLM polishing was discarded because protected numbers or labels changed."
        return polished

    @staticmethod
    def _preserves_protected_tokens(original: str, candidate: str) -> bool:
        token_pattern = r"\$\d+(?:\.\d+)?|\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)?%?/\d+|\d+(?:\.\d+)?%?"
        original_tokens = set(re.findall(token_pattern, original))
        candidate_tokens = set(re.findall(token_pattern, candidate))
        option_labels = {"Option A", "Option B", "Option C", "Option D"}
        original_labels = {label for label in option_labels if label in original}
        candidate_labels = {label for label in option_labels if label in candidate}
        return original_tokens == candidate_tokens and original_labels == candidate_labels

    @abstractmethod
    def run(self, trip_request: dict, run_dir: Path, context: dict[str, Any]) -> dict[str, Any]:
        """Run the agent and return context updates."""
