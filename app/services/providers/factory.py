"""Provider selection driven by settings, not graph code."""

from app.core.config import Settings
from app.services.providers.base import LLMProvider, LLMProviderError
from app.services.providers.gemini import GeminiProvider


def create_provider(settings: Settings) -> LLMProvider:
    """Create the configured provider, with actionable configuration errors."""

    if settings.llm_provider.lower() == "gemini":
        if not settings.gemini_api_key or settings.gemini_api_key == "replace_me":
            raise LLMProviderError("GEMINI_API_KEY is missing. Add a valid key to your .env file.")
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model,
            temperature=settings.llm_temperature,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    raise LLMProviderError(
        f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. Add its adapter in app/services/providers."
    )
