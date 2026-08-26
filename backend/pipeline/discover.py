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
        # Counter-evidence: relevant observations not in this cluster that show
        # the opposite outcome or explicitly contradict the dominant barrier.
        counter_ids: list[str] = []
        dominant = top_barriers[0] if top_barriers else None
        if dominant:
            for other in relevant:
                if other["observation_id"] in supporting:
                    continue
                ext = extractions.get(other["observation_id"]) or {}
                outcome = ext.get("purchase_outcome")
                other_barriers = ext.get("barriers") or []
                if dominant not in other_barriers and outcome == "purchased":
                    counter_ids.append(other["observation_id"])
                if len(counter_ids) >= 12:
                    break

        postponement = outcomes.get("postponed", 0) + outcomes.get("still considering", 0)
        non_purchase = sum(outcomes.get(o, 0) for o in NON_PURCHASE_OUTCOMES)
        source_div = sorted({s for s in sources if s})
        freq_pct = round(100.0 * len(members) / n_relevant, 2)
        conf = min(
            0.35
            + 0.2 * min(len(source_div) / 4, 1)
            + 0.25 * min(len(members) / 80, 1)
            + 0.2 * (1 if top_barriers else 0),
            0.92,
        )
        research_gap = (
            f"We do not yet know whether '{barrier_clause}' actually causes 30-day "
            "wishlist non-conversion, for whom it is most severe, or whether it occurs "
            "before vs after saving an item."
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
                "segments": _top_n(segments, 5),
                "purchase_outcomes": dict(outcomes),
                "barriers": top_barriers,
                "uncertainties": top_unc,
                "workarounds": top_work,
                "external_research": _top_n(platforms, 5),
                "supporting_evidence_ids": supporting[:80],
                "counter_evidence_ids": counter_ids,
                "confidence": _confidence_label(conf),
                "confidence_score": round(conf, 3),
                "research_gap": research_gap,
                "potential_user_value": (
                    "Reducing this uncertainty could help users decide whether to buy, wait, or walk away — "
                    "the direction of the decision is not assumed."
                ),
                "potential_business_relevance": (
                    f"{non_purchase} of {len(members)} clustered observations are associated with "
                    "postponement, abandonment, alternative purchase, or still-considering language. "
                    "This is an association, not causation."
                ),
                "claim_type": "PATTERN",
                "cluster_id": cluster_id,
                "postponement_count": postponement,
                "non_purchase_count": non_purchase,
            }
        )
    themes.sort(key=lambda t: t["frequency"], reverse=True)
    return themes


def _name_theme(barriers: list[str], uncs: list[str], works: list[str], intents: list[str]) -> str:
    if "fit" in barriers or "size" in barriers or "fit" in uncs:
        return (
            "Users remain uncertain about how a garment will fit despite having some size information, "
            "and some seek extra measurements, photos, or reviews before buying."
        )
    if "quality uncertainty" in barriers or "material/fabric uncertainty" in barriers:
        return (
            "Users cannot tell from listing information how a product will look or feel in real life, "
            "so they delay buying or look for proof elsewhere."
        )
    if "appearance uncertainty" in barriers or "photo vs reality" in uncs:
        return (
            "Users distrust product photos versus real appearance, which is observed alongside postponement "
            "and returns language."
        )
    if "reviews/trust" in barriers:
        return (
            "Users question whether reviews and ratings can be trusted when deciding to convert a shortlist "
            "into a purchase."
        )
    if "price" in barriers and "timing" in barriers:
        return (
            "Users treat saved items as a wait-for-better-price list rather than an immediate purchase queue."
        )
    if "price" in barriers:
        return (
            "Price and value-for-money concerns appear alongside hesitation, even when users already "
            "expressed interest in a product."
        )
    if "comparison" in barriers or "competing product" in barriers:
        return (
            "Users keep multiple options in play and leave the original product unsold while they compare "
            "across products or platforms."
        )
    if "return concern" in barriers:
        return (
            "Return and exchange friction is described as part of the decision, not only as a post-purchase process."
        )
    if "external research" in barriers or works:
        return (
            "Users leave the shopping app to gather fit, quality, or social proof before they are willing to buy."
        )
    if "decision overload" in barriers:
        return (
            "Choice overload after shortlisting is observed alongside postponed or abandoned purchases."
        )
    if "availability" in barriers:
        return (
            "Saved items going out of stock or size unavailability is observed alongside missed purchases."
        )
    if "delivery" in barriers:
        return (
            "Delivery reliability concerns appear in the same comments that describe buying hesitation."
        )
    if "occasion" in barriers:
        return (
            "Occasion timing (events, weddings, seasons) is used to justify saving now and deciding later."
        )
    return (
        "A recurring decision-friction pattern is present, but the dominant barrier is mixed; "
        "primary research is required before naming a single problem."
    )


