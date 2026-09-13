"""API contracts and structured outputs returned by graph agents."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalyzeRequest(BaseModel):
    """A candidate's DSA interview question."""

    question: str = Field(min_length=10, max_length=6000, examples=["Find the longest substring without repeating characters."])

    @field_validator("question")
    @classmethod
    def require_meaningful_question(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Please enter a fuller interview question (at least 10 characters).")
        return cleaned


class ClassificationOutput(BaseModel):
    """Combined result of the difficulty and pattern responsibilities."""

    difficulty: Literal["Easy", "Medium", "Hard"]
    primary_pattern: str = Field(min_length=2, max_length=100)


class SolutionReviewOutput(BaseModel):
    """Combined algorithm-planning and complexity-review result."""

    algorithm_idea: str = Field(min_length=20, max_length=1400)
    # Providers sometimes add a brief justification alongside the Big-O label.
    # Allow it rather than rejecting an otherwise correct coaching response.
    time_complexity: str = Field(min_length=3, max_length=300)
    space_complexity: str = Field(min_length=3, max_length=300)
    better_solution_exists: bool
    better_solution_notes: str = Field(min_length=3, max_length=500)


class CoachingOutput(BaseModel):
    """Combined hint-generation and interviewer-follow-up result."""

    hints: list[str] = Field(min_length=3, max_length=3)
    follow_up_questions: list[str] = Field(min_length=2, max_length=2)

    @field_validator("hints")
    @classmethod
    def require_nonempty_hints(cls, hints: list[str]) -> list[str]:
        if any(not hint.strip() for hint in hints):
            raise ValueError("Hints cannot be empty.")
        return hints


class InterviewAnalysis(BaseModel):
    """Stable JSON object consumed by the browser client."""

    model_config = ConfigDict(extra="forbid")

    difficulty: Literal["Easy", "Medium", "Hard"]
    primary_pattern: str
    algorithm_idea: str
    time_complexity: str
    space_complexity: str
    better_solution_exists: bool
    better_solution_notes: str
    hints: list[str] = Field(min_length=3, max_length=3)
    follow_up_questions: list[str] = Field(min_length=2, max_length=2)


class AnalyzeResponse(BaseModel):
    """Envelope that leaves room for request metadata later."""

    analysis: InterviewAnalysis
