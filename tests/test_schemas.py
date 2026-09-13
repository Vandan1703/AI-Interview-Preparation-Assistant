"""Fast, provider-free checks for the public output contract."""

import pytest
from pydantic import ValidationError

from app.models.schemas import AnalyzeRequest, CoachingOutput, SolutionReviewOutput


def test_question_is_trimmed() -> None:
    assert AnalyzeRequest(question="  Explain two sum please  ").question == "Explain two sum please"


def test_hints_must_have_exactly_three_items() -> None:
    with pytest.raises(ValidationError):
        CoachingOutput(hints=["one", "two"], follow_up_questions=["one", "two"])


def test_complexity_review_allows_a_short_explanation() -> None:
    result = SolutionReviewOutput(
        algorithm_idea="Maintain a valid window and track the character counts while it moves.",
        time_complexity="O(n), because each boundary advances through the input at most once.",
        space_complexity="O(1), for a fixed uppercase alphabet.",
        better_solution_exists=False,
        better_solution_notes="The scan is asymptotically optimal.",
    )
    assert result.time_complexity.startswith("O(n)")
