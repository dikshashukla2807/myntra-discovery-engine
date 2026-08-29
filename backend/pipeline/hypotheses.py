"""Test starting hypotheses against extracted public observations.

Counts and status are calculated in code. The LLM is not allowed to invent them.
A price mention is not automatically H2. Naming Amazon is not automatically H4.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from config.hypotheses import (
    HYPOTHESIS_BANK,
    HYPOTHESIS_IDS,
    PURCHASE_RELATED_OUTCOMES,
    STATUS_CONTRADICTED,
    STATUS_INSUFFICIENT,
    STATUS_SUPPORTED,
    STATUS_WEAKLY,
    STANCE_COUNTER,
    STANCE_NEUTRAL,
    STANCE_SUPPORTING,
    STANCE_UNCLEAR,
)

_BANK = {h["hypothesis_id"]: h for h in HYPOTHESIS_BANK}

WISHLIST_SAVE = {
    "explicitly wishlisted",
    "explicitly saved",
    "implied shortlist",
    "carted as consideration",
}

H6_KINDS = (
    ("fit", ("fit",)),
    ("size", ("size",)),
    ("quality", ("quality uncertainty",)),
    ("material/fabric", ("material/fabric uncertainty",)),
    ("appearance", ("appearance uncertainty",)),
    ("reviews", ("reviews/trust",)),
    ("returns", ("return concern",)),
    ("product information", ("product information",)),
    ("comparison", ("comparison",)),
)


def _rx(*parts: str) -> re.Pattern[str]:
    return re.compile("|".join(parts), re.I)


# Behavioral phrases — more than a single keyword.
H1_SUPPORT = _rx(
    r"\bsave(d|ing)? for later\b",
    r"\bjust liked\b",
    r"\bjust love(d)? (the )?(look|design|it)\b",
    r"\bbookmark",
    r"\bkeep(ing)? it (in|on) (my )?(wish ?list|saved)\b",
    r"\bmight buy (it )?later\b",
    r"\bnot sure (if|whether) i('ll| will) buy\b",
    r"\bno plan(s)? to buy\b",
    r"\bfor reference\b",
    r"\blike(d)? it so (i )?save",
)
H1_INTENT = _rx(
    r"\bgoing to buy\b",
    r"\bwill (buy|order)\b",
    r"\bplanning to (buy|order)\b",
    r"\bneed(ed)? this\b",
    r"\bbuying (it )?now\b",
)

H2_BUDGET = _rx(
    r"\bnot ready to spend\b",
    r"\bwasn'?t ready to spend\b",
    r"\bdon'?t want to spend\b",
    r"\bdidn'?t want to spend\b",
    r"\bcan'?t afford\b",
    r"\bcannot afford\b",
    r"\bover budget\b",
    r"\bout of budget\b",
    r"\bthis month'?s budget\b",
    r"\bwaiting for (my )?(salary|payday|paycheck)\b",
    r"\buntil payday\b",
    r"\bother (expenses|priorities|bills)\b",
    r"\bpriorities changed\b",
    r"\bsaving (up|money) (first|for)\b",
    r"\bholding off\b",
    r"\bwait until i have (the )?money\b",
    r"\bnot spending (that|this) (much )?right now\b",
)
H2_POSTPONE = _rx(
    r"\blater\b",
    r"\bwait(ing)?\b",
    r"\bnot now\b",
    r"\bpostpon",
    r"\bdidn'?t buy\b",
    r"\bdid not buy\b",
    r"\bholding off\b",
)
H2_COUNTER = _rx(
    r"\bbought it anyway\b",
    r"\bworth the price\b",
    r"\bstill (bought|ordered|purchased)\b",
    r"\bordered despite\b",
    r"\bpaid (full|anyway)\b",
    r"\bgood value so i (bought|ordered)\b",
)
H2_PRICE_ONLY = _rx(r"\bprice\b", r"\bexpensive\b", r"\bcostly\b", r"\boverpriced\b", r"\bmrp\b")

H3_OCCASION = _rx(
    r"\bwedding\b",
    r"\bfestival\b",
    r"\bdiwali\b",
    r"\bnavratri\b",
    r"\beid\b",
    r"\bvaction\b",
    r"\bvacation\b",
    r"\btrip\b",
    r"\bholiday\b",
    r"\bparty\b",
    r"\bevent\b",
    r"\boccasion\b",
    r"\breception\b",
    r"\bsangeet\b",
)
H3_FUTURE = _rx(
    r"\bupcoming\b",
    r"\bnext (month|week|year)\b",
    r"\bfor (my |the )?(wedding|festival|trip|vacation|party|event|occasion)\b",
    r"\blater\b",
    r"\bsave(d|ing)? for\b",
    r"\bwhen (the|my) .*(comes|happens)\b",
)
H3_NOW = _rx(
    r"\bneeded it (today|tonight|this week)\b",
    r"\bwore it (to|for)\b",
    r"\bbought (it )?for (the |my )?(wedding|party|event) (yesterday|today|last)\b",
)

H4_SWITCH = _rx(
    r"\bbought (it )?(from|on) (amazon|ajio|meesho|nykaa|flipkart|brand (site|website))\b",
    r"\bordered (from|on) (amazon|ajio|meesho|nykaa|flipkart)\b",
    r"\bpurchased (from|on) (amazon|ajio|meesho|nykaa|flipkart)\b",
    r"\bcheaper on (amazon|ajio|meesho|nykaa|flipkart)\b",
    r"\bbetter on (amazon|ajio|meesho|nykaa|flipkart)\b",
    r"\bcompared (prices?|it|them) (with|on|to)\b",
    r"\bchecked (on|with) (amazon|ajio|meesho|nykaa) then (bought|ordered)\b",
    r"\bbought elsewhere\b",
    r"\bordered from another (app|site|platform)\b",
)
H4_PLATFORM_ONLY = _rx(r"\bamazon\b", r"\bajio\b", r"\bmeesho\b", r"\bnykaa\b", r"\bflipkart\b")
H4_COUNTER = _rx(
    r"\bbought (it )?(on|from) myntra\b",
    r"\bmyntra (was|is) cheaper\b",
    r"\bstayed (on|with) myntra\b",
    r"\bordered (here|from myntra) after compar",
)

H5_BLOCK = _rx(
    r"\bout of stock\b",
    r"\bsold out\b",
    r"\bnot available\b",
    r"\bunavailable\b",
    r"\bsize (was |is )?(not available|unavailable|gone|sold out)\b",
    r"\b(colour|color) (was |is )?(not available|unavailable|gone|sold out)\b",
    r"\bwanted to (buy|order) later but .{0,40}(gone|unavailable|sold out|out of stock)\b",
    r"\bwhen i (came|went) back .{0,40}(sold out|out of stock|unavailable)\b",
    r"\bremoved (the )?(product|listing)\b",
)
H5_COUNTER = _rx(
    r"\bfound my size\b",
    r"\bback in stock\b",
    r"\brestocked\b",
    r"\bavailable when i (bought|ordered)\b",
)

H6_HESITATE = _rx(
    r"\bnot sure\b",
    r"\bunsure\b",
    r"\bhesitat",
    r"\bcan'?t tell\b",
    r"\bdon'?t know (if|whether|how)\b",
    r"\bbefore (i |I )?(buy|buying|order)\b",
    r"\bsize chart\b",
    r"\breal (life|photo)\b",
)
H6_COUNTER = _rx(
    r"\btrue to size\b",
    r"\bas shown\b",
    r"\breviews were enough\b",
    r"\breviews helped (me )?decide\b",
    r"\bfit was (fine|perfect|accurate)\b",
    r"\bas described\b",
    r"\bas expected\b",
)


def _text(obs: dict[str, Any]) -> str:
    return (obs.get("text_clean") or obs.get("text_original") or "")


def _has(pattern: re.Pattern[str], text: str) -> bool:
    return bool(pattern.search(text or ""))


def _purchase_related(outcome: str | None) -> bool:
    return outcome in PURCHASE_RELATED_OUTCOMES


def classify_observation(obs: dict[str, Any], ext: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return stance per hypothesis. Neutral if the comment does not address it."""
    ext = ext or {}
    text = _text(obs)
    outcome = ext.get("purchase_outcome") or "unknown"
    intent = ext.get("user_intent") or "unclear"
    wishlist = ext.get("wishlist_behavior") or "no evidence"
    barriers = [b for b in (ext.get("barriers") or []) if b not in {"unknown", "other"}]
    uncs = ext.get("uncertainty_type") or []
    reasons = ext.get("consider_reasons") or []
    work = ext.get("workaround_type") or []
    post_purchase = intent in {"purchased", "post-purchase", "return/exchange"}

    stances: dict[str, dict[str, Any]] = {
        "H1": _h1(text, wishlist, intent, outcome, reasons),
        "H2": _h2(text, outcome, intent, barriers),
        "H3": _h3(text, outcome, reasons, barriers),
        "H4": _h4(text, outcome, barriers, work, ext.get("external_research")),
        "H5": _h5(text, outcome, barriers, uncs),
        "H6": _h6(text, outcome, intent, barriers, uncs, work, post_purchase),
    }
    return {"observation_id": obs.get("observation_id"), "stances": stances}


