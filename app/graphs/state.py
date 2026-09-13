"""Shared state passed through the LangGraph coaching workflow."""

from typing import TypedDict


class InterviewState(TypedDict, total=False):
    """Each agent adds only the fields it owns to this shared state."""

    question: str
    difficulty: str
    primary_pattern: str
    algorithm_idea: str
    time_complexity: str
    space_complexity: str
    better_solution_exists: bool
    better_solution_notes: str
    hints: list[str]
    follow_up_questions: list[str]
    final_response: dict[str, object]
