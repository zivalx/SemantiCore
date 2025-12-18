"""OpenAI LLM provider."""

import os
import json
from typing import Optional, Type

from pydantic import BaseModel

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """LLM provider using OpenAI API."""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (default: from OPENAI_API_KEY env var)
            model: Model name (default: from OPENAI_MODEL env var)
        """
        if OpenAI is None:
            raise ImportError("openai package required. Install with: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.client = OpenAI(api_key=self.api_key)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> BaseModel:
        """
        Generate structured output using OpenAI.

        Uses JSON mode with schema to ensure structured output.
        """
        # Build system prompt with schema
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)

        full_system = f"""You are a semantic ontology expert. You must respond with valid JSON that matches this schema:

{schema_str}

Respond ONLY with valid JSON."""

        if system_prompt:
            full_system = f"{system_prompt}\n\n{full_system}"

        # Call OpenAI API with JSON mode
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": full_system},
                {"role": "user", "content": prompt},
            ],
        )

        # Extract and parse JSON
        content = response.choices[0].message.content

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
        """Generate text output using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt or "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content
