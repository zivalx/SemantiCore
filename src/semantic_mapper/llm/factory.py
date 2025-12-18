"""LLM provider factory."""

import os
from .base import BaseLLMProvider
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider


class LLMFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create(provider: str = None) -> BaseLLMProvider:
        """
        Create an LLM provider.

        Args:
            provider: Provider name ("anthropic" or "openai")
                     Defaults to LLM_PROVIDER env var or "anthropic"

        Returns:
            LLM provider instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = provider or os.getenv("LLM_PROVIDER", "anthropic")
        provider = provider.lower()

        if provider == "anthropic":
            return AnthropicProvider()
        elif provider == "openai":
            return OpenAIProvider()
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: anthropic, openai"
            )

    @staticmethod
    def create_anthropic(api_key: str = None, model: str = None) -> AnthropicProvider:
        """Create Anthropic provider with specific configuration."""
        return AnthropicProvider(api_key=api_key, model=model)

    @staticmethod
    def create_openai(api_key: str = None, model: str = None) -> OpenAIProvider:
        """Create OpenAI provider with specific configuration."""
        return OpenAIProvider(api_key=api_key, model=model)
