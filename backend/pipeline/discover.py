from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from backend.ai.heuristics import classify_relevance, extract_behavior
from backend.ai.llm import complete_json, llm_available
from config.taxonomies import OPPORTUNITY_WEIGHTS, NON_PURCHASE_OUTCOMES


def relevance_for(obs: dict[str, Any]) -> dict[str, Any]:
    text = obs.get("text_clean") or obs.get("text_original") or ""
    result = classify_relevance(text)
    if llm_available():
        payload = complete_json(
            system=(
                "You classify public shopping comments for a product-discovery study. "
                "Return JSON with relevant_to_discovery (bool), relevance_categories (array), "
                "relevance_rationale (string), confidence (0-1). "
                "Do NOT mark relevant only because the text mentions Myntra. "
                "Relevant means evidence of product consideration, wishlist/save, purchase "
                "decision, postponement, abandonment, fit/size/quality/price/info uncertainty, "
                "comparison, returns, or external research related to buying fashion."
            ),
            user=text[:4000],
            cache_key=f"rel:{obs['observation_id']}",
        )
        if payload and "relevant_to_discovery" in payload:
            result.update(
                {
                    "relevant_to_discovery": bool(payload.get("relevant_to_discovery")),
                    "relevance_categories": payload.get("relevance_categories") or result["relevance_categories"],
                    "relevance_rationale": payload.get("relevance_rationale") or result["relevance_rationale"],
                    "confidence": float(payload.get("confidence") or result["confidence"]),
                    "method": "llm",
                }
            )
    result["observation_id"] = obs["observation_id"]
    return result


def extraction_for(obs: dict[str, Any]) -> dict[str, Any]:
    text = obs.get("text_clean") or obs.get("text_original") or ""
    extracted = extract_behavior(text)
    if llm_available():
        payload = complete_json(
            system=(
                "Extract structured shopping behavior from the comment. "
                "Only use labels supported by the text. If unknown, say unknown/no evidence/unclear. "
                "Never invent wishlist behavior. Return JSON with keys: user_intent, "
                "wishlist_behavior, consider_reasons, purchase_outcome, barriers, "
                "uncertainty_present, uncertainty_type, uncertainty_description, "
                "workaround_present, workaround_type, workaround_description, "
                "external_research, external_research_platform, external_research_purpose, "
                "segment_signals, confidence."
            ),
            user=text[:4000],
            cache_key=f"ext:{obs['observation_id']}",
        )
        if payload and payload.get("user_intent"):
            extracted.update({k: payload[k] for k in payload if k in extracted})
            extracted["method"] = "llm"
    extracted["observation_id"] = obs["observation_id"]
    return extracted


def build_embeddings(texts: list[str]) -> tuple[np.ndarray, TfidfVectorizer, TruncatedSVD | None]:
    vectorizer = TfidfVectorizer(
        max_features=8000,
        ngram_range=(1, 2),
        min_df=2 if len(texts) > 40 else 1,
        stop_words="english",
    )
    matrix = vectorizer.fit_transform(texts)
    svd = None
    if matrix.shape[1] > 80 and matrix.shape[0] > 30:
        n_comp = min(80, matrix.shape[0] - 1, matrix.shape[1] - 1)
        svd = TruncatedSVD(n_components=n_comp, random_state=42)
        dense = svd.fit_transform(matrix)
    else:
        dense = matrix.toarray()
    return dense, vectorizer, svd


