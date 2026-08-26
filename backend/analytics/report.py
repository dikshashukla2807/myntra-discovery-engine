from __future__ import annotations

from collections import Counter
from typing import Any


def build_report(
    *,
    quality: dict[str, Any],
    overview: dict[str, Any],
    opportunities: list[dict[str, Any]],
    themes: list[dict[str, Any]],
    segments: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
    interview: dict[str, Any] | None,
    dataset_label: str,
) -> dict[str, Any]:
    top = opportunities[:5]
    return {
        "title": "Myntra Wishlist → Purchase Discovery Report",
        "dataset_label": dataset_label,
        "dataset_disclaimer": (
            "Public user-generated content collected from source platforms."
            if dataset_label == "public_source"
            else "Demo / Sample Data — not real user research. Do not present as findings."
        ),
        "executive_summary": {
            "business_metric": "Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it.",
            "constraint": "We cannot use monetary incentives to influence users.",
            "total_observations": quality.get("total_collected"),
            "relevant_observations": quality.get("relevant"),
            "sources": quality.get("source_distribution"),
            "top_opportunity_areas": [
                {"rank": o["rank"], "title": o["title"], "score": o["composite_score"], "claim_type": o["claim_type"]}
                for o in top
            ],
            "key_research_gaps": [g["research_gap"] for g in gaps[:5]],
            "what_this_does_not_answer": "What feature Myntra should build. That decision comes after primary research.",
        },
        "dataset": quality,
        "behavioral_findings": overview.get("behavioral") or {},
        "opportunity_landscape": [
            {
                "opportunity": o["title"],
                "frequency": o["frequency"],
                "purchase_association": o["purchase_association"],
                "user_segment": o["user_segment"],
                "evidence_strength": o["evidence_strength"],
                "confidence": o["confidence"],
                "existing_workaround": o["existing_workaround"],
                "research_gap": o["research_gap"],
            }
            for o in opportunities
        ],
        "detailed_opportunity_analysis": opportunities,
        "themes": themes,
        "segments": segments,
        "interview_plan": interview,
        "methodology": {
            "scoring_weights": {
                "evidence_strength": 0.12,
                "frequency": 0.10,
                "purchase_association": 0.18,
                "user_severity": 0.10,
                "segment_concentration": 0.08,
                "source_diversity": 0.08,
                "workaround_intensity": 0.12,
                "potential_user_value": 0.08,
                "potential_business_relevance": 0.08,
                "product_solvability": 0.06,
            },
            "language": "Associations are described as observed alongside / potential contributor, not as causes.",
            "authenticity": "Original text is preserved. AI may classify and cluster but never replaces evidence.",
        },
    }


def html_report(report: dict[str, Any]) -> str:
    summary = report["executive_summary"]
    rows = "".join(
        f"<tr><td>{i+1}</td><td>{o['opportunity']}</td><td>{o['frequency']}</td>"
        f"<td>{o['purchase_association']}</td><td>{o['evidence_strength']}</td>"
        f"<td>{o['confidence']}</td><td>{o['research_gap']}</td></tr>"
        for i, o in enumerate(report["opportunity_landscape"][:12])
    )
    disclaimer = report["dataset_disclaimer"]
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{report['title']}</title>
<style>
body {{ font-family: Inter, system-ui, sans-serif; max-width: 960px; margin: 40px auto; color: #1a1a1a; }}
.banner {{ padding: 10px 14px; background: #f4efe6; border: 1px solid #d9cbb3; margin-bottom: 24px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
td, th {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
h1 {{ font-size: 28px; }}
</style></head>
<body>
<p class="banner"><strong>Dataset:</strong> {disclaimer}</p>
<h1>{report['title']}</h1>
<p><strong>Business metric:</strong> {summary['business_metric']}</p>
<p><strong>Constraint:</strong> {summary['constraint']}</p>
<p>Observations collected: {summary['total_observations']} · Relevant: {summary['relevant_observations']}</p>
<h2>Opportunity landscape</h2>
<table><thead><tr><th>#</th><th>Opportunity</th><th>Freq</th><th>Purchase assoc.</th><th>Evidence</th><th>Conf.</th><th>Research gap</th></tr></thead>
<tbody>{rows}</tbody></table>
<p><em>{summary['what_this_does_not_answer']}</em></p>
</body></html>"""
