from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


SEGMENT_DEFS = {
    "high-wishlist users": "Language that explicitly mentions wishlist or saved items.",
    "fit-conscious shoppers": "Language about fit or size as part of the decision.",
    "price-sensitive shoppers": "Language about price, value, discounts, or waiting for sales.",
    "research-heavy shoppers": "Language about looking things up, photos, measurements, or leaving the app.",
    "comparison-heavy shoppers": "Language about comparing products or platforms.",
    "occasion-driven shoppers": "Language about events, weddings, office, or timed need.",
    "brand-loyal shoppers": "Language about brand, authenticity, or originals.",
    "exploratory browsers": "Language about browsing, inspiration, or just looking.",
    "unclassified": "Relevant observations without a discovered behavioral segment signal.",
}


def discover_segments(
    relevant: list[dict[str, Any]],
    extractions: dict[str, dict[str, Any]],
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for obs in relevant:
        ext = extractions.get(obs["observation_id"]) or {}
        signals = ext.get("segment_signals") or []
        if not signals:
            buckets["unclassified"].append(obs["observation_id"])
        for signal in signals:
            buckets[signal].append(obs["observation_id"])

    n = max(len(relevant), 1)
    profiles: list[dict[str, Any]] = []
    for name, ids in buckets.items():
        if name != "unclassified" and len(ids) < 5:
            continue
        ext_list = [extractions[i] for i in ids if i in extractions]
        barriers = Counter(b for e in ext_list for b in (e.get("barriers") or []) if b not in {"unknown", "other"})
        uncs = Counter(u for e in ext_list for u in (e.get("uncertainty_type") or []))
        works = Counter(w for e in ext_list for w in (e.get("workaround_type") or []))
        plats = Counter(p for e in ext_list for p in (e.get("external_research_platform") or []))
        outcomes = Counter(e.get("purchase_outcome") for e in ext_list)
        theme_hits: Counter[str] = Counter()
        for opp in opportunities:
            overlap = set(opp.get("supporting_evidence_ids") or []) & set(ids)
            if overlap:
                theme_hits[opp["title"][:80]] += len(overlap)
        profiles.append(
            {
                "segment_id": name.lower().replace(" ", "-"),
                "name": name,
                "definition": SEGMENT_DEFS.get(name, "Discovered from extraction signals; not a demographic claim."),
                "observation_count": len(ids),
                "percentage": round(100.0 * len(ids) / n, 2),
                "major_barriers": [k for k, _ in barriers.most_common(5)],
                "major_uncertainties": [k for k, _ in uncs.most_common(5)],
                "workarounds": [k for k, _ in works.most_common(5)],
                "external_research": [k for k, _ in plats.most_common(5)],
                "purchase_outcomes": dict(outcomes),
                "dominant_opportunity_themes": [k for k, _ in theme_hits.most_common(3)],
                "evidence_ids": ids[:40],
                "discovered": True,
            }
        )
    profiles.sort(key=lambda p: p["observation_count"], reverse=True)
    return profiles
