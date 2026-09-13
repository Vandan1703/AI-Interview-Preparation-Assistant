"""Provider protocol so the graph is independent of any one LLM vendor."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMProviderError(RuntimeError):
    """Raised when a provider cannot produce a valid model response."""


class LLMProvider(ABC):
    """Minimal interface needed by the graph's individual agents."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a textual response from a system and user prompt."""

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel],
    ) -> BaseModel | str:
        """Generate a schema-shaped result when the provider supports it.

        The text fallback keeps alternative providers simple; Gemini overrides
        this with its native JSON-schema mode without adding another LLM call.
        """

        del schema
        return await self.generate(system_prompt, user_prompt)
