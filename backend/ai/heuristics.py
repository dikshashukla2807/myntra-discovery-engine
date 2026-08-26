from __future__ import annotations

from backend.ai.patterns import (
    ABANDON,
    APPEARANCE,
    AVAIL,
    BRAND,
    BROWSE,
    CART_CONSIDER,
    COMPARISON,
    COMPETING,
    CONSIDER,
    DECISION,
    DELIVERY,
    DESIGN,
    EXTERNAL,
    FABRIC,
    FIT,
    INFO,
    INSPIRATION,
    IRRELEVANT_APP_ONLY,
    LOW_INFO_PHRASES,
    NEED,
    OCCASION,
    OVERLOAD,
    POSTPONE,
    PRICE,
    PROMO,
    PURCHASE_INTENT,
    PURCHASED,
    QUALITY,
    RETURNS,
    REVIEWS,
    SAVED_EXPLICIT,
    SHORTLIST,
    SIZE,
    SOCIAL,
    SPAMMY,
    TIMING,
    TREND,
    URGENCY,
    WISHLIST_EXPLICIT,
    contains,
    matched_span,
)
from backend.utils.text import token_count
from config.taxonomies import RELEVANCE_CATEGORIES


def classify_relevance(text: str) -> dict:
    raw = text or ""
    lower = raw.lower()
    categories: list[str] = []
    spans: dict[str, list[str]] = {}

    checks = [
        ("wishlist/save behavior", WISHLIST_EXPLICIT, SAVED_EXPLICIT, SHORTLIST),
        ("purchase postponement", POSTPONE),
        ("purchase abandonment", ABANDON),
        ("purchase completion", PURCHASED),
        ("purchase intent", PURCHASE_INTENT),
        ("fit", FIT),
        ("size", SIZE),
        ("quality", QUALITY),
        ("price", PRICE),
        ("reviews/trust", REVIEWS),
        ("product information", INFO),
        ("comparison", COMPARISON),
        ("social validation", SOCIAL),
        ("occasion", OCCASION),
        ("availability", AVAIL),
        ("returns/exchange", RETURNS),
        ("external research", EXTERNAL),
        ("decision making", DECISION, OVERLOAD),
        ("product consideration", CONSIDER, CART_CONSIDER, BROWSE),
    ]
    for item in checks:
        label = item[0]
        pats = item[1:]
        found: list[str] = []
        for pat in pats:
            found.extend(matched_span(pat, raw))
        if found:
            categories.append(label)
            spans[label] = found[:3]

    # "Myntra" alone is not relevance. App-ops complaints without product-decision
    # language are treated as irrelevant to wishlist→purchase discovery.
    app_only = contains(IRRELEVANT_APP_ONLY, raw) and not categories
    if app_only:
        return {
            "relevant_to_discovery": False,
            "relevance_categories": [],
            "relevance_rationale": "App operations issue without product-decision evidence.",
            "confidence": 0.72,
            "method": "heuristic",
            "spans": {},
        }

    if not categories:
        # Generic product quality/price one-liners still mention a shopping outcome.
        if any(k in lower for k in ("product", "dress", "kurta", "jeans", "shoes", "shirt", "top", "saree", "sari")):
            categories.append("other")
        else:
            return {
                "relevant_to_discovery": False,
                "relevance_categories": [],
                "relevance_rationale": "No evidence of product consideration, purchase decision, or shopping uncertainty.",
                "confidence": 0.6,
                "method": "heuristic",
                "spans": {},
            }

    # Keep only known labels
    categories = [c for c in categories if c in RELEVANCE_CATEGORIES or c == "other"]
    relevant = bool(categories)
    rationale = "Matched behavioral categories from original text: " + ", ".join(categories)
    confidence = min(0.55 + 0.08 * len(categories), 0.9)
    return {
        "relevant_to_discovery": relevant,
        "relevance_categories": categories,
        "relevance_rationale": rationale,
        "confidence": round(confidence, 3),
        "method": "heuristic",
        "spans": spans,
    }


def detect_spam_or_low_value(text: str) -> str | None:
    compact = (text or "").strip()
    if not compact:
        return "empty"
    tokens = token_count(compact)
    if contains(SPAMMY, compact) or contains(PROMO, compact):
        return "promotional" if contains(PROMO, compact) else "spam"
    if tokens < 4:
        return "low_information"
    folded = " ".join(compact.lower().split())
    if folded in LOW_INFO_PHRASES:
        return "low_information"
    # Repeated character / emoji-only handled upstream via is_mostly_symbols
    return None


