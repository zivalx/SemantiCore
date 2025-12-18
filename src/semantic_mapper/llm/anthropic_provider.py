"""Anthropic Claude LLM provider."""

import os
import json
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """LLM provider using Anthropic Claude API."""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (default: from ANTHROPIC_API_KEY env var)
            model: Model name (default: from ANTHROPIC_MODEL env var)
        """
        if Anthropic is None:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required")

        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.client = Anthropic(api_key=self.api_key)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> BaseModel:
        """
        Generate structured output using Claude.

        Uses JSON mode with schema to ensure structured output.
        """
        # Build system prompt with schema
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)

        full_system = f"""You are a semantic ontology expert. You must respond with valid JSON that matches this schema:

{schema_str}

Respond ONLY with valid JSON. Do not include any text before or after the JSON."""

        if system_prompt:
            full_system = f"{system_prompt}\n\n{full_system}"

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=full_system,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract and parse JSON
        content = response.content[0].text

        # Try to extract JSON if it's wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Parse into Pydantic model
        try:
            data = json.loads(content)
            return response_model(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM output as JSON: {e}\nOutput: {content}")
        except Exception as e:
            raise ValueError(f"Failed to validate LLM output: {e}\nOutput: {content}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Generate text output using Claude."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text