def _h1(text, wishlist, intent, outcome, reasons) -> dict[str, Any]:
    saved = wishlist in WISHLIST_SAVE or _has(
        _rx(r"\bwishlist", r"\bsaved for later\b", r"\bshortlist"), text
    )
    if not saved:
        return {"stance": STANCE_NEUTRAL, "rationale": "No wishlist/save behavior in this comment."}
    if _has(H1_INTENT, text) or outcome == "purchased" or intent == "purchase intent":
        return {
            "stance": STANCE_COUNTER,
            "rationale": "Save/wishlist language appears with purchase intent or a completed purchase.",
        }
    if _has(H1_SUPPORT, text) or "future purchase" in reasons:
        return {
            "stance": STANCE_SUPPORTING,
            "rationale": "Save/wishlist looks like later-reference or low-intent bookmarking, not a stated buy plan.",
        }
    return {
        "stance": STANCE_UNCLEAR,
        "rationale": "Wishlist/save is present, but the comment does not show bookmarking vs purchase intent clearly.",
    }


def _h2(text, outcome, intent, barriers) -> dict[str, Any]:
    budget = _has(H2_BUDGET, text)
    postpone_lang = _has(H2_POSTPONE, text) or outcome in {"postponed", "abandoned"}
    if _has(H2_COUNTER, text) or (outcome == "purchased" and _has(H2_PRICE_ONLY, text) and not budget):
        if outcome == "purchased" or _has(H2_COUNTER, text):
            return {
                "stance": STANCE_COUNTER,
                "rationale": "Spend/price comes up, but the user still purchased or called it worth buying.",
            }
    if budget and postpone_lang:
        return {
            "stance": STANCE_SUPPORTING,
            "rationale": "Budget, payday, or spending-priority language appears alongside waiting or not buying.",
        }
    if budget and outcome in {"still considering", "unknown"}:
        return {
            "stance": STANCE_UNCLEAR,
            "rationale": "Budget language is present, but the purchase outcome is not clearly postponed.",
        }
    if _has(H2_PRICE_ONLY, text) or "price" in barriers:
        return {
            "stance": STANCE_NEUTRAL,
            "rationale": "Price is mentioned without evidence of a budget/timing constraint on purchase.",
        }
    return {"stance": STANCE_NEUTRAL, "rationale": "Does not address budget or spending timing."}


