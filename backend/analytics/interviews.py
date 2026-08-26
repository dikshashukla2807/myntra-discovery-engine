from __future__ import annotations

from typing import Any

from backend.ai.llm import complete_json, llm_available


BASE_QUESTIONS = [
    "Tell me about the last fashion product you wanted to buy but didn't.",
    "Walk me through how that product ended up saved, wishlisted, or sitting in your bag.",
    "What made you save it in the first place?",
    "What happened between saving it and deciding whether to buy?",
    "What information were you still looking for?",
    "Where did you go to find that information, if anywhere?",
    "Did you look anywhere outside Myntra? If yes, what were you trying to learn?",
    "If you compared it with something else, how did you compare?",
    "What did you eventually do, and what made that the decision?",
    "Tell me about a time you did buy something you had saved. What was different?",
    "When you hesitate, what usually makes you wait versus drop it altogether?",
    "Who, if anyone, do you involve before you buy clothes online?",
]


def generate_interview_plan(opportunity: dict[str, Any], segment: str | None = None) -> dict[str, Any]:
    questions = list(BASE_QUESTIONS)
    if llm_available():
        payload = complete_json(
            system=(
                "You design behavioral product interviews. Return JSON {questions: string[]}. "
                "8-12 questions. Open-ended. About past behavior. Non-leading. "
                "Do NOT ask if they would use a feature. Do NOT ask if a solution would help. "
                "Investigate root cause, workarounds, postponement, external research, decision-making."
            ),
            user=f"Opportunity: {opportunity.get('title')}\nDescription: {opportunity.get('description')}\nGap: {opportunity.get('research_gap')}\nSegment: {segment or 'unspecified'}",
            cache_key=f"iv:{opportunity.get('opportunity_id')}:{segment}",
        )
        if payload and payload.get("questions"):
            questions = [str(q) for q in payload["questions"] if q][:12]

    # Guardrail: drop leading solution-validation questions if an LLM produced them.
    banned = ("would you use", "would this help", "would you like a feature", "ai feature")
    questions = [q for q in questions if not any(b in q.lower() for b in banned)]
    if len(questions) < 8:
        questions = BASE_QUESTIONS

    return {
        "opportunity_id": opportunity.get("opportunity_id"),
        "selected_opportunity": opportunity.get("title"),
        "target_segment": segment or (opportunity.get("user_segment") or ["unspecified"])[0],
        "research_objective": (
            "Understand what actually happens between expressing interest (save/wishlist) "
            "and buying or not buying, for this opportunity area — without validating a solution."
        ),
        "interview_questions": questions[:12],
        "notes": [
            "Ask for the last real episode, not hypotheticals.",
            "Follow the story: trigger → save → wait → research → decide.",
            "Do not pitch a feature. The engine identifies opportunity areas; interviews validate the problem.",
        ],
        "claim_type": "HYPOTHESIS",
    }
