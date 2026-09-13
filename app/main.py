"""FastAPI entry point serving both the coaching API and its web client."""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.graphs.workflow import InterviewWorkflow
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.providers.base import LLMProviderError
from app.services.providers.factory import create_provider

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.settings = settings
    app.state.workflow = None
    try:
        app.state.workflow = InterviewWorkflow(create_provider(settings))
        logger.info("Interview workflow initialized with provider '%s'", settings.llm_provider)
    except LLMProviderError as exc:
        logger.warning("Workflow not initialized: %s", exc)
    yield


app = FastAPI(
    title="AI Interview Preparation Assistant",
    version="1.0.0",
    description="A LangGraph-powered DSA coaching assistant that guides without code solutions.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    """Serve the single-page, dependency-free frontend."""

    # Avoid stale UI copy after a server-side frontend update during development.
    return FileResponse(
        BASE_DIR / "templates" / "index.html",
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    """Report whether the API can currently accept analyses."""

    return {"status": "ok" if request.app.state.workflow else "misconfigured"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    """Run the three-call coaching graph for one validated interview question."""

    workflow: InterviewWorkflow | None = request.app.state.workflow
    if workflow is None:
        raise HTTPException(status_code=503, detail="LLM is not configured. Set GEMINI_API_KEY in .env and restart.")
    try:
        analysis = await asyncio.wait_for(
            workflow.analyze(payload.question),
            timeout=request.app.state.settings.workflow_timeout_seconds,
        )
        return AnalyzeResponse(analysis=analysis)
    except TimeoutError as exc:
        logger.warning("Interview workflow exceeded its configured deadline")
        raise HTTPException(
            status_code=504,
            detail="The model provider took too long to respond. Please try again shortly.",
        ) from exc
    except LLMProviderError as exc:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
