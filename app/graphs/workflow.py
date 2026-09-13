"""LangGraph workflow assembly and public analysis entry point."""

from langgraph.graph import END, START, StateGraph

from app.graphs.nodes import build_nodes
from app.graphs.state import InterviewState
from app.models.schemas import InterviewAnalysis
from app.services.providers.base import LLMProvider, LLMProviderError


class InterviewWorkflow:
    """Coordinates three LLM specialists and a deterministic formatter."""

    def __init__(self, provider: LLMProvider) -> None:
        graph = StateGraph(InterviewState)
        for name, node in build_nodes(provider).items():
            graph.add_node(name, node)

        graph.add_edge(START, "classification")
        graph.add_edge("classification", "solution_review")
        graph.add_edge("solution_review", "coaching")
        graph.add_edge("coaching", "formatter")
        graph.add_edge("formatter", END)
        self._graph = graph.compile()

    async def analyze(self, question: str) -> InterviewAnalysis:
        """Run all agents and validate the Formatter's final structured response."""

        try:
            result = await self._graph.ainvoke({"question": question})
            return InterviewAnalysis.model_validate(result["final_response"])
        except LLMProviderError:
            raise
        except Exception as exc:
            raise LLMProviderError("The interview workflow could not be completed.") from exc