def _h3(text, outcome, reasons, barriers) -> dict[str, Any]:
    occasion = _has(H3_OCCASION, text) or "occasion" in barriers or "occasion" in reasons
    if not occasion:
        return {"stance": STANCE_NEUTRAL, "rationale": "No occasion or event timing in this comment."}
    if _has(H3_NOW, text) and outcome == "purchased":
        return {
            "stance": STANCE_COUNTER,
            "rationale": "Occasion is mentioned, but the user bought for a current/near need.",
        }
    if occasion and (_has(H3_FUTURE, text) or "future purchase" in reasons or "timing" in barriers or "occasion" in barriers):
        if _has(H3_FUTURE, text) or "future purchase" in reasons or outcome == "postponed":
            return {
                "stance": STANCE_SUPPORTING,
                "rationale": "Occasion/event language appears with later/future purchase timing.",
            }
    return {
        "stance": STANCE_UNCLEAR,
        "rationale": "An occasion is named, but it is not clear whether need-timing explains non-purchase.",
    }


def _h4(text, outcome, barriers, work, external) -> dict[str, Any]:
    switched = _has(H4_SWITCH, text) or outcome == "purchased alternative"
    named = _has(H4_PLATFORM_ONLY, text) or "comparison" in barriers or "competing product" in barriers
    if _has(H4_COUNTER, text):
        return {
            "stance": STANCE_COUNTER,
            "rationale": "Comparison happened, but the comment says the purchase stayed on Myntra.",
        }
    if switched:
        return {
            "stance": STANCE_SUPPORTING,
            "rationale": "Comment describes comparing or buying the same/similar item on another platform.",
        }
    if named or external:
        return {
            "stance": STANCE_UNCLEAR,
            "rationale": "Another platform is named, but there is no clear comparison or purchase-elsewhere behavior.",
        }
    return {"stance": STANCE_NEUTRAL, "rationale": "Does not address cross-platform comparison."}