def extract_behavior(text: str) -> dict:
    raw = text or ""
    evidence: dict[str, list[str]] = {}

    def tag(label: str, pattern) -> bool:
        spans = matched_span(pattern, raw)
        if spans:
            evidence.setdefault(label, []).extend(spans)
            return True
        return False

    intent = "unclear"
    if tag("intent:purchased", PURCHASED):
        intent = "purchased"
    elif tag("intent:abandoned", ABANDON):
        intent = "abandoned"
    elif tag("intent:postponed", POSTPONE):
        intent = "postponed"
    elif tag("intent:return", RETURNS) and tag("intent:post-purchase-signal", PURCHASED):
        intent = "return/exchange"
    elif tag("intent:return", RETURNS):
        intent = "return/exchange"
    elif tag("intent:purchase_intent", PURCHASE_INTENT):
        intent = "purchase intent"
    elif tag("intent:wishlist", WISHLIST_EXPLICIT) or tag("intent:saved", SAVED_EXPLICIT):
        intent = "wishlist/save"
    elif tag("intent:comparison", COMPARISON):
        intent = "comparison"
    elif tag("intent:consideration", CONSIDER):
        intent = "consideration"
    elif tag("intent:inspiration", INSPIRATION):
        intent = "inspiration"
    elif tag("intent:browsing", BROWSE):
        intent = "browsing"
    elif tag("intent:post-purchase", PURCHASED):
        intent = "post-purchase"

    if intent == "purchased" and not tag("post-purchase-extra", RETURNS):
        # Bought + quality/fit talk is still post-purchase evidence of the journey.
        if tag("quality", QUALITY) or tag("fit", FIT):
            intent = "post-purchase"

    wishlist = "no evidence"
    if tag("wishlist", WISHLIST_EXPLICIT):
        wishlist = "explicitly wishlisted"
    elif tag("saved", SAVED_EXPLICIT):
        wishlist = "explicitly saved"
    elif tag("shortlist", SHORTLIST):
        wishlist = "implied shortlist"
    elif tag("cart", CART_CONSIDER):
        wishlist = "carted as consideration"

    reasons: list[str] = []
    reason_map = [
        ("design", DESIGN),
        ("trend", TREND),
        ("brand", BRAND),
        ("price", PRICE),
        ("occasion", OCCASION),
        ("recommendation", SOCIAL),
        ("perceived quality", QUALITY),
        ("need", NEED),
        ("comparison", COMPARISON),
        ("social influence", SOCIAL),
    ]
    for label, pat in reason_map:
        if tag(f"reason:{label}", pat):
            reasons.append(label)
    if tag("reason:future", POSTPONE) and wishlist != "no evidence":
        reasons.append("future purchase")
    if not reasons:
        reasons = ["unclear"]

    outcome = "unknown"
    if tag("outcome:alternative", COMPETING):
        outcome = "purchased alternative"
    elif intent in {"purchased", "post-purchase"}:
        outcome = "purchased"
    elif intent == "abandoned":
        outcome = "abandoned"
    elif intent == "postponed":
        outcome = "postponed"
    elif intent in {"consideration", "wishlist/save", "purchase intent", "comparison"}:
        outcome = "still considering"

    barriers: list[str] = []
    barrier_map = [
        ("price", PRICE),
        ("fit", FIT),
        ("size", SIZE),
        ("quality uncertainty", QUALITY),
        ("material/fabric uncertainty", FABRIC),
        ("appearance uncertainty", APPEARANCE),
        ("reviews/trust", REVIEWS),
        ("return concern", RETURNS),
        ("delivery", DELIVERY),
        ("availability", AVAIL),
        ("product information", INFO),
        ("comparison", COMPARISON),
        ("social validation", SOCIAL),
        ("occasion", OCCASION),
        ("timing", TIMING),
        ("decision overload", OVERLOAD),
        ("lack of urgency", URGENCY),
        ("competing product", COMPETING),
        ("external research", EXTERNAL),
    ]
    for label, pat in barrier_map:
        if tag(f"barrier:{label}", pat):
            barriers.append(label)
    if not barriers:
        barriers = ["unknown"]

    uncertainty_type: list[str] = []
    if "fit" in barriers:
        uncertainty_type.append("fit")
    if "size" in barriers:
        uncertainty_type.append("size")
    if "material/fabric uncertainty" in barriers:
        uncertainty_type.append("fabric/feel")
    if "quality uncertainty" in barriers and "price" in barriers:
        uncertainty_type.append("quality vs price")
    elif "quality uncertainty" in barriers:
        uncertainty_type.append("quality vs price")
    if "appearance uncertainty" in barriers:
        uncertainty_type.append("photo vs reality")
    if "comparison" in barriers or "competing product" in barriers:
        uncertainty_type.append("better alternative")
    if "reviews/trust" in barriers:
        uncertainty_type.append("review trust")
    if "return concern" in barriers:
        uncertainty_type.append("return hassle")
    if "occasion" in barriers:
        uncertainty_type.append("occasion suitability")
    if "availability" in barriers:
        uncertainty_type.append("availability")
    uncertainty_present = bool(uncertainty_type) or contains(DECISION, raw)
    if uncertainty_present and not uncertainty_type:
        uncertainty_type = ["other"]
    uncertainty_description = None
    if uncertainty_present:
        bits = []
        for key in ("fit", "size", "quality", "photo", "review", "return", "fabric"):
            if any(key in u or key in " ".join(barriers) for u in uncertainty_type):
                bits.append(key)
        uncertainty_description = (
            "User language indicates unresolved questions about: " + ", ".join(uncertainty_type)
        )

    workaround_type: list[str] = []
    external_platform: list[str] = []
    lower = raw.lower()
    platform_map = [
        ("Google", r"google"),
        ("YouTube", r"youtube"),
        ("Instagram", r"instagram"),
        ("Reddit", r"reddit"),
        ("checking another ecommerce platform", r"amazon|ajio|meesho|nykaa|flipkart"),
        ("checking brand website", r"brand (site|website)|official (site|website)"),
        ("checking customer photos", r"customer photo|user photo|real photo"),
        ("checking measurements manually", r"measur(e|ed|ing)|size chart"),
        ("comparing alternatives", r"compar"),
        ("visiting an offline store", r"offline|in store|in-store|showroom"),
        ("asking friends/family", r"friend|sister|mom|family"),
        ("waiting", r"wait(ing)? for sale|later"),
        ("adding alternatives to wishlist", r"wishlist"),
    ]
    import re as _re

    for label, pat in platform_map:
        if _re.search(pat, lower):
            workaround_type.append(label)
            if label in {"Google", "YouTube", "Instagram", "Reddit"}:
                external_platform.append(label)
            elif "ecommerce" in label:
                external_platform.append("other ecommerce")
            elif "brand" in label:
                external_platform.append("brand website")
            elif "offline" in label:
                external_platform.append("offline store")
            elif "friends" in label:
                external_platform.append("friends/family")

    workaround_type = list(dict.fromkeys(workaround_type))
    external_platform = list(dict.fromkeys(external_platform))
    workaround_present = bool(workaround_type)
    workaround_description = (
        "Observed workaround language: " + ", ".join(workaround_type) if workaround_present else None
    )

    external_research = bool(external_platform) or contains(EXTERNAL, raw)
    purposes: list[str] = []
    if external_research:
        for label, flag in [
            ("fit", "fit" in barriers or "fit" in uncertainty_type),
            ("size", "size" in barriers or "size" in uncertainty_type),
            ("quality", "quality uncertainty" in barriers),
            ("reviews", "reviews/trust" in barriers),
            ("price", "price" in barriers),
            ("comparison", "comparison" in barriers),
            ("product information", "product information" in barriers),
            ("social proof", "social validation" in barriers),
        ]:
            if flag:
                purposes.append(label)
        if not purposes:
            purposes = ["other"]

    segments: list[str] = []
    if wishlist in {"explicitly wishlisted", "explicitly saved"}:
        segments.append("high-wishlist users")
    if "fit" in barriers or "size" in barriers:
        segments.append("fit-conscious shoppers")
    if "price" in barriers:
        segments.append("price-sensitive shoppers")
    if workaround_present or external_research:
        segments.append("research-heavy shoppers")
    if "comparison" in barriers or intent == "comparison":
        segments.append("comparison-heavy shoppers")
    if "occasion" in barriers or "occasion" in reasons:
        segments.append("occasion-driven shoppers")
    if "brand" in reasons:
        segments.append("brand-loyal shoppers")
    if intent in {"browsing", "inspiration"}:
        segments.append("exploratory browsers")

    # Do not invent demographics. Only emit segments with textual support.
    confidence = 0.5
    if evidence:
        confidence = min(0.5 + 0.05 * len(evidence), 0.88)

    return {
        "user_intent": intent,
        "wishlist_behavior": wishlist,
        "consider_reasons": reasons,
        "purchase_outcome": outcome,
        "barriers": barriers,
        "uncertainty_present": uncertainty_present,
        "uncertainty_type": list(dict.fromkeys(uncertainty_type)),
        "uncertainty_description": uncertainty_description,
        "workaround_present": workaround_present,
        "workaround_type": workaround_type,
        "workaround_description": workaround_description,
        "external_platform": external_platform,
        "external_research": external_research,
        "external_research_platform": external_platform,
        "external_research_purpose": purposes,
        "segment_signals": list(dict.fromkeys(segments)),
        "evidence_spans": {k: v[:2] for k, v in evidence.items()},
        "method": "heuristic",
        "confidence": round(confidence, 3),
    }
