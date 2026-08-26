"""Search queries used for Reddit and YouTube collection.

Queries are intentionally broader than "Myntra wishlist" because the
underlying conversion problem is unknown and must be discovered from evidence.
"""

REDDIT_QUERY_CATEGORIES: list[dict[str, str]] = [
    {"category": "myntra_wishlist", "query": "Myntra wishlist"},
    {"category": "myntra_saved", "query": "Myntra saved items"},
    {"category": "myntra_didnt_buy", "query": 'Myntra "didn\'t buy" OR "did not buy" OR "not buying"'},
    {"category": "myntra_purchase_decision", "query": "Myntra purchase decision"},
    {"category": "myntra_shopping_experience", "query": "Myntra shopping experience"},
    {"category": "myntra_sizing", "query": "Myntra sizing"},
    {"category": "myntra_fit", "query": "Myntra fit"},
    {"category": "myntra_quality", "query": "Myntra quality"},
    {"category": "myntra_returns", "query": "Myntra returns"},
    {"category": "myntra_reviews", "query": "Myntra reviews"},
    {"category": "myntra_comparison", "query": "Myntra comparison OR vs Ajio OR vs Amazon"},
    {"category": "myntra_product_research", "query": "Myntra product research OR before buying"},
    {"category": "myntra_worth_buying", "query": "Myntra worth buying OR worth it"},
    {"category": "online_fashion_wishlist", "query": "online fashion wishlist OR saved for later clothes"},
    {"category": "online_fashion_purchase_decision", "query": "online fashion purchase decision India"},
    {"category": "online_fashion_uncertainty", "query": "online shopping clothes unsure OR hesitant"},
    {"category": "online_fashion_fit", "query": "online shopping clothes fit India"},
    {"category": "online_fashion_quality", "query": "online shopping clothes quality India"},
    {"category": "online_fashion_comparison", "query": "comparing clothes online before buying"},
    {"category": "fashion_shopping_behavior", "query": "fashion shopping behavior online India"},
    {"category": "fashion_purchase_postponement", "query": "keep adding clothes to cart but don't buy"},
    {"category": "fashion_purchase_abandonment", "query": "abandoned cart clothes OR never bought wishlist"},
]

YOUTUBE_SEARCH_TOPICS: list[str] = [
    "Myntra shopping experience",
    "Myntra haul",
    "Myntra review",
    "Myntra fashion shopping",
    "Myntra sizing",
    "Myntra quality",
    "Myntra returns",
    "Myntra product reviews",
    "online fashion shopping India",
    "Myntra wishlist",
    "Myntra purchase experience",
]
