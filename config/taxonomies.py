"""Closed vocabularies for classification and extraction.

These are labels the engine may assign. They are not assumed problems.
An observation is only tagged when evidence in the original text supports it.
"""

SOURCES = ("google_play", "app_store", "reddit", "youtube")

DATASET_LABELS = ("public_source", "demo_sample")

RELEVANCE_CATEGORIES = (
    "product consideration",
    "wishlist/save behavior",
    "purchase intent",
    "purchase postponement",
    "purchase abandonment",
    "purchase completion",
    "fit",
    "size",
    "quality",
    "price",
    "reviews/trust",
    "product information",
    "comparison",
    "social validation",
    "occasion",
    "availability",
    "returns/exchange",
    "external research",
    "decision making",
    "other",
)

USER_INTENTS = (
    "browsing",
    "inspiration",
    "consideration",
    "wishlist/save",
    "comparison",
    "purchase intent",
    "purchased",
    "postponed",
    "abandoned",
    "return/exchange",
    "post-purchase",
    "unclear",
)

WISHLIST_BEHAVIORS = (
    "explicitly wishlisted",
    "explicitly saved",
    "implied shortlist",
    "carted as consideration",
    "no evidence",
    "unclear",
)

CONSIDER_REASONS = (
    "design",
    "trend",
    "brand",
    "price",
    "occasion",
    "recommendation",
    "perceived quality",
    "need",
    "future purchase",
    "comparison",
    "social influence",
    "other",
    "unclear",
)

PURCHASE_OUTCOMES = (
    "purchased",
    "postponed",
    "abandoned",
    "purchased alternative",
    "still considering",
    "unknown",
)

BARRIERS = (
    "price",
    "fit",
    "size",
    "quality uncertainty",
    "material/fabric uncertainty",
    "appearance uncertainty",
    "reviews/trust",
    "return concern",
    "delivery",
    "availability",
    "product information",
    "comparison",
    "social validation",
    "occasion",
    "timing",
    "decision overload",
    "changed preference",
    "lack of urgency",
    "competing product",
    "external research",
    "other",
    "unknown",
)

UNCERTAINTY_TYPES = (
    "fit",
    "size",
    "fabric/feel",
    "quality vs price",
    "photo vs reality",
    "better alternative",
    "regret",
    "review trust",
    "return hassle",
    "occasion suitability",
    "availability",
    "other",
)

WORKAROUNDS = (
    "Google",
    "YouTube",
    "Instagram",
    "Reddit",
    "asking friends/family",
    "checking another ecommerce platform",
    "checking brand website",
    "checking customer photos",
    "checking measurements manually",
    "comparing alternatives",
    "visiting an offline store",
    "waiting",
    "checking later",
    "adding alternatives to wishlist",
    "doing nothing",
)

EXTERNAL_PLATFORMS = (
    "Google",
    "YouTube",
    "Instagram",
    "Reddit",
    "other ecommerce",
    "brand website",
    "offline store",
    "friends/family",
    "other",
)

EXTERNAL_PURPOSES = (
    "fit",
    "size",
    "quality",
    "styling",
    "reviews",
    "price",
    "comparison",
    "authenticity",
    "product information",
    "social proof",
    "other",
)

CLAIM_TYPES = ("FACT", "PATTERN", "HYPOTHESIS", "OPPORTUNITY")

EXCLUSION_REASONS = (
    "empty",
    "duplicate",
    "spam",
    "bot",
    "promotional",
    "irrelevant",
    "low_information",
)

NON_PURCHASE_OUTCOMES = {
    "postponed",
    "abandoned",
    "purchased alternative",
}

# Six comparison scores, each 1–5. Weights must sum to 1.
OPPORTUNITY_WEIGHTS = {
    "evidence_strength": 0.20,
    "frequency": 0.15,
    "purchase_association": 0.25,
    "user_severity": 0.15,
    "workaround_intensity": 0.15,
    "segment_relevance": 0.10,
}
