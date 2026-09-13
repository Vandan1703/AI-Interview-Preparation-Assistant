"""Google Gemini implementation of the provider interface."""

import asyncio
import logging
from typing import NoReturn, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from app.services.providers.base import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    """Adapt LangChain's Gemini chat model to the application's provider contract."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        timeout_seconds: float,
    ) -> None:
        self._model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            timeout=timeout_seconds,
            # The REST transport is reliable in restricted local environments
            # where the default gRPC transport can stall before timing out.
            transport="rest",
            # langchain-google-genai interprets this as max *attempts*.
            # One attempt ensures quota (429) errors are never retried.
            max_retries=1,
        )

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = await asyncio.to_thread(
                self._model.invoke,
                [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)],
            )
        except Exception as exc:  # Provider-specific exception types are not stable.
            self._raise_provider_error(exc)

        content = response.content
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part) for part in content
            )
        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError("Gemini returned an empty response.")
        return content.strip()

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[T],
    ) -> T:
        """Use Gemini JSON-schema mode for one-call, Pydantic-valid output."""

        try:
            structured_model = self._model.with_structured_output(schema, method="json_mode")
            result = await asyncio.to_thread(
                structured_model.invoke,
                [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)],
            )
            return schema.model_validate(result)
        except Exception as exc:  # Provider-specific exception types are not stable.
            self._raise_provider_error(exc)

    def _raise_provider_error(self, exc: Exception) -> NoReturn:
        """Translate Gemini exceptions without logging prompts or credentials."""

        logger.exception("Gemini generation failed")
        error_text = str(exc).lower()
        if "quota" in error_text or "resource_exhausted" in error_text:
            raise LLMProviderError(
                "Gemini rejected this request because the configured API key has no available quota. "
                "Enable billing or use a key/project with Gemini API quota."
            ) from exc
        if "no longer available" in error_text or "not found" in error_text:
            raise LLMProviderError(
                "The configured Gemini model is unavailable to this API key. "
                "Set GEMINI_MODEL to a model listed for your project, such as gemini-flash-latest."
            ) from exc
        raise LLMProviderError("The Gemini service could not complete the analysis.") from exc
