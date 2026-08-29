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
        "target_segment": (
            segment
            or (
                (opportunity.get("user_segment") or ["Insufficient evidence."])[0]
            )
        ),
        "what_we_know": opportunity.get("what_we_know")
        or opportunity.get("description")
        or "Insufficient evidence.",
        "what_we_dont_know": opportunity.get("research_gap")
        or "Whether this pattern actually prevents 30-day wishlist conversion.",
        "research_hypothesis": (
            "If this barrier is a true decision blocker for high-intent / high-wishlist users, "
            "we should hear it unprompted in stories of products they wanted but did not buy. "
            "This remains a hypothesis until interviews."
        ),
        "research_objective": (
            "Understand what actually happens between expressing interest (save/wishlist) "
            "and buying or not buying, for this opportunity area — without validating a solution."
        ),
        "interview_questions": questions[:12],
        "research_objectives": [
            "What actually happened between saving/wishlisting and deciding not to buy?",
            "Was this barrier the main reason, or one of several?",
            "Who else was involved, and what information was still missing?",
            "When in the 30 days after saving did the decision stall?",
        ][:4],
        "ready_for_primary_research": True,
        "end_state": "READY FOR PRIMARY RESEARCH",
        "why_primary_research": (
            "Public UGC can show that a pattern exists and whether it is observed alongside "
            "postponement or non-purchase. It cannot prove the final user problem, severity, "
            "or whether fixing it would change 30-day wishlist conversion. That takes 5–6 interviews."
        ),
        "notes": [
            "Ask for the last real episode, not hypotheticals.",
            "Follow the story: trigger → save → wait → research → decide.",
            "Do not pitch a feature. The engine stops at opportunity + evidence + research gap.",
            "End state: ready for primary research — not a final solution.",
        ],
    }