def cluster_embeddings(dense: np.ndarray, k: int) -> np.ndarray:
    n = dense.shape[0]
    k = max(2, min(k, max(2, n // 8), n))
    model = MiniBatchKMeans(n_clusters=k, random_state=42, n_init=10, batch_size=min(256, n))
    return model.fit_predict(dense)


def _top_n(counter: Counter, n: int = 5) -> list[str]:
    return [item for item, _ in counter.most_common(n) if item and item not in {"unknown", "unclear", "no evidence", "other"}]


def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def build_themes(
    relevant: list[dict[str, Any]],
    extractions: dict[str, dict[str, Any]],
    labels: list[int],
) -> list[dict[str, Any]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for idx, label in enumerate(labels):
        groups[int(label)].append(idx)

    themes: list[dict[str, Any]] = []
    n_relevant = max(len(relevant), 1)
    for cluster_id, indices in sorted(groups.items()):
        members = [relevant[i] for i in indices]
        ext_list = [extractions[m["observation_id"]] for m in members if m["observation_id"] in extractions]
        if len(members) < 3:
            continue
        barriers = Counter(b for e in ext_list for b in (e.get("barriers") or []))
        uncs = Counter(u for e in ext_list for u in (e.get("uncertainty_type") or []))
        works = Counter(w for e in ext_list for w in (e.get("workaround_type") or []))
        intents = Counter(e.get("user_intent") for e in ext_list)
        outcomes = Counter(e.get("purchase_outcome") for e in ext_list)
        segments = Counter(s for e in ext_list for s in (e.get("segment_signals") or []))
        sources = Counter(m.get("source") for m in members)
        platforms = Counter(p for e in ext_list for p in (e.get("external_research_platform") or []))

        top_barriers = _top_n(barriers, 4)
        top_unc = _top_n(uncs, 4)
        top_work = _top_n(works, 4)
        top_intent = _top_n(intents, 3)

        # Behavioral theme, not a keyword dump.
        barrier_clause = ", ".join(top_barriers) if top_barriers else "unspecified decision friction"
        intent_clause = ", ".join(top_intent) if top_intent else "mixed shopping intents"
        description = (
            f"Users describing {intent_clause} repeatedly surface {barrier_clause}. "
            "Some still complete a purchase; others postpone, abandon, or keep considering. "
            "This is an observed pattern in public comments, not a proven cause of 30-day wishlist conversion."
        )
        theme_name = _name_theme(top_barriers, top_unc, top_work, top_intent)
        if llm_available():
            sample = "\n".join((m.get("text_clean") or "")[:240] for m in members[:8])
            named = complete_json(
                system=(
                    "Name a behavioral theme for product discovery. "
                    "Return JSON {theme_name, description}. Theme name must be a sentence "
                    "about user behavior/unmet need, not a single keyword like Size."
                ),
                user=f"Barriers: {top_barriers}\nUncertainties: {top_unc}\nWorkarounds: {top_work}\nSamples:\n{sample}",
                cache_key=f"theme:{cluster_id}:{theme_name}",
            )
            if named and named.get("theme_name"):
                theme_name = named["theme_name"]
                description = named.get("description") or description

        supporting = [m["observation_id"] for m in members]
        dominant = top_barriers[0] if top_barriers else None
        counter_ids = _counter_evidence_ids(dominant, supporting, relevant, extractions)

        postponement = outcomes.get("postponed", 0)
        non_purchase = sum(outcomes.get(o, 0) for o in NON_PURCHASE_OUTCOMES)
        source_div = sorted({s for s in sources if s})
        freq_pct = round(100.0 * len(members) / n_relevant, 2)
        conf = min(
            0.35
            + 0.2 * min(len(source_div) / 3, 1)
            + 0.25 * min(len(members) / 80, 1)
            + 0.2 * (1 if top_barriers else 0),
            0.92,
        )
        qualified_segments = [s for s, c in segments.most_common(5) if c >= 8]
        research_gap = (
            f"Public comments mention '{barrier_clause}' in this cluster. "
            "We do not know whether it actually prevents 30-day wishlist conversion, "
            "for whom it is strongest, or whether it happens before or after saving an item."
        )
        what_we_know = (
            f"{len(members)} relevant observations ({freq_pct}%) grouped here. "
            f"Observed alongside postponed={outcomes.get('postponed', 0)}, "
            f"abandoned={outcomes.get('abandoned', 0)}, "
            f"purchased alternative={outcomes.get('purchased alternative', 0)}. "
            "These are co-occurrences, not causes."
        )
        themes.append(
            {
                "theme_id": f"theme-{cluster_id:02d}",
                "theme_name": theme_name,
                "description": description,
                "frequency": len(members),
                "frequency_percentage": freq_pct,
                "source_count": len(source_div),
                "source_diversity": source_div,
                "segments": qualified_segments,
                "segment_note": None if qualified_segments else "Insufficient evidence.",
                "purchase_outcomes": dict(outcomes),
                "barriers": top_barriers,
                "uncertainties": top_unc,
                "workarounds": top_work,
                "external_research": _top_n(platforms, 5),
                "supporting_evidence_ids": supporting[:40],
                "counter_evidence_ids": counter_ids,
                "confidence": _confidence_label(conf),
                "confidence_score": round(conf, 3),
                "research_gap": research_gap,
                "what_we_know": what_we_know,
                "cluster_id": cluster_id,
                "postponement_count": postponement,
                "non_purchase_count": non_purchase,
            }
        )
    themes.sort(key=lambda t: t["frequency"], reverse=True)
    return _unique_theme_names(themes)[:10]


def _unique_theme_names(themes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep cluster-level opportunities (5–10) but never show identical titles in the PM table.

    Names still start from the dominant barrier. When k-means splits one barrier into
    several clusters, the second barrier (or uncertainty) is appended so rows stay distinct.
    """
    counts = Counter(t["theme_name"] for t in themes)
    used: set[str] = set()
    for theme in themes:
        name = theme["theme_name"]
        if counts[name] == 1 and name not in used:
            used.add(name)
            continue
        extras = [b for b in (theme.get("barriers") or [])[1:] if b]
        extras.extend(
            u for u in (theme.get("uncertainties") or []) if u and u not in extras
        )
        lead = (theme.get("barriers") or [None])[0]
        extras = [
            e
            for e in extras
            if not lead
            or (e != lead and lead.replace(" uncertainty", "") not in e and e.replace(" uncertainty", "") not in lead)
        ]
        candidate = None
        for extra in extras:
            trial = f"{name} Also observed with {extra}."
            if trial not in used:
                candidate = trial
                break
        if candidate is None and len(extras) >= 2:
            trial = f"{name} Also observed with {extras[0]} and {extras[1]}."
            if trial not in used:
                candidate = trial
        if candidate is None:
            trial = f"{name} Pattern group {theme.get('cluster_id')}."
            n = 2
            candidate = trial
            while candidate in used:
                candidate = f"{trial} #{n}"
                n += 1
        theme["theme_name"] = candidate
        used.add(candidate)
    return themes


_COUNTER_PHRASES = {
    "fit": ("perfect fit", "fits well", "true to size", "size is accurate", "size chart was enough", "fit was fine"),
    "size": ("true to size", "size is accurate", "size chart was enough", "ordered my usual size and it worked"),
    "quality uncertainty": ("good quality", "as shown", "as expected", "as described", "worth the price"),
    "material/fabric uncertainty": ("fabric is good", "material as expected", "nice fabric"),
    "appearance uncertainty": ("looks like the photo", "same as pictures", "as shown in photos"),
    "reviews/trust": ("reviews helped", "reviews were enough", "trusted the reviews"),
    "price": ("worth the price", "reasonable price", "fair price", "bought it anyway"),
    "product information": ("details were enough", "size chart was enough", "information was clear"),
    "comparison": ("didn't need to compare", "this one was clearly better"),
    "return concern": ("easy return", "return was simple", "bought because returns are easy"),
}


def _counter_evidence_ids(
    dominant: str | None,
    supporting: list[str],
    relevant: list[dict[str, Any]],
    extractions: dict[str, dict[str, Any]],
) -> list[str]:
    if not dominant:
        return []
    phrases = _COUNTER_PHRASES.get(dominant, ())
    support_set = set(supporting)
    explicit: list[str] = []
    weak: list[str] = []
    for other in relevant:
        oid = other["observation_id"]
        if oid in support_set:
            continue
        text = (other.get("text_clean") or other.get("text_original") or "").lower()
        if any(p in text for p in phrases):
            explicit.append(oid)
            if len(explicit) >= 8:
                break
            continue
        ext = extractions.get(oid) or {}
        if ext.get("purchase_outcome") == "purchased" and dominant not in (ext.get("barriers") or []):
            weak.append(oid)
    return (explicit + weak)[:8]


def _name_theme(barriers: list[str], uncs: list[str], works: list[str], intents: list[str]) -> str:
    """Name from the cluster's *dominant* barrier only — do not skip to fit if it is merely present."""
    lead = barriers[0] if barriers else None
    names = {
        "fit": "Users remain uncertain about how a garment will fit, even when some size information is available.",
        "size": "Users cannot tell which size to order from the listing, so some wait or look for extra measurements.",
        "quality uncertainty": "Users cannot tell from the listing whether quality will match the price they would pay.",
        "material/fabric uncertainty": "Users cannot tell how a product will feel or drape from listing information alone.",
        "appearance uncertainty": "Users distrust product photos versus how the item will look in real life.",
        "reviews/trust": "Users question whether reviews and ratings are enough to convert a shortlist into a purchase.",
        "price": "Price and value-for-money concerns appear alongside hesitation after a product is already of interest.",
        "timing": "Users treat saved items as a wait-for-later list rather than an immediate purchase queue.",
        "comparison": "Users keep multiple options in play and delay buying while they compare products or platforms.",
        "competing product": "Users buy elsewhere after considering an item, rather than converting the original shortlist.",
        "return concern": "Return and exchange friction shows up in the decision, not only after a package arrives.",
        "product information": "Listing information is described as too thin to decide, so users look for proof elsewhere.",
        "availability": "Saved or considered items going out of stock is observed alongside missed purchases.",
        "delivery": "Delivery reliability is mentioned in the same comments as buying hesitation.",
        "occasion": "Occasion timing is used to justify saving now and deciding later.",
        "decision overload": "Too many similar options after shortlisting is observed alongside postponed or abandoned purchases.",
        "external research": "Users leave the shopping app to gather proof before they are willing to buy.",
        "lack of urgency": "Users describe no need to buy now, so saved items sit without converting.",
    }
    if lead and lead in names:
        return names[lead]
    if works:
        return "Users leave the listing to reduce uncertainty before they will buy."
    return (
        "A recurring decision-friction pattern is present, but no single barrier dominates; "
        "primary research is required before naming one problem."
    )


def _score_1_to_5_pct(pct: float, bands: tuple[float, float, float, float]) -> int:
    a, b, c, d = bands
    if pct >= d:
        return 5
    if pct >= c:
        return 4
    if pct >= b:
        return 3
    if pct >= a:
        return 2
    return 1


def score_opportunities(themes: list[dict[str, Any]], n_relevant: int) -> list[dict[str, Any]]:
    n_relevant = max(n_relevant, 1)
    opportunities: list[dict[str, Any]] = []
    for theme in themes:
        n = int(theme.get("frequency") or 0)
        if n <= 0:
            continue
        freq_pct = round(100.0 * n / n_relevant, 2)
        theme["frequency_percentage"] = freq_pct
        outcomes = theme.get("purchase_outcomes") or {}
        total_out = max(sum(outcomes.values()), 1)
        postponement = 100.0 * outcomes.get("postponed", 0) / total_out
        abandonment = 100.0 * outcomes.get("abandoned", 0) / total_out
        alt = 100.0 * outcomes.get("purchased alternative", 0) / total_out
        purchase_assoc = postponement + abandonment + alt

        supporting = len(theme.get("supporting_evidence_ids") or [])
        counter = len(theme.get("counter_evidence_ids") or [])
        n_sources = len(theme.get("source_diversity") or [])
        evidence = 1
        if supporting >= 15:
            evidence += 1
        if supporting >= 40:
            evidence += 1
        if n_sources >= 2:
            evidence += 1
        if counter > 0:
            evidence += 1
        evidence = min(5, evidence)

        freq_score = _score_1_to_5_pct(freq_pct, (6, 12, 20, 30))
        assoc_score = _score_1_to_5_pct(purchase_assoc, (8, 15, 25, 40))

        uncs = theme.get("uncertainties") or []
        severity = 4 if uncs else 2
        if theme.get("barriers"):
            severity = min(5, severity + 1)

        n_work = len(theme.get("workarounds") or [])
        workaround = min(5, 1 + n_work)
        if theme.get("external_research"):
            workaround = min(5, workaround + 1)

        segments = theme.get("segments") or []
        if not segments:
            segment_score = 1
            segment_label = ["Insufficient evidence."]
        else:
            segment_score = min(5, 2 + len(segments))
            segment_label = segments[:3]

        scores = {
            "evidence_strength": evidence,
            "frequency": freq_score,
            "purchase_association": assoc_score,
            "user_severity": severity,
            "workaround_intensity": workaround,
            "segment_relevance": segment_score,
        }
        composite = round(sum(scores[k] * OPPORTUNITY_WEIGHTS[k] for k in OPPORTUNITY_WEIGHTS), 2)
        opportunities.append(
            {
                "opportunity_id": theme["theme_id"].replace("theme", "opp"),
                "rank": 0,
                "title": theme["theme_name"],
                "description": theme["description"],
                "theme_ids": [theme["theme_id"]],
                "frequency": theme["frequency"],
                "frequency_percentage": theme["frequency_percentage"],
                "purchase_association": round(purchase_assoc, 2),
                "postponement_association": round(postponement, 2),
                "abandonment_association": round(abandonment, 2),
                "alternative_purchase_association": round(alt, 2),
                "user_segment": segment_label,
                "evidence_strength": evidence,
                "confidence": theme["confidence"],
                "confidence_score": theme["confidence_score"],
                "existing_workaround": theme.get("workarounds") or [],
                "research_gap": theme.get("research_gap"),
                "what_we_know": theme.get("what_we_know"),
                "scores": scores,
                "composite_score": composite,
                "supporting_evidence_ids": theme.get("supporting_evidence_ids") or [],
                "counter_evidence_ids": theme.get("counter_evidence_ids") or [],
                "why_ranked_higher": "",
                "scoring_notes": (
                    "Each dimension is scored 1–5. Composite is a weighted average "
                    "(purchase association 25%, evidence 20%, frequency / severity / workaround 15% each, "
                    "segment 10%). Purchase association is co-occurrence with postponed / abandoned / "
                    "purchased-alternative language — not causation."
                ),
            }
        )
    opportunities.sort(key=lambda o: o["composite_score"], reverse=True)
    for i, opp in enumerate(opportunities, start=1):
        opp["rank"] = i
        if i < len(opportunities):
            nxt = opportunities[i]
            delta = opp["composite_score"] - nxt["composite_score"]
            diffs = sorted(
                ((k, opp["scores"][k] - nxt["scores"][k]) for k in OPPORTUNITY_WEIGHTS),
                key=lambda kv: kv[1] * OPPORTUNITY_WEIGHTS[kv[0]],
                reverse=True,
            )
            driver, dval = diffs[0]
            opp["why_ranked_higher"] = (
                f"Ranked #{i} vs #{i + 1} because the weighted score is {delta:.2f} higher (max 5). "
                f"Biggest gap: {driver.replace('_', ' ')} "
                f"({opp['scores'][driver]}/5 vs {nxt['scores'][driver]}/5)."
            )
            if dval == 0:
                opp["why_ranked_higher"] = (
                    f"Ranked #{i} vs #{i + 1} on a {delta:.2f} composite edge; "
                    "individual 1–5 scores are close, so treat the order as comparison, not a large gap."
                )
        else:
            opp["why_ranked_higher"] = "Lowest of the discovered opportunities on the six 1–5 scores."
    return opportunities
