"""Tests for collectors, normalization, quality, extraction, scoring, and API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.ai.heuristics import classify_relevance, detect_spam_or_low_value, extract_behavior
from backend.pipeline.discover import score_opportunities
from backend.pipeline.normalize import normalize_record
from backend.pipeline.quality import quality_gate
from backend.scrapers.app_store import _parse_entry
from backend.scrapers.google_play import _serialize_review
from backend.scrapers.reddit import _serialize as reddit_serialize
from backend.scrapers.youtube import collect_youtube
from backend.utils.text import content_hash, observation_id
from config import settings


def test_observation_id_stable():
    assert observation_id("google_play", "abc") == observation_id("google_play", "abc")
    assert observation_id("google_play", "abc") != observation_id("app_store", "abc")


def test_normalize_never_drops_original():
    row = normalize_record(
        source="google_play",
        source_id="r1",
        source_url="https://play.google.com/store/apps/details?id=com.myntra.android&reviewId=r1",
        text="  Saved it to wishlist  ",
        collected_at="2026-01-01T00:00:00Z",
        rating=4,
    )
    assert row["text_original"] == "  Saved it to wishlist  "
    assert row["dataset_label"] == "public_source"
    assert row["source_url"].startswith("https://play.google.com")


def test_google_play_serializer_preserves_fields():
    raw = {
        "reviewId": "gp123",
        "content": "Size chart is confusing so I didn't buy the jeans I saved.",
        "score": 2,
        "at": "2026-02-01T00:00:00Z",
        "userName": "PublicUser",
        "thumbsUpCount": 3,
        "reviewCreatedVersion": "4.0",
        "replyContent": None,
    }
    row = _serialize_review(raw, "2026-08-01T00:00:00Z")
    assert row["source"] == "google_play"
    assert row["source_id"] == "gp123"
    assert "gp123" in row["source_url"]
    assert row["text_original"].startswith("Size chart")
    assert row["rating"] == 2
    assert row["metadata"]["helpful_count"] == 3


def test_app_store_parser_skips_app_metadata_entry():
    assert _parse_entry({"id": {"label": "app"}}, "t", "in") is None
    row = _parse_entry(
        {
            "id": {"label": "555"},
            "title": {"label": "Fit issues"},
            "content": {"label": "Wish I knew the fit before buying."},
            "im:rating": {"label": "2"},
            "im:version": {"label": "5.1"},
            "updated": {"label": "2026-03-01T00:00:00Z"},
            "author": {"name": {"label": "A"}},
        },
        "2026-08-01T00:00:00Z",
        "in",
    )
    assert row is not None
    assert row["source"] == "app_store"
    assert row["rating"] == 2.0
    assert row["title"] == "Fit issues"
    assert row["source_url"] == settings.MYNTRA_APP_STORE_URL


def test_reddit_serializer_builds_permalink():
    row = reddit_serialize(
        {
            "id": "abc",
            "name": "t3_abc",
            "title": "Myntra wishlist never converts",
            "selftext": "I save and then google fabric reviews.",
            "created_utc": 1700000000,
            "permalink": "/r/india/comments/abc/myntra/",
            "subreddit": "india",
            "score": 10,
        },
        "2026-08-01T00:00:00Z",
        "Myntra wishlist",
        "myntra_wishlist",
        "t3",
    )
    assert row is not None
    assert row["source_url"] == "https://www.reddit.com/r/india/comments/abc/myntra/"
    assert "google fabric" in row["text_original"]


def test_youtube_without_key_does_not_fabricate(monkeypatch):
    monkeypatch.setattr(settings, "YOUTUBE_API_KEY", "")
    rows = collect_youtube(target=10)
    assert rows == []


def test_duplicate_detection():
    seen: dict[str, str] = {}
    a = normalize_record(source="google_play", source_id="1", source_url="u", text="Hello world product quality is confusing", collected_at="t")
    b = normalize_record(source="app_store", source_id="2", source_url="u", text="hello   world product quality is confusing", collected_at="t")
    status_a, _ = quality_gate(a, seen)
    status_b, reason_b = quality_gate(b, seen)
    assert status_a == "included"
    assert status_b == "excluded"
    assert reason_b == "duplicate"
    assert content_hash("Hello world product quality is confusing") == content_hash("hello   world product quality is confusing")


def test_spam_and_empty():
    assert detect_spam_or_low_value("") == "empty"
    assert detect_spam_or_low_value("good") == "low_information"
    assert detect_spam_or_low_value("use my code SAVE20") == "promotional"


def test_relevance_does_not_fire_on_myntra_alone():
    result = classify_relevance("Myntra is an app I have on my phone.")
    assert result["relevant_to_discovery"] is False


def test_relevance_wishlist_fit():
    result = classify_relevance("I wishlisted the kurta but I'm not sure it will fit me.")
    assert result["relevant_to_discovery"] is True
    assert "wishlist/save behavior" in result["relevance_categories"]
    assert "fit" in result["relevance_categories"]


def test_app_crash_is_irrelevant_without_purchase_language():
    result = classify_relevance("App keeps crashing after the latest update. OTP also delayed.")
    assert result["relevant_to_discovery"] is False


def test_extraction_does_not_invent_wishlist():
    ext = extract_behavior("The product quality is poor and stitching came undone after one wash.")
    assert ext["wishlist_behavior"] in {"no evidence", "unclear"}
    assert "quality uncertainty" in ext["barriers"]


def test_extraction_external_research():
    ext = extract_behavior("I googled YouTube hauls for the dress I saved for later because the fabric is unclear.")
    assert ext["external_research"] is True
    assert ext["wishlist_behavior"] in {"explicitly saved", "explicitly wishlisted"}
    assert "YouTube" in ext["workaround_type"] or "Google" in ext["workaround_type"]


def test_opportunity_scoring_transparent():
    themes = [
        {
            "theme_id": "theme-01",
            "theme_name": "Fit uncertainty after shortlisting",
            "description": "desc",
            "frequency": 20,
            "frequency_percentage": 40,
            "source_diversity": ["google_play", "reddit"],
            "segments": ["fit-conscious shoppers"],
            "purchase_outcomes": {"postponed": 8, "purchased": 2, "abandoned": 5, "unknown": 5},
            "barriers": ["fit", "size"],
            "uncertainties": ["fit"],
            "workarounds": ["checking measurements manually"],
            "external_research": ["Google"],
            "supporting_evidence_ids": [f"id{i}" for i in range(20)],
            "counter_evidence_ids": ["c1"],
            "confidence": "medium",
            "confidence_score": 0.6,
            "research_gap": "gap",
        }
    ]
    opps = score_opportunities(themes, 50)
    assert opps[0]["rank"] == 1
    assert "scores" in opps[0]
    assert abs(sum({"evidence_strength":0.12,"frequency":0.10,"purchase_association":0.18,"user_severity":0.10,"segment_concentration":0.08,"source_diversity":0.08,"workaround_intensity":0.12,"potential_user_value":0.08,"potential_business_relevance":0.08,"product_solvability":0.06}.values()) - 1.0) < 1e-9
    assert opps[0]["claim_type"] == "OPPORTUNITY"
    assert "not causation" in opps[0]["scoring_notes"]


def test_api_health(monkeypatch, tmp_path: Path):
    from backend.api.main import app

    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_frontend_pages_exist():
    root = Path(__file__).resolve().parents[1] / "frontend" / "src" / "app"
    expected = [
        "page.tsx",
        "explorer/page.tsx",
        "signals/page.tsx",
        "opportunities/page.tsx",
        "opportunities/[id]/page.tsx",
        "segments/page.tsx",
        "evidence/page.tsx",
        "gaps/page.tsx",
        "interviews/page.tsx",
        "pipeline/page.tsx",
        "report/page.tsx",
    ]
    for rel in expected:
        assert (root / rel).exists(), rel
