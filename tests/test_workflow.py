"""End-to-end graph verification with a deterministic provider fake."""

import asyncio

from app.graphs.workflow import InterviewWorkflow
from app.services.providers.base import LLMProvider


class FakeProvider(LLMProvider):
    """Returns one valid result for each of the three LLM calls."""

    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if "Classification specialist" in system_prompt:
            return '{"difficulty":"Medium","primary_pattern":"Sliding Window"}'
        if "Solution Review specialist" in system_prompt:
            return '{"algorithm_idea":"Maintain a moving range and track the values currently inside it. Shrink the range only when its constraint is violated.","time_complexity":"O(n)","space_complexity":"O(n)","better_solution_exists":false,"better_solution_notes":"A single pass is asymptotically optimal."}'
        if "Coaching specialist" in system_prompt:
            return '{"hints":["Consider a contiguous range.","Track what is inside the current range.","Move the left boundary when a duplicate appears."],"follow_up_questions":["How would you handle a stream?","What changes for Unicode input?"]}'
        raise AssertionError("Unexpected specialist prompt")


def test_three_call_workflow_returns_valid_analysis() -> None:
    provider = FakeProvider()
    analysis = asyncio.run(
        InterviewWorkflow(provider).analyze(
            "Find the longest substring without repeating characters."
        )
    )

    assert analysis.difficulty == "Medium"
    assert analysis.primary_pattern == "Sliding Window"
    assert len(analysis.hints) == 3
    assert len(analysis.follow_up_questions) == 2
    assert provider.calls == 3
