from __future__ import annotations

from typing import Any


GAP_QUESTIONS = [
    "Does this actually cause users to postpone purchase after wishlisting, or is it only mentioned in the same comments?",
    "Is this concentrated in a specific behavioral segment, category (apparel vs footwear), or price band?",
    "Does this occur before saving, at the moment of saving, or in the days after saving?",
    "How severe is it relative to other open questions the user still has?",
    "What workaround do users currently prefer, and does it actually resolve the uncertainty?",
    "Would resolving this change purchase intent within 30 days, or would another barrier remain?",
]


def build_gaps(opportunities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps = []
    for opp in opportunities:
        gaps.append(
            {
                "opportunity_id": opp["opportunity_id"],
                "opportunity_title": opp["title"],
                "research_gap": opp.get("research_gap"),
                "unknowns": GAP_QUESTIONS,
                "claim_type": "HYPOTHESIS",
                "why_primary_research": (
                    "Public UGC can show that a theme exists. It cannot show whether the theme "
                    "causes 30-day wishlist conversion failure for Myntra users in the target metric."
                ),
                "suggested_interview_count": 5,
            }
        )
    return gaps
