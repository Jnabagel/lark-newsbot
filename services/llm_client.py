"""LLM client wrapper for OpenAI and Anthropic APIs."""

import logging
from typing import Optional
from openai import OpenAI
from anthropic import Anthropic

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin wrapper for LLM API calls."""

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ('openai' or 'anthropic'). Defaults to settings.
            api_key: API key. Defaults to settings.
        """
        self.provider = provider or settings.llm_provider.lower()
        api_key = api_key or settings.get_llm_api_key()

        if self.provider == "openai":
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
        elif self.provider == "anthropic":
            base_url = settings.anthropic_base_url or "https://api.anthropic.com"
            self.client = Anthropic(api_key=api_key, base_url=base_url)
            self.model = "claude-3-5-sonnet-20241022"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        logger.info(f"Initialized LLM client with provider: {self.provider}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: System prompt (if supported)

        Returns:
            Generated text
        """
        try:
            if self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens or 4096,
                    temperature=temperature,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text

        except Exception as e:
            logger.error(f"LLM generation error: {e}", exc_info=True)
            raise