def _h5(text, outcome, barriers, uncs) -> dict[str, Any]:
    blocked = _has(H5_BLOCK, text) or "availability" in barriers or "availability" in uncs
    if _has(H5_COUNTER, text):
        return {
            "stance": STANCE_COUNTER,
            "rationale": "Availability/size/color was resolved or the item was in stock when they bought.",
        }
    if blocked:
        return {
            "stance": STANCE_SUPPORTING,
            "rationale": "Out of stock, size/color unavailable, or lost chance to buy later is described.",
        }
    return {"stance": STANCE_NEUTRAL, "rationale": "Does not address availability, size, or color stock."}


def _h6(text, outcome, intent, barriers, uncs, work, post_purchase) -> dict[str, Any]:
    kinds = _uncertainty_kinds(barriers, uncs)
    hesitate = (
        _has(H6_HESITATE, text)
        or outcome in {"postponed", "still considering", "abandoned"}
        or bool(work)
    )
    if post_purchase and outcome == "purchased" and not _has(H6_HESITATE, text):
        if kinds:
            return {
                "stance": STANCE_NEUTRAL,
                "rationale": "Uncertainty words appear in a post-purchase complaint, not as pre-purchase hesitation.",
                "uncertainty_kinds": kinds,
            }
        return {"stance": STANCE_NEUTRAL, "rationale": "Post-purchase comment; not pre-purchase uncertainty."}
    if _has(H6_COUNTER, text) and outcome == "purchased":
        return {
            "stance": STANCE_COUNTER,
            "rationale": "User indicates listing/reviews/fit information was enough to buy.",
            "uncertainty_kinds": kinds,
        }
    if kinds and hesitate:
        return {
            "stance": STANCE_SUPPORTING,
            "rationale": "Pre-purchase uncertainty is named (" + ", ".join(kinds) + ") alongside hesitation or information-seeking.",
            "uncertainty_kinds": kinds,
        }
    if kinds and not hesitate:
        return {
            "stance": STANCE_UNCLEAR,
            "rationale": "A product attribute is mentioned, but hesitation before purchase is not clear.",
            "uncertainty_kinds": kinds,
        }
    return {"stance": STANCE_NEUTRAL, "rationale": "Does not address pre-purchase product uncertainty."}


def _uncertainty_kinds(barriers: list[str], uncs: list[str]) -> list[str]:
    found: list[str] = []
    for label, barrier_names in H6_KINDS:
        if any(b in barriers for b in barrier_names) or label in uncs or any(u in barrier_names or u == label for u in uncs):
            if label not in found:
                found.append(label)
    extra_map = {
        "fabric/feel": "material/fabric",
        "quality vs price": "quality",
        "photo vs reality": "appearance",
        "review trust": "reviews",
        "return hassle": "returns",
    }
    for u in uncs:
        mapped = extra_map.get(u)
        if mapped and mapped not in found:
            found.append(mapped)
    return found