def score_opportunities(themes: list[dict[str, Any]], n_relevant: int) -> list[dict[str, Any]]:
    n_relevant = max(n_relevant, 1)
    opportunities: list[dict[str, Any]] = []
    for theme in themes:
        freq = 100.0 * theme["frequency"] / n_relevant
        outcomes = theme.get("purchase_outcomes") or {}
        total_out = max(sum(outcomes.values()), 1)
        postponement = 100.0 * outcomes.get("postponed", 0) / total_out
        abandonment = 100.0 * outcomes.get("abandoned", 0) / total_out
        alt = 100.0 * outcomes.get("purchased alternative", 0) / total_out
        still = 100.0 * outcomes.get("still considering", 0) / total_out
        purchase_assoc = postponement + abandonment + alt + still

        supporting = len(theme.get("supporting_evidence_ids") or [])
        counter = len(theme.get("counter_evidence_ids") or [])
        contradiction = counter / max(supporting + counter, 1)
        source_div = len(theme.get("source_diversity") or []) / 4.0
        evidence_strength = (
            40.0 * min(np.log1p(supporting) / np.log1p(50), 1.0)
            + 30.0 * source_div
            + 30.0 * (1 - contradiction)
        )
        user_severity = 100.0 if theme.get("uncertainties") else 55.0
        if theme.get("barriers"):
            user_severity = min(100.0, user_severity + 15)
        segments = theme.get("segments") or []
        # Concentration: fewer named segments with more of the mass → higher.
        segment_concentration = 100.0 if len(segments) <= 2 else max(40.0, 100.0 - 12 * (len(segments) - 2))
        workaround_intensity = 100.0 * min(len(theme.get("workarounds") or []) / 4.0, 1.0)
        if theme.get("external_research"):
            workaround_intensity = min(100.0, workaround_intensity + 15)
        user_value = min(100.0, 40 + workaround_intensity * 0.3 + user_severity * 0.3)
        business = min(100.0, purchase_assoc)
        # Solvability: information-seeking workarounds suggest a product (non-monetary) intervention
        # *might* exist. This is a hypothesis about solvability, not a feature recommendation.
        info_barriers = {
            "fit",
            "size",
            "quality uncertainty",
            "material/fabric uncertainty",
            "appearance uncertainty",
            "reviews/trust",
            "product information",
            "comparison",
        }
        if any(b in info_barriers for b in theme.get("barriers") or []):
            solvability = 78.0
        elif "price" in (theme.get("barriers") or []):
            # Price can still be an opportunity area to research; monetary incentives are forbidden
            # as a solution, which lowers *product* solvability without deleting the finding.
            solvability = 42.0
        else:
            solvability = 55.0

        scores = {
            "evidence_strength": round(float(evidence_strength), 2),
            "frequency": round(float(freq), 2),
            "purchase_association": round(float(purchase_assoc), 2),
            "user_severity": round(float(user_severity), 2),
            "segment_concentration": round(float(segment_concentration), 2),
            "source_diversity": round(float(source_div * 100), 2),
            "workaround_intensity": round(float(workaround_intensity), 2),
            "potential_user_value": round(float(user_value), 2),
            "potential_business_relevance": round(float(business), 2),
            "product_solvability": round(float(solvability), 2),
        }
        composite = sum(scores[k] * OPPORTUNITY_WEIGHTS[k] for k in OPPORTUNITY_WEIGHTS)
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
                "user_segment": segments,
                "evidence_strength": scores["evidence_strength"],
                "confidence": theme["confidence"],
                "confidence_score": theme["confidence_score"],
                "existing_workaround": theme.get("workarounds") or [],
                "research_gap": theme.get("research_gap"),
                "scores": scores,
                "composite_score": round(float(composite), 2),
                "supporting_evidence_ids": theme.get("supporting_evidence_ids") or [],
                "counter_evidence_ids": theme.get("counter_evidence_ids") or [],
                "claim_type": "OPPORTUNITY",
                "why_ranked_higher": "",
                "scoring_notes": (
                    "Composite score is a weighted sum of 10 documented dimensions (see scores). "
                    "Purchase association is co-occurrence with postponement/abandonment/"
                    "alternative/still-considering language, not causation. "
                    "Monetary incentives are out of scope for solutions even if price appears as a barrier."
                ),
            }
        )
    opportunities.sort(key=lambda o: o["composite_score"], reverse=True)
    for i, opp in enumerate(opportunities, start=1):
        opp["rank"] = i
        if i < len(opportunities):
            delta = opp["composite_score"] - opportunities[i]["composite_score"]
            top_driver = max(opp["scores"].items(), key=lambda kv: kv[1] * OPPORTUNITY_WEIGHTS[kv[0]])
            opp["why_ranked_higher"] = (
                f"Ranked #{i} vs #{i+1} because composite score is {delta:.1f} points higher. "
                f"Largest weighted driver on this opportunity: {top_driver[0].replace('_', ' ')} "
                f"({top_driver[1]:.1f}/100, weight {OPPORTUNITY_WEIGHTS[top_driver[0]]:.0%})."
            )
        else:
            opp["why_ranked_higher"] = "Lowest ranked of the discovered opportunities on the documented composite formula."
    return opportunities
