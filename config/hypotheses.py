"""Starting hypotheses for wishlist → 30-day purchase conversion.

These are not established problems. The engine must test them against
public UGC and is allowed to return insufficient, weak, or contradicted.
"""

from __future__ import annotations

HYPOTHESIS_BANK = [
    {
        "hypothesis_id": "H1",
        "hypothesis_name": "Wishlist as Bookmarking",
        "statement": (
            "Some users wishlist products primarily as a bookmarking mechanism "
            "rather than because they have strong purchase intent."
        ),
        "investigate": [
            "save because they like it",
            "save for future reference",
            "explicit purchase intent vs low-intent save",
            "different levels of intent inside wishlist behavior",
        ],
    },
    {
        "hypothesis_id": "H2",
        "hypothesis_name": "Budget / Timing",
        "statement": (
            "Some users want a wishlisted product but postpone purchasing because "
            "they do not want to spend money at that moment or their priorities change."
        ),
        "investigate": [
            "budget constraints",
            "spending priorities",
            "waiting before purchase",
            "changing needs or preferences",
            "purchase postponement",
        ],
        "caution": "A price mention is not automatically a budget constraint.",
    },
    {
        "hypothesis_id": "H3",
        "hypothesis_name": "Future Occasion",
        "statement": (
            "Some users wishlist products for a future occasion such as a festival, "
            "event, vacation, wedding, or other planned use."
        ),
        "investigate": [
            "occasion-based saving",
            "future purchase intent",
            "timing mismatch",
            "seasonal or event-based purchasing",
        ],
    },
    {
        "hypothesis_id": "H4",
        "hypothesis_name": "Cross-Platform Comparison",
        "statement": (
            "Some users wishlist an item on Myntra but later find the same or a "
            "similar item elsewhere and purchase it from another platform."
        ),
        "investigate": [
            "cross-platform comparison",
            "price comparison",
            "product comparison",
            "brand website research",
            "competing ecommerce platforms",
            "purchasing elsewhere",
        ],
        "caution": "Naming another platform is not the same as switching.",
    },
    {
        "hypothesis_id": "H5",
        "hypothesis_name": "Availability / Size / Color",
        "statement": (
            "Some users intend to purchase a wishlisted product later but lose the "
            "opportunity because the product, size, or color becomes unavailable."
        ),
        "investigate": [
            "out of stock",
            "size unavailable",
            "color unavailable",
            "product removed",
            "inventory changes",
            "inability to purchase later",
        ],
    },
    {
        "hypothesis_id": "H6",
        "hypothesis_name": "Product Uncertainty",
        "statement": (
            "Some users hesitate to purchase because they lack sufficient confidence "
            "or information about the product."
        ),
        "investigate": [
            "fit",
            "size",
            "quality",
            "material/fabric",
            "appearance",
            "reviews",
            "customer photos",
            "authenticity/trust",
            "styling",
            "returns",
            "product information",
            "comparison",
        ],
        "caution": "Name the specific uncertainty; do not dump everything into one bucket.",
    },
]

HYPOTHESIS_IDS = tuple(h["hypothesis_id"] for h in HYPOTHESIS_BANK)

STATUS_SUPPORTED = "supported"
STATUS_WEAKLY = "weakly_supported"
STATUS_CONTRADICTED = "contradicted"
STATUS_INSUFFICIENT = "insufficient_evidence"

STANCE_SUPPORTING = "supporting"
STANCE_COUNTER = "counter"
STANCE_NEUTRAL = "neutral"
STANCE_UNCLEAR = "unclear"

PURCHASE_RELATED_OUTCOMES = ("postponed", "abandoned", "purchased alternative")