def test_hypotheses(
    relevant: list[dict[str, Any]],
    extractions: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    """Classify every relevant observation, then aggregate counts in code."""
    rows: list[dict[str, Any]] = []
    buckets: dict[str, dict[str, list[str]]] = {
        hid: {"supporting": [], "counter": [], "unclear": [], "neutral": []} for hid in HYPOTHESIS_IDS
    }
    purchase_support: dict[str, int] = {hid: 0 for hid in HYPOTHESIS_IDS}
    purchase_counter: dict[str, int] = {hid: 0 for hid in HYPOTHESIS_IDS}
    sources_support: dict[str, Counter[str]] = {hid: Counter() for hid in HYPOTHESIS_IDS}
    segments_support: dict[str, Counter[str]] = {hid: Counter() for hid in HYPOTHESIS_IDS}
    work_support: dict[str, Counter[str]] = {hid: Counter() for hid in HYPOTHESIS_IDS}
    kinds_support: dict[str, Counter[str]] = {hid: Counter() for hid in HYPOTHESIS_IDS}
    outcome_support: dict[str, Counter[str]] = {hid: Counter() for hid in HYPOTHESIS_IDS}

    for obs in relevant:
        oid = obs["observation_id"]
        ext = extractions.get(oid) or {}
        classified = classify_observation(obs, ext)
        rows.append(classified)
        outcome = ext.get("purchase_outcome") or "unknown"
        for hid, payload in classified["stances"].items():
            stance = payload["stance"]
            buckets[hid][stance].append(oid)
            if stance == STANCE_SUPPORTING:
                if _purchase_related(outcome):
                    purchase_support[hid] += 1
                sources_support[hid][obs.get("source") or "unknown"] += 1
                for s in ext.get("segment_signals") or []:
                    segments_support[hid][s] += 1
                for w in ext.get("workaround_type") or []:
                    work_support[hid][w] += 1
                for k in payload.get("uncertainty_kinds") or []:
                    kinds_support[hid][k] += 1
                outcome_support[hid][outcome] += 1
            elif stance == STANCE_COUNTER and _purchase_related(outcome):
                purchase_counter[hid] += 1

    n_relevant = max(len(relevant), 1)
    results: list[dict[str, Any]] = []
    for spec in HYPOTHESIS_BANK:
        hid = spec["hypothesis_id"]
        support_ids = buckets[hid]["supporting"]
        counter_ids = buckets[hid]["counter"]
        unclear_ids = buckets[hid]["unclear"]
        support_n = len(support_ids)
        counter_n = len(counter_ids)
        relevant_n = support_n + counter_n + len(unclear_ids)
        support_pct = round(100.0 * support_n / n_relevant, 2)
        counter_pct = round(100.0 * counter_n / n_relevant, 2)
        purchase_assoc = round(100.0 * purchase_support[hid] / support_n, 2) if support_n else 0.0
        status = _status(support_n, counter_n, n_relevant, purchase_assoc)
        evidence_label = _evidence_label(status, support_n, purchase_assoc)
        confidence = _confidence(support_n + counter_n, len(sources_support[hid]), n_relevant)
        candidate = _is_candidate(status, support_n, purchase_support[hid], purchase_assoc, n_relevant)
        segs = [s for s, c in segments_support[hid].most_common(5) if c >= 3]
        works = [w for w, _ in work_support[hid].most_common(5)]
        results.append(
            {
                "hypothesis_id": hid,
                "hypothesis_name": spec["hypothesis_name"],
                "statement": spec["statement"],
                "status": status,
                "evidence_label": evidence_label,
                "supporting_observations": support_ids[:80],
                "counter_observations": counter_ids[:40],
                "support_count": support_n,
                "counter_count": counter_n,
                "unclear_count": len(unclear_ids),
                "relevant_observation_count": relevant_n,
                "support_percentage": support_pct,
                "counter_percentage": counter_pct,
                "purchase_related_support": purchase_support[hid],
                "purchase_related_counter": purchase_counter[hid],
                "purchase_association": purchase_assoc,
                "support_outcomes": dict(outcome_support[hid]),
                "source_distribution": dict(sources_support[hid]),
                "affected_segments": segs or ["Insufficient evidence."],
                "common_workarounds": works,
                "uncertainty_kinds": [k for k, _ in kinds_support[hid].most_common(8)],
                "confidence": confidence,
                "candidate_opportunity": candidate,
                "reasoning": _reasoning(spec, status, support_n, counter_n, purchase_assoc, purchase_support[hid], n_relevant),
                "research_gap": _research_gap(spec, status),
                "priority": 0,
            }
        )

    results.sort(
        key=lambda r: (
            0 if r["candidate_opportunity"] else 1,
            -(r["purchase_association"] or 0),
            -(r["purchase_related_support"] or 0),
            -(r["support_count"] or 0),
        )
    )
    for i, row in enumerate(results, start=1):
        row["priority"] = i

    unexplained = 0
    for row in rows:
        stances = row["stances"]
        if not any(stances[h]["stance"] == STANCE_SUPPORTING for h in HYPOTHESIS_IDS):
            unexplained += 1
    return rows, results, unexplained


def _min_n(n_relevant: int) -> int:
    return 3 if n_relevant < 80 else 8


def _status(support: int, counter: int, n_relevant: int, purchase_assoc: float) -> str:
    floor = _min_n(n_relevant)
    classified = support + counter
    if classified < floor:
        return STATUS_INSUFFICIENT
    if counter > support and counter >= floor:
        return STATUS_CONTRADICTED
    if support >= floor * 2 and purchase_assoc >= 12:
        return STATUS_SUPPORTED
    if support >= floor:
        return STATUS_WEAKLY
    return STATUS_INSUFFICIENT


def _evidence_label(status: str, support: int, purchase_assoc: float) -> str:
    if status == STATUS_INSUFFICIENT:
        return "Insufficient"
    if status == STATUS_CONTRADICTED:
        return "Counter-weighted"
    if support >= 40 and purchase_assoc >= 25:
        return "Strong"
    if support >= 15:
        return "Moderate"
    return "Weak"


def _confidence(classified: int, n_sources: int, n_relevant: int) -> str:
    if classified >= (25 if n_relevant >= 80 else 6) and n_sources >= 2:
        return "high"
    if classified >= (12 if n_relevant >= 80 else 3):
        return "medium"
    return "low"


def _is_candidate(status: str, support: int, purchase_support: int, purchase_assoc: float, n_relevant: int) -> bool:
    floor = _min_n(n_relevant)
    if status not in {STATUS_SUPPORTED, STATUS_WEAKLY}:
        return False
    if support < floor:
        return False
    if purchase_support < floor:
        return False
    if purchase_assoc < 12:
        return False
    return True


def _reasoning(
    spec: dict[str, Any],
    status: str,
    support: int,
    counter: int,
    purchase_assoc: float,
    purchase_support: int,
    n_relevant: int,
) -> str:
    hid = spec["hypothesis_id"]
    name = spec["hypothesis_name"]
    if status == STATUS_INSUFFICIENT:
        extra = ""
        if hid == "H1":
            extra = " Explicit wishlist/save language is rare in app reviews; that is a coverage gap, not proof that bookmarking is absent."
        if hid == "H2":
            extra = " Price can appear often without meeting the budget/timing test used here."
        return (
            f"{name} was tested on {n_relevant} relevant observations. "
            f"{support} supported it and {counter} contradicted it — not enough classified evidence to judge.{extra}"
        )
    if status == STATUS_CONTRADICTED:
        return (
            f"Counter-evidence ({counter}) outweighs supporting comments ({support}) for {name}. "
            "Treat the starting hypothesis as challenged, not confirmed."
        )
    if hid == "H2" and status != STATUS_SUPPORTED:
        return (
            f"Price may be discussed in the corpus, but only {support} observations connect budget/timing "
            f"to waiting or not buying ({purchase_support} of those are purchase-related; "
            f"purchase association {purchase_assoc}%). {name} should not currently be prioritized."
        )
    return (
        f"{support} observations support {name} and {counter} go against it "
        f"({support} is {round(100.0 * support / max(n_relevant, 1), 1)}% of relevant comments). "
        f"{purchase_support} supporting comments are observed alongside postponement, abandonment, "
        f"or alternative purchase (association {purchase_assoc}%). That is co-occurrence, not causation."
    )


def _research_gap(spec: dict[str, Any], status: str) -> str:
    name = spec["hypothesis_name"]
    if status == STATUS_INSUFFICIENT:
        return (
            f"Public UGC does not contain enough behavioral evidence to accept or reject {name}. "
            "Interviews are required if this remains a suspected conversion path."
        )
    return (
        f"Public comments cannot tell us whether {name} is the primary reason a wishlisted item "
        "fails to convert within 30 days, who it hits hardest, or whether it happens before or after saving."
    )


def attach_origin(
    themes: list[dict[str, Any]],
    hypothesis_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Tag theme opportunities as initial-hypothesis or emerging."""
    support_sets = {
        r["hypothesis_id"]: set(r.get("supporting_observations") or []) for r in hypothesis_results
    }
    names = {r["hypothesis_id"]: r["hypothesis_name"] for r in hypothesis_results}
    cand = {r["hypothesis_id"]: r.get("candidate_opportunity") for r in hypothesis_results}
    for theme in themes:
        ids = set(theme.get("supporting_evidence_ids") or [])
        best_h, best_n = None, 0
        for hid, sset in support_sets.items():
            ov = len(ids & sset)
            if ov > best_n:
                best_h, best_n = hid, ov
        share = best_n / max(len(ids), 1)
        if best_h and share >= 0.35 and best_n >= 3:
            theme["source_hypothesis"] = best_h
            theme["source_hypothesis_name"] = names[best_h]
            theme["origin"] = "initial_hypothesis"
            theme["candidate_opportunity"] = bool(cand.get(best_h))
        else:
            theme["source_hypothesis"] = None
            theme["source_hypothesis_name"] = None
            theme["origin"] = "emerging"
            theme["candidate_opportunity"] = True
    return themes


def extra_hypothesis_themes(
    themes: list[dict[str, Any]],
    hypothesis_results: list[dict[str, Any]],
    relevant: list[dict[str, Any]],
    extractions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """If a candidate hypothesis has no matching theme, add one opportunity from its evidence."""
    covered = {t.get("source_hypothesis") for t in themes if t.get("source_hypothesis")}
    by_id = {o["observation_id"]: o for o in relevant}
    extra: list[dict[str, Any]] = []
    for row in hypothesis_results:
        if not row.get("candidate_opportunity"):
            continue
        if row["hypothesis_id"] in covered:
            continue
        members = [by_id[i] for i in row.get("supporting_observations") or [] if i in by_id]
        if len(members) < 3:
            continue
        outcomes: Counter[str] = Counter()
        barriers: Counter[str] = Counter()
        uncs: Counter[str] = Counter()
        works: Counter[str] = Counter()
        sources: list[str] = []
        for obs in members:
            ext = extractions.get(obs["observation_id"]) or {}
            outcomes[ext.get("purchase_outcome") or "unknown"] += 1
            for b in ext.get("barriers") or []:
                if b not in {"unknown", "other"}:
                    barriers[b] += 1
            for u in ext.get("uncertainty_type") or []:
                uncs[u] += 1
            for w in ext.get("workaround_type") or []:
                works[w] += 1
            sources.append(obs.get("source"))
        hid = row["hypothesis_id"]
        extra.append(
            {
                "theme_id": f"theme-{hid.lower()}",
                "theme_name": row["statement"],
                "description": row["reasoning"],
                "frequency": row["support_count"],
                "frequency_percentage": row["support_percentage"],
                "source_count": len({s for s in sources if s}),
                "source_diversity": sorted({s for s in sources if s}),
                "segments": [s for s in row.get("affected_segments") or [] if s != "Insufficient evidence."],
                "purchase_outcomes": dict(outcomes),
                "barriers": [b for b, _ in barriers.most_common(4)],
                "uncertainties": [u for u, _ in uncs.most_common(4)],
                "workarounds": [w for w, _ in works.most_common(5)],
                "external_research": [],
                "supporting_evidence_ids": row.get("supporting_observations") or [],
                "counter_evidence_ids": row.get("counter_observations") or [],
                "confidence": row["confidence"],
                "confidence_score": {"high": 0.8, "medium": 0.6, "low": 0.35}[row["confidence"]],
                "research_gap": row["research_gap"],
                "what_we_know": row["reasoning"],
                "source_hypothesis": hid,
                "source_hypothesis_name": row["hypothesis_name"],
                "origin": "initial_hypothesis",
                "candidate_opportunity": True,
            }
        )
    return extra


def comparison_table(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "hypothesis_id": r["hypothesis_id"],
            "hypothesis_name": r["hypothesis_name"],
            "evidence": r["evidence_label"],
            "support": r["support_count"],
            "counter_evidence": r["counter_count"],
            "purchase_association": r["purchase_association"],
            "confidence": r["confidence"],
            "priority": r["priority"],
            "status": r["status"],
            "candidate_opportunity": r["candidate_opportunity"],
        }
        for r in sorted(results, key=lambda x: x["priority"])
    ]


def summary_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    c = Counter(r["status"] for r in results)
    return {
        "tested": len(results),
        "supported": c.get(STATUS_SUPPORTED, 0),
        "weakly_supported": c.get(STATUS_WEAKLY, 0),
        "contradicted": c.get(STATUS_CONTRADICTED, 0),
        "insufficient_evidence": c.get(STATUS_INSUFFICIENT, 0),
    }
